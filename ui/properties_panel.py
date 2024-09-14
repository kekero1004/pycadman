# ui/properties_panel.py

from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QFormLayout
from PyQt5.QtCore import Qt

class PropertiesPanel(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.name_label = QLabel('이름:')
        self.name_edit = QLineEdit()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_edit)
        self.attribute_layout = QFormLayout()
        self.layout.addLayout(self.attribute_layout)
        self.setLayout(self.layout)

    def update_properties(self, shape):
        self.attribute_layout = QFormLayout()
        if shape:
            self.name_edit.setText(shape.__class__.__name__)
            for attr_name, attr_value in shape.attributes.items():
                line_edit = QLineEdit(str(attr_value))
                self.attribute_layout.addRow(QLabel(attr_name), line_edit)
                line_edit.textChanged.connect(lambda val, name=attr_name: self.update_attribute(name, val))
            self.layout.addLayout(self.attribute_layout)
        else:
            self.name_edit.clear()
