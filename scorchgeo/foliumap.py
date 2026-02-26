import folium
import folium.plugins
import os


class Map(folium.Map):
    def __init__(self, center=(0, 0), zoom=2, **kwargs):
        """Initialize a folium Map object.

        Args:
            center (tuple): Latitude and longitude coordinates for map center.
                Defaults to (0, 0).
            zoom (int): Initial zoom level. Defaults to 2.
            **kwargs: Additional keyword arguments to pass to folium.Map.
        """
        super().__init__(location=center, zoom_start=zoom, **kwargs)

    def add_layer_control(self):
        """Add a layer control widget to the map.

        Allows users to toggle visibility of different layers on the map.
        """
        folium.LayerControl().add_to(self)

    def add_basemap(self, basemap="OpenStreetMap"):
        """Add a basemap tile layer to the map.

        Args:
            basemap (str): The basemap name or URL. Defaults to "OpenStreetMap".
                Common options include "OpenStreetMap", "CartoDB positron",
                "CartoDB dark_matter", etc.
        """
        folium.TileLayer(tiles=basemap, name=basemap, control=True).add_to(self)

    def add_geojson(
        self,
        data,
        zoom_to_layer=True,
        hover_style=None,
        **kwargs,
    ):
        """Add GeoJSON data to the map.

        Loads GeoJSON data from a file path or dictionary, converts it to EPSG:4326
        if necessary, and adds it as a layer to the map with optional hover styling.

        Args:
            data (str or dict): Path to a GeoJSON file or a GeoJSON dictionary.
            zoom_to_layer (bool, optional): If True, fit the map bounds to the layer.
                Defaults to True.
            hover_style (dict, optional): CSS-style dictionary for hover effects.
                Defaults to {"color": "yellow", "fillOpacity": 0.2}.
            **kwargs: Additional keyword arguments passed to folium.GeoJson.

        Raises:
            ValueError: If data is not a file path (str) or GeoJSON dictionary (dict).

        Returns:
            None
        """
        import geopandas as gpd

        if hover_style is None:
            hover_style = {"color": "yellow", "fillOpacity": 0.2}

        gdf = None

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__

        elif isinstance(data, dict):
            gdf = gpd.GeoDataFrame.from_features(data["features"])
            geojson = data
            try:
                gdf = gpd.GeoDataFrame.from_features(geojson)
            except AttributeError:
                gdf = gpd.GeoDataFrame.from_features(geojson.get("features", []))
        else:
            raise ValueError("Data must be a file path or GeoJSON dictionary.")

        if gdf.crs is not None and gdf.crs.to_string() != "EPSG:4326":
            gdf = gdf.to_crs(epsg=4326)

        layer = folium.GeoJson(
            geojson,
            highlight_function=lambda x: hover_style,
            **kwargs,
        )

        layer.add_to(self)

        if zoom_to_layer and gdf is not None:
            bounds = gdf.total_bounds  # minx, miny, maxx, maxy
            self.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    def add_shp(self, data, **kwargs):
        """Add a shapefile to the map.

        Args:
            data (str): Path to the shapefile.
            **kwargs: Additional keyword arguments to pass to folium.GeoJson.
        """
        import geopandas as gpd

        gdf = gpd.read_file(data)
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_gdf(self, gdf, **kwargs):
        """Add a GeoDataFrame to the map.

        Args:
            gdf (geopandas.GeoDataFrame): The GeoDataFrame to add to the map.
            **kwargs: Additional keyword arguments to pass to folium.GeoJson.
        """
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_vector(self, data, **kwargs):
        """Add vector data to the map.

        Args:
            data (str, geopandas.GeoDataFrame, or dict): Vector data as a file path,
                GeoDataFrame, or GeoJSON dictionary.
            **kwargs: Additional keyword arguments to pass to folium.GeoJson.

        Raises:
            ValueError: If data is not a file path, GeoDataFrame, or GeoJSON dict.
        """
        import geopandas as gpd

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            self.add_gdf(gdf, **kwargs)
        elif isinstance(data, gpd.GeoDataFrame):
            self.add_gdf(data, **kwargs)
        elif isinstance(data, dict):
            self.add_geojson(data, **kwargs)
        else:
            raise ValueError("Data must be a file path, GeoDataFrame, or GeoJSON dict.")
