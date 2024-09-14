# models/shapes.py

from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QPainter
import math

class Shape:
    def __init__(self):
        self.attributes = {}
        self.object_data = {}

    def draw(self, painter):
        pass

    def update(self, pos):
        pass

    def add_to_dxf(self, msp, layer_name):
        pass

    def contains(self, pos):
        return False

    def rotate(self, angle, center_point=None):
        pass

    def to_geometry(self):
        pass

    def to_geojson(self):
        pass

class LineShape(Shape):
    def __init__(self, start_point, end_point=None):
        super().__init__()
        self.start_point = start_point
        self.end_point = end_point if end_point else start_point

    def update(self, pos):
        self.end_point = pos

    def draw(self, painter):
        painter.drawLine(self.start_point, self.end_point)

    def add_to_dxf(self, msp, layer_name):
        msp.add_line((self.start_point.x(), self.start_point.y(), 0),
                     (self.end_point.x(), self.end_point.y(), 0),
                     dxfattribs={'layer': layer_name})

    def contains(self, pos):
        threshold = 5 / 1.0  # 스케일 고려
        distance = self.point_to_line_distance(pos, self.start_point, self.end_point)
        return distance < threshold

    def point_to_line_distance(self, p, a, b):
        # 선분 AB와 점 P 사이의 거리 계산
        pa = p - a
        ba = b - a
        h = max(0, min(1, QPointF.dotProduct(pa, ba) / QPointF.dotProduct(ba, ba)))
        projection = a + ba * h
        return (p - projection).manhattanLength()

    def rotate(self, angle, center_point=None):
        if not center_point:
            center_point = self.get_center()
        self.start_point = self.rotate_point(self.start_point, center_point, angle)
        self.end_point = self.rotate_point(self.end_point, center_point, angle)

    def rotate_point(self, point, center, angle):
        dx = point.x() - center.x()
        dy = point.y() - center.y()
        radians = math.radians(angle)
        cos_theta = math.cos(radians)
        sin_theta = math.sin(radians)
        x = cos_theta * dx - sin_theta * dy + center.x()
        y = sin_theta * dx + cos_theta * dy + center.y()
        return QPointF(x, y)

    def get_center(self):
        x = (self.start_point.x() + self.end_point.x()) / 2
        y = (self.start_point.y() + self.end_point.y()) / 2
        return QPointF(x, y)

    def to_geometry(self):
        return {
            'type': 'LINESTRING',
            'coordinates': [
                (self.start_point.x(), self.start_point.y()),
                (self.end_point.x(), self.end_point.y())
            ]
        }

    def to_geojson(self):
        return {
            'type': 'Feature',
            'geometry': self.to_geometry(),
            'properties': self.attributes
        }

class CircleShape(Shape):
    def __init__(self, center_point, radius=0):
        super().__init__()
        self.center_point = center_point
        self.radius = radius

    def update(self, pos):
        dx = pos.x() - self.center_point.x()
        dy = pos.y() - self.center_point.y()
        self.radius = (dx**2 + dy**2) ** 0.5

    def draw(self, painter):
        rect = QRectF(self.center_point.x() - self.radius,
                      self.center_point.y() - self.radius,
                      self.radius * 2, self.radius * 2)
        painter.drawEllipse(rect)

    def add_to_dxf(self, msp, layer_name):
        msp.add_circle((self.center_point.x(), self.center_point.y(), 0),
                       self.radius,
                       dxfattribs={'layer': layer_name})

    def contains(self, pos):
        dx = pos.x() - self.center_point.x()
        dy = pos.y() - self.center_point.y()
        distance = (dx**2 + dy**2) ** 0.5
        return abs(distance - self.radius) < (5 / 1.0)  # 스케일 고려

    def rotate(self, angle, center_point=None):
        pass  # 원은 회전해도 동일하므로 처리 불필요

    def to_geometry(self):
        # GeoJSON에서 원은 지원되지 않으므로 근사 폴리곤으로 변환 필요
        return {
            'type': 'POINT',
            'coordinates': (self.center_point.x(), self.center_point.y())
        }

    def to_geojson(self):
        return {
            'type': 'Feature',
            'geometry': self.to_geometry(),
            'properties': self.attributes
        }

class RectangleShape(Shape):
    def __init__(self, start_point, end_point=None):
        super().__init__()
        self.start_point = start_point
        self.end_point = end_point if end_point else start_point

    def update(self, pos):
        self.end_point = pos

    def draw(self, painter):
        rect = QRectF(self.start_point, self.end_point)
        painter.drawRect(rect)

    def add_to_dxf(self, msp, layer_name):
        points = [
            (self.start_point.x(), self.start_point.y(), 0),
            (self.start_point.x(), self.end_point.y(), 0),
            (self.end_point.x(), self.end_point.y(), 0),
            (self.end_point.x(), self.start_point.y(), 0),
            (self.start_point.x(), self.start_point.y(), 0),
        ]
        msp.add_lwpolyline(points, close=True, dxfattribs={'layer': layer_name})

    def contains(self, pos):
        rect = QRectF(self.start_point, self.end_point)
        return rect.contains(pos)

    def rotate(self, angle, center_point=None):
        if not center_point:
            center_point = self.get_center()
        corners = [self.start_point, QPointF(self.start_point.x(), self.end_point.y()),
                   self.end_point, QPointF(self.end_point.x(), self.start_point.y())]
        rotated_corners = [self.rotate_point(corner, center_point, angle) for corner in corners]
        # 새로운 시작점과 끝점 설정
        xs = [pt.x() for pt in rotated_corners]
        ys = [pt.y() for pt in rotated_corners]
        self.start_point = QPointF(min(xs), min(ys))
        self.end_point = QPointF(max(xs), max(ys))

    def rotate_point(self, point, center, angle):
        dx = point.x() - center.x()
        dy = point.y() - center.y()
        radians = math.radians(angle)
        cos_theta = math.cos(radians)
        sin_theta = math.sin(radians)
        x = cos_theta * dx - sin_theta * dy + center.x()
        y = sin_theta * dx + cos_theta * dy + center.y()
        return QPointF(x, y)

    def get_center(self):
        x = (self.start_point.x() + self.end_point.x()) / 2
        y = (self.start_point.y() + self.end_point.y()) / 2
        return QPointF(x, y)

    def to_geometry(self):
        coordinates = [
            (self.start_point.x(), self.start_point.y()),
            (self.start_point.x(), self.end_point.y()),
            (self.end_point.x(), self.end_point.y()),
            (self.end_point.x(), self.start_point.y()),
            (self.start_point.x(), self.start_point.y()),
        ]
        return {
            'type': 'POLYGON',
            'coordinates': [coordinates]
        }

    def to_geojson(self):
        return {
            'type': 'Feature',
            'geometry': self.to_geometry(),
            'properties': self.attributes
        }
