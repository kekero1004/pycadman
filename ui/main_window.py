# ui/main_window.py

from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QToolBar, QStatusBar, QDockWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from ui.canvas import Canvas
from ui.properties_panel import PropertiesPanel
from ui.layer_manager import LayerManager
from ui.project_manager import ProjectManager
from ui.map_canvas import MapCanvas
from ui.three_d_viewer import ThreeDViewer
from network.cloud_sync import login
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('심플 CAD 소프트웨어 with BIM 기능')
        self.setGeometry(100, 100, 1200, 800)
        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)
        self.create_actions()
        self.create_menus()
        self.create_toolbars()
        self.create_statusbar()

        # DockWidget으로 패널 추가
        self.properties_panel = PropertiesPanel(self.canvas)
        self.properties_dock = QDockWidget("속성 패널", self)
        self.properties_dock.setWidget(self.properties_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)

        self.layer_manager = LayerManager(self.canvas)
        self.layer_dock = QDockWidget("레이어 관리자", self)
        self.layer_dock.setWidget(self.layer_manager)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.layer_dock)

        self.project_manager = ProjectManager()
        self.project_dock = QDockWidget("프로젝트 관리자", self)
        self.project_dock.setWidget(self.project_manager)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.project_dock)

        self.map_canvas = MapCanvas()
        self.map_dock = QDockWidget("지도 캔버스", self)
        self.map_dock.setWidget(self.map_canvas)
        self.addDockWidget(Qt.RightDockWidgetArea, self.map_dock)

    def create_actions(self):
        # 기존 액션 유지
        self.open_dxf_viewer_action = QAction('DXF 뷰어로 열기', self)
        self.open_dxf_viewer_action.triggered.connect(self.open_dxf_in_viewer)
        
        self.new_action = QAction(QIcon('icons/new.png'), '새로 만들기', self)
        self.new_action.triggered.connect(self.new_file)

        self.open_action = QAction(QIcon('icons/open.png'), '열기', self)
        self.open_action.triggered.connect(self.open_file)

        self.save_action = QAction(QIcon('icons/save.png'), '저장', self)
        self.save_action.triggered.connect(self.save_file)

        self.open_ifc_action = QAction('IFC 열기', self)
        self.open_ifc_action.triggered.connect(self.open_ifc_file)

        self.export_shp_action = QAction('Shapefile 내보내기', self)
        self.export_shp_action.triggered.connect(self.export_shapefile)

        self.parcel_analysis_action = QAction('파셀 분석', self)
        self.parcel_analysis_action.triggered.connect(self.perform_parcel_analysis)

        self.view_3d_action = QAction('3D 보기', self)
        self.view_3d_action.triggered.connect(self.open_3d_viewer)

    def create_menus(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('파일')
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.open_ifc_action)
        file_menu.addAction(self.export_shp_action)
        file_menu.addAction(self.open_dxf_viewer_action)

        analysis_menu = menubar.addMenu('분석')
        analysis_menu.addAction(self.parcel_analysis_action)

        view_menu = menubar.addMenu('보기')
        view_menu.addAction(self.view_3d_action)

    def open_dxf_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'DXF 파일 열기', '', 'DXF Files (*.dxf)')
        if fname:
            self.canvas.open_dxf(fname)
            # DXF 뷰어로도 표시
            self.cad_viewer = CADViewerWidget(dxf_file=fname)
            self.cad_viewer_dock = QDockWidget("DXF 뷰어", self)
            self.cad_viewer_dock.setWidget(self.cad_viewer)
            self.addDockWidget(Qt.RightDockWidgetArea, self.cad_viewer_dock)
            

    def open_dxf_in_viewer(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'DXF 파일 열기', '', 'DXF Files (*.dxf)')
        if fname:
            self.cad_viewer = CADViewerWidget(dxf_file=fname)
            self.cad_viewer_dock = QDockWidget("DXF 뷰어", self)
            self.cad_viewer_dock.setWidget(self.cad_viewer)
            self.addDockWidget(Qt.RightDockWidgetArea, self.cad_viewer_dock)


    def create_toolbars(self):
        self.toolbar = QToolBar('Toolbar')
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

        self.toolbar.addAction(self.new_action)
        self.toolbar.addAction(self.open_action)
        self.toolbar.addAction(self.save_action)
        # 기타 도구 추가...

    def create_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.canvas.position_changed.connect(self.update_statusbar)

    def update_statusbar(self, pos):
        self.statusbar.showMessage(f'좌표: ({pos.x():.2f}, {pos.y():.2f}) | 모드: {self.canvas.mode}')

    def new_file(self):
        self.canvas.new_file()

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, '파일 열기', '', 'DXF Files (*.dxf)')
        if fname:
            self.canvas.open_dxf(fname)

    def save_file(self):
        fname, _ = QFileDialog.getSaveFileName(self, '파일 저장', '', 'DXF Files (*.dxf)')
        if fname:
            self.canvas.save_dxf(fname)

    def open_ifc_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'IFC 파일 열기', '', 'IFC Files (*.ifc)')
        if fname:
            self.canvas.open_ifc(fname)

    def export_shapefile(self):
        fname, _ = QFileDialog.getSaveFileName(self, 'Shapefile 내보내기', '', 'Shapefile (*.shp)')
        if fname:
            self.canvas.export_to_shapefile(fname)

    def perform_parcel_analysis(self):
        self.canvas.perform_parcel_analysis()

    def open_3d_viewer(self):
        viewer = ThreeDViewer(self.canvas.shapes)
        viewer.show()
