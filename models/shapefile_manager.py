# models/shapefile_manager.py

import shapefile

class ShapefileManager:
    def __init__(self, filename):
        self.w = shapefile.Writer(filename)
        self.w.autoBalance = 1

    def create_fields(self, fields):
        for field in fields:
            self.w.field(*field)  # (name, fieldType, size, decimal)

    def add_record(self, geometry, attributes):
        if geometry['type'] == 'POINT':
            self.w.point(*geometry['coordinates'])
        elif geometry['type'] == 'LINESTRING':
            self.w.line([geometry['coordinates']])
        elif geometry['type'] == 'POLYGON':
            self.w.poly([geometry['coordinates'][0]])
        # 기타 지오메트리 타입 처리

        self.w.record(*attributes)

    def save(self):
        self.w.close()
