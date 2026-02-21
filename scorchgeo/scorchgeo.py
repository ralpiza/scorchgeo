"""Main module."""

import ipyleaflet

class Map(ipyleaflet.Map):
    def __init__(self, center=[0, 0], zoom=2, height="600px", **kwargs):
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.add_control(ipyleaflet.LayersControl())
        self.layout.height = height

    def add_basemap(self, basemap = "OpenTopoMap"):
        
        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add_layer(layer)