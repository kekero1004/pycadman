# -*- coding: utf-8 -*-
import ezdxf
import sys
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.pyqt import PyQtBackend, CorrespondingDXFEntity, CorrespondingDXFParentStack
from ezdxf.addons.drawing.properties import is_dark_color
from ezdxf.addons.drawing.qtviewer import CADGraphicsViewWithOverlay
from ezdxf.lldxf.const import DXFStructureError
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui, QtPrintSupport
from PyQt5.QtGui import QIcon

class cadViewer(QWidget):
    def __init__(self, dxf_file=None):

        super().__init__()
        self.viewer = QtViewer()
        layout = QVBoxLayout()
        layout.addWidget(self.viewer)
        self.setLayout(layout)
        if dxf_file:
            self.load_dxf(dxf_file)


        self.setCentralWidget(self.view)
        #self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.files)
        #self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.savePdfs)
        #self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.layers)
        #self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.selectedInfo)
        #self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.logView)

        self.menuBar().addAction( '도면열기', self.selectFile )
        #self.menuBar().addAction( 'PDF로 저장', self.save_pdfs )
        #self.menuBar().addAction( 'PDF 씬 보기', self.show_pdf_scene )
        self.select_layout_menu = self.menuBar().addMenu('모형 또는 배치 선택')
        self.statusBar().addPermanentWidget(self.statusLabel)

        self.view.element_selected.connect(self.selectedInfo.set_elements)
        self.view.mouse_moved.connect(self.on_mouse_moved)
        self.layers.updated_signal.connect( lambda : self.draw_layout(self.current_layout) )
        self.files.clicked_signal.connect(self.change_drawing)

    def load_dxf(self, filename):
        doc = ezdxf.readfile(filename)
        self.viewer.set_document(doc)

    def change_drawing(self, path, scene):
        self.view.setScene(scene)
        self.view.fit_to_scene()
        self.setWindowTitle('도면 뷰어 - ' + str(path))

    def change_layout(self):
        layout_name = self.sender().text()
        self.draw_layout(layout_name)

    def draw_layout(self, layout_name):
        self.current_layout = layout_name
        self.view.begin_loading()
        new_scene = QtWidgets.QGraphicsScene()
        self.backend.set_scene(new_scene)
        layout = self.dxf.layout(layout_name)
        self.render_context.set_current_layout(layout)
        if self.layers.visible_names is not None:
            self.render_context.set_layers_state(self.layers.visible_names, state=True)
        try:
            frontend = MyFrontend(self.render_context, self.backend)
            frontend.log_view = self.logView
            frontend.draw_layout(layout)
        except DXFStructureError as e:
            self.logView.append('DXF 도면이 유효하지 않습니다.')
            self.logView.append(f'Abort rendering of layout "{layout_name}": {str(e)}')
        finally:
            self.backend.finalize()

        self.view.end_loading(new_scene)
        self.view.buffer_scene_rect()
        self.view.setScene(new_scene)
        self.view.fit_to_scene()

    def on_mouse_moved(self, mouse_pos: QtCore.QPointF):
        self.statusLabel.setText( f'mouse position: {mouse_pos.x():.4f}, {mouse_pos.y():.4f}\n' )

    def selectFile(self):
        Selectdxfpaths, filter = QtWidgets.QFileDialog.getOpenFileNames(None, '도면열기', '', 'CAD 파일 (*.dxf *.DXF)')
        self.open_files(Selectdxfpaths)
        
    def open_files(self, dxfpaths):
        #filenames, filter = QtWidgets.QFileDialog.getOpenFileNames(None, 'Open file', '', 'CAD files (*.dxf *.DXF)')
        filenames = dxfpaths

        if filenames == '':
            return

        for filename in filenames:
            self.dxf = ezdxf.readfile(filename)

            self.render_context = RenderContext(self.dxf)
            self.backend = PyQtBackend(use_text_cache=True, params=self.render_params)
            self.layers.visible_names = None
            self.current_layout = None

            self.select_layout_menu.clear()
            for layout_name in self.dxf.layout_names_in_taborder():
                action = self.select_layout_menu.addAction(layout_name)
                action.triggered.connect(self.change_layout)

            self.layers.populate_layer_list( self.render_context.layers.values() )
            self.draw_layout('Model')
            self.setWindowTitle('도면뷰어 - ' + filename)

            self.files.append(Path(filename), self.view.scene())

    def save_pdfs(self):
        print('start.....save_pdfs..........')
        scene0 = self.view.scene()
        datas = self.savePdfs.datas(self.savePdfs.model)
        datas2 = self.savePdfs.datas(self.savePdfs.model2)
        if not Path('outputs').exists():
            Path('outputs').mkdir()
        
        for path, scene in zip(self.files.paths, self.files.scenes):

            print_scene = self.savePdfs.create_scene(scene)
            self.view.setScene(print_scene)

            image_path = 'outputs/' + path.with_suffix('.pdf').name
            width, height = int(print_scene.width()), int(print_scene.height())
            page_size = QtGui.QPageSize(
                QtCore.QSizeF(width, height),
                QtGui.QPageSize.Unit.Millimeter
            )

            printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
            printer.setPageSize(page_size)
            printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
            printer.setOutputFileName(image_path)
            painter = QtGui.QPainter(printer)
            painter.translate( width*datas['translate']['x'], height*datas['translate']['y'] )
            painter.scale( datas['scale']['x'], datas['scale']['y'] )
            painter.rotate(datas2['rotate']['value'])
            self.view.scene().render(painter)
            painter.end()

        self.view.setScene(scene0)

    def show_pdf_scene(self):
        print('start....show_pdf_scene')
        indexes = self.files.view.selectedIndexes()
        if len(indexes) == 0:
            return
        scene = self.files.scenes[ indexes[0].row() ]
        pdf_scene = self.savePdfs.create_scene(scene)
        self.view.setScene(pdf_scene)

