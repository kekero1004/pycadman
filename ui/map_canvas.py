# ui/map_canvas.py

from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import io

class MapCanvas(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.init_map()

    def init_map(self):
        m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)
        data = io.BytesIO()
        m.save(data, close_file=False)
        self.setHtml(data.getvalue().decode())

    def update_map_with_shapes(self, shapes):
        m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)
        for shape in shapes:
            geojson = shape.to_geojson()
            folium.GeoJson(geojson).add_to(m)
        data = io.BytesIO()
        m.save(data, close_file=False)
        self.setHtml(data.getvalue().decode())
