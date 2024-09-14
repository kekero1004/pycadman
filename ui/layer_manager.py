# ui/layer_manager.py

from PyQt5.QtWidgets import QWidget, QListWidget, QPushButton, QColorDialog, QComboBox, QVBoxLayout, QHBoxLayout, QLabel,QInputDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class LayerManager(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layer_list = QListWidget()
        self.layer_list.addItems(self.canvas.layers.keys())
        self.layer_list.currentItemChanged.connect(self.layer_selection_changed)

        self.hatch_combo = QComboBox()
        self.hatch_combo.addItems(['No Brush', 'Dense1', 'Dense2', 'Dense3'])
        self.hatch_combo.currentIndexChanged.connect(self.change_hatch)

        self.add_layer_button = QPushButton('레이어 추가')
        self.add_layer_button.clicked.connect(self.add_layer)

        self.delete_layer_button = QPushButton('레이어 삭제')
        self.delete_layer_button.clicked.connect(self.delete_layer)

        self.layout.addWidget(QLabel('레이어 목록'))
        self.layout.addWidget(self.layer_list)
        self.layout.addWidget(QLabel('해칭 패턴'))
        self.layout.addWidget(self.hatch_combo)
        self.layout.addWidget(self.add_layer_button)
        self.layout.addWidget(self.delete_layer_button)
        self.setLayout(self.layout)

    def layer_selection_changed(self, current, previous):
        layer_name = current.text()
        self.canvas.current_layer = layer_name
        hatch = self.canvas.layers[layer_name].get('hatch', Qt.NoBrush)
        index = [Qt.NoBrush, Qt.Dense1Pattern, Qt.Dense2Pattern, Qt.Dense3Pattern].index(hatch)
        self.hatch_combo.setCurrentIndex(index)

    def change_hatch(self, index):
        layer_name = self.layer_list.currentItem().text()
        hatch_patterns = [Qt.NoBrush, Qt.Dense1Pattern, Qt.Dense2Pattern, Qt.Dense3Pattern]
        self.canvas.layers[layer_name]['hatch'] = hatch_patterns[index]
        self.canvas.update()

    def add_layer(self):
        layer_name, ok = QInputDialog.getText(self, '레이어 추가', '레이어 이름:')
        if ok and layer_name:
            self.canvas.layers[layer_name] = {'color': Qt.black, 'shapes': [], 'hatch': Qt.NoBrush}
            self.layer_list.addItem(layer_name)

    def delete_layer(self):
        layer_name = self.layer_list.currentItem().text()
        if layer_name != 'Default':
            del self.canvas.layers[layer_name]
            self.layer_list.takeItem(self.layer_list.currentRow())
