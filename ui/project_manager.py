# ui/project_manager.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class ProjectManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('프로젝트 관리')
        self.setGeometry(200, 200, 600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel('프로젝트 관리 기능은 여기서 구현됩니다.'))
        self.setLayout(layout)