class SelectedInfo(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super(SelectedInfo, self).__init__(parent)
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setReadOnly(True)
        self.setWidget( QtWidgets.QWidget() )
        self.widget().setLayout( QtWidgets.QVBoxLayout() )
        self.widget().layout().addWidget(self.text)
        self.setWindowTitle('선택된 객체정보')

    def set_elements(self, elements, index):

        def _entity_attribs_string(dxf_entity, indent=''):
            text = ''
            for key, value in dxf_entity.dxf.all_existing_dxf_attribs().items():
                text += f'{indent}- {key}: {value}\n'
            return text

        if not elements:
            text = 'No element selected'
        else:
            text = f'Selected: {index + 1} / {len(elements)}    (click to cycle)\n'
            element = elements[index]
            dxf_entity = element.data(CorrespondingDXFEntity)
            if dxf_entity is None:
                text += 'No data'
            else:
                text += f'Selected Entity: {dxf_entity}\nLayer: {dxf_entity.dxf.layer}\n\nDXF Attributes:\n'
                text += _entity_attribs_string(dxf_entity)

                dxf_parent_stack = element.data(CorrespondingDXFParentStack)
                if dxf_parent_stack:
                    text += '\nParents:\n'
                    for entity in reversed(dxf_parent_stack):
                        text += f'- {entity}\n'
                        text += _entity_attribs_string(entity, indent='    ')

        self.text.setPlainText(text)

class Layers(QtWidgets.QDockWidget):
    updated_signal = QtCore.pyqtSignal(list)
    def __init__(self, parent=None):
        super(Layers, self).__init__(parent)

        self.visible_names = None

        self.model = QtGui.QStandardItemModel()
        self.view = QtWidgets.QListView()
        self.view.setModel(self.model)
        self.view.setStyleSheet( 'QListWidget {font-size: 12pt;} QCheckBox {font-size: 12pt; padding-left: 5px;}' )
        self.setWidget( QtWidgets.QWidget() )
        self.widget().setLayout( QtWidgets.QVBoxLayout() )
        self.widget().layout().addWidget(self.view)
        self.setWindowTitle('레이어창')

        self.model.dataChanged.connect(self.layers_updated)

    def populate_layer_list(self, layers):
        self.model.clear()
        for layer in layers:
            item = QtGui.QStandardItem(layer.layer)
            item.setData(layer)
            item.setCheckable(True)
            item.setCheckState( QtCore.Qt.Checked if layer.is_visible else QtCore.Qt.Unchecked )
            text_color = '#FFFFFF' if is_dark_color(layer.color, 0.4) else '#000000'
            item.setForeground( QtGui.QBrush(QtGui.QColor(text_color)) )
            item.setBackground( QtGui.QBrush(QtGui.QColor(layer.color)) )
            self.model.appendRow(item)

    def layers_updated(self):
        self.visible_names = []
        for row in range( self.model.rowCount() ):
            item = self.model.item(row, 0)
            if item.checkState() == QtCore.Qt.Checked:
                self.visible_names.append( item.text() )
        self.updated_signal.emit(self.visible_names)

class LogView(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super(LogView, self).__init__(parent)
        self.text = QtWidgets.QTextBrowser()
        self.setWidget( QtWidgets.QWidget() )
        self.widget().setLayout( QtWidgets.QVBoxLayout() )
        self.widget().layout().addWidget(self.text)
        self.setWindowTitle('로그')

    def append(self, text):
        self.text.append(text)

class Files(QtWidgets.QDockWidget):
    clicked_signal = QtCore.pyqtSignal( Path, QtWidgets.QGraphicsScene )
    def __init__(self, parent=None):
        super(Files, self).__init__(parent)
        self.paths = []
        self.scenes = []
        self.print_scenes = []
        self.model = QtGui.QStandardItemModel()
        self.view = QtWidgets.QTableView()
        self.view.setModel(self.model)
        self.setWidget( QtWidgets.QWidget() )
        self.widget().setLayout( QtWidgets.QVBoxLayout() )
        self.widget().layout().addWidget(self.view)
        self.setWindowTitle('도면리스트')

        self.model.setHorizontalHeaderLabels(['Name', 'Width', 'Height'])
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.clicked.connect(self.clicked)

    def clicked(self, index):
        row = index.row()
        self.clicked_signal.emit( self.paths[row], self.scenes[row] )

    def append(self, path, scene):
        self.paths.append(path)
        self.scenes.append(scene)

        self.model.appendRow([
            QtGui.QStandardItem(path.name),
            QtGui.QStandardItem( str( round(scene.width(),  3) ) ),
            QtGui.QStandardItem( str( round(scene.height(), 3) ) )
        ])

class SavePdfs(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super(SavePdfs, self).__init__(parent)
        self.model = QtGui.QStandardItemModel()
        self.view = QtWidgets.QTableView()
        self.view.setModel(self.model)
        self.view.horizontalHeader().setStretchLastSection(True)

        self.model2 = QtGui.QStandardItemModel()
        self.view2 = QtWidgets.QTableView()
        self.view2.setModel(self.model2)
        self.view2.horizontalHeader().setStretchLastSection(True)

        self.setWidget( QtWidgets.QWidget() )
        self.widget().setLayout( QtWidgets.QVBoxLayout() )
        self.widget().layout().addWidget(self.view)
        self.widget().layout().addWidget(self.view2)
        self.setWindowTitle('Save PDFs')

        self.model.setHorizontalHeaderLabels(['x', 'y'])
        self.model.setVerticalHeaderLabels(['translate', 'scale'])
        for row, row_data in enumerate([ [0.0, 46.65], [1.0, -1.0] ]):
            for column, data in enumerate(row_data):
                self.model.setData(self.model.index(row, column), data)

        self.model2.setHorizontalHeaderLabels(['value'])
        self.model2.setVerticalHeaderLabels(['rotate', 'thin line width', 'thick line width'])
        for row, data in enumerate([0.0, 0.4, 1.2]):
            self.model2.setData(self.model2.index(row, 0), data)

    def create_scene(self, scene):
        new_scene = QtWidgets.QGraphicsScene( scene.sceneRect() )
        brush = QtGui.QBrush( QtGui.QColor('#000000') )
        data2 = self.datas(self.model2)
        pen = QtGui.QPen( brush, 0 )
        thin_pen = QtGui.QPen( brush, data2['thin line width']['value'] )
        thick_pen = QtGui.QPen( brush, data2['thick line width']['value'] )

        for item in scene.items():

            dxf_entity = item.data(CorrespondingDXFEntity)
            dxf_parent_stack = item.data(CorrespondingDXFParentStack)
            copied = type(item)()

            if type(copied) is QtWidgets.QGraphicsPathItem:
                copied.setPath( item.path() )

            if type(copied) is QtWidgets.QGraphicsLineItem:
                copied.setLine( item.line() )

            if type(copied) is QtWidgets.QGraphicsPolygonItem:
                copied.setPolygon( item.polygon() )

            if type(copied) is ezdxf.addons.drawing.pyqt._Point:
                copied.pos = item.pos

            if type(copied) is ezdxf.addons.drawing.pyqt._CosmeticPath:
                copied.setPath( item.path() )

            if type(copied) is ezdxf.addons.drawing.pyqt._CosmeticPolygon:
                copied.setPolygon( item.polygon() )


            if type(dxf_entity) is ezdxf.entities.mtext.MText or type(dxf_entity) is ezdxf.entities.text.Text:
                copied.setBrush(brush)
                copied.setPen(pen)
            else:
                copied.setPen(thick_pen)

                if not dxf_parent_stack is None:
                    if ezdxf.entities.dimension.Dimension in [ type(p) for p in dxf_parent_stack ]:
                        copied.setPen(thin_pen)

                if type(dxf_entity) is ezdxf.entities.line.Line:
                    if dxf_entity.dxf.linetype == 'CENTER':
                        copied.setPen(thin_pen)

            new_scene.addItem(copied)

        return new_scene

    def datas(self, model):
        datas = {}
        for row in range( model.rowCount() ):
            row_data = {}
            row_key = model.verticalHeaderItem(row).text()
            for column in range( model.columnCount() ):
                column_key = model.horizontalHeaderItem(column).text()
                data = model.data( model.index(row, column) )
                row_data[column_key] = data
            datas[row_key] = row_data
        return datas

class MyFrontend(Frontend):
    log_view = None
    def log_message(self, message):
        self.log_view.append(message)

##if __name__ == '__main__':
##    app = QtWidgets.QApplication(sys.argv)
##    window = cadViewer()
##    window.show()
##    app.exec()