# ui/three_d_viewer.py

import open3d as o3d
from PyQt5.QtWidgets import QMainWindow

class ThreeDViewer(QMainWindow):
    def __init__(self, shapes):
        super().__init__()
        self.setWindowTitle('3D 뷰어')
        self.shapes = shapes
        self.init_viewer()

    def init_viewer(self):
        geometries = []
        for shape in self.shapes:
            mesh = shape.to_mesh()
            if mesh:
                geometries.append(mesh)
        if geometries:
            o3d.visualization.draw_geometries(geometries)
