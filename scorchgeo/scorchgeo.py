"""Main module."""

import ipyleaflet
import geopandas as gpd


class Map(ipyleaflet.Map):
    def __init__(self, center=[0, 0], zoom=2, height="600px", **kwargs):
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.add_control(ipyleaflet.LayersControl())
        self.layout.height = height
        self.scroll_wheel_zoom = True

    def add_basemap(self, basemap="OpenTopoMap"):
        """Add basemap to the map.

        Args:
            basemap (str, optional): Basemap name. Defaults to "OpenTopoMap".
        """

        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add_layer(layer)

    def add_geojson(
        self,
        data,
        zoom_to_layer=True,
        hover_style=None,
        **kwargs,
    ):
        """Add GeoJSON data to the map.

        Args:
            data (str or dict): Path to a GeoJSON file or a GeoJSON dictionary.
            zoom_to_layer (bool, optional): Whether to zoom to the bounds of the layer. Defaults to True.
            hover_style (dict, optional): Style applied on hover. Defaults to {"color": "yellow", "fillOpacity": 0.2}.
            **kwargs: Additional keyword arguments to pass to ipyleaflet.GeoJSON.

        Raises:
            FileNotFoundError: If the provided file path does not exist.
        """
        if hover_style is None:
            hover_style = {"color": "yellow", "fillOpacity": 0.2}
        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__
        elif isinstance(data, dict):
            geojson = data
        layer = ipyleaflet.GeoJSON(data=geojson, hover_style=hover_style, **kwargs)
        self.add_layer(layer)

        if zoom_to_layer:
            bounds = gdf.total_bounds
            self.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    def add_shp(self, data, layer_name=None, hover_style=None, **kwargs):
        """Add a shapefile to the map.

        Args:
            data (str or dict): Path to a shapefile or a GeoJSON dictionary.
            layer_name (str, optional): Name of the layer. Defaults to the filename if data is a path.
            hover_style (dict, optional): Style applied on hover. Defaults to {"color": "yellow", "fillOpacity": 0.2}.
            **kwargs: Additional keyword arguments to pass to ipyleaflet.GeoJSON.
        """
        if hover_style is None:
            hover_style = {"color": "yellow", "fillOpacity": 0.2}
        if layer_name is None:
            layer_name = data.split("/")[-1]
        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__
        elif isinstance(data, dict):
            geojson = data
        layer = ipyleaflet.GeoJSON(
            data=geojson, name=layer_name, hover_style=hover_style, **kwargs
        )
        self.add_layer(layer)

    def add_gdf(self, gdf, zoom_to_layer=True, **kwargs):
        """Add a GeoDataFrame to the map.

        Converts the GeoDataFrame to WGS84 (EPSG:4326) if necessary before adding to map.

        Args:
            gdf (geopandas.GeoDataFrame): A GeoDataFrame to add to the map.
            zoom_to_layer (bool, optional): Whether to zoom to the bounds of the layer. Defaults to True.
            **kwargs: Additional keyword arguments to pass to ipyleaflet.GeoJSON.

        Raises:
            TypeError: If the input is not a GeoDataFrame.
        """
        import geopandas as gpd

        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame.")

        # Ensure WGS84
        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs(epsg=4326)

            geojson = gdf.__geo_interface__
            layer = ipyleaflet.GeoJSON(data=geojson, **kwargs)
            self.add_layer(layer)

        if zoom_to_layer:
            bounds = gdf.total_bounds
            self.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    def add_vector(self, data, hover_style=None, zoom_to_layer=True, **kwargs):
        """Add vector data to the map from multiple supported formats.

        Accepts file paths (shapefiles, GeoJSON), GeoDataFrames, or GeoJSON dictionaries.

        Args:
            data (str, geopandas.GeoDataFrame, or dict): Vector data as a file path, GeoDataFrame, or GeoJSON dictionary.
            hover_style (dict, optional): Style applied on hover. Defaults to {"color": "yellow", "fillOpacity": 0.2}.
            zoom_to_layer (bool, optional): Whether to zoom to the bounds of the layer. Defaults to True.
            **kwargs: Additional keyword arguments to pass to ipyleaflet.GeoJSON.

        Raises:
            ValueError: If the data type is not supported (must be str, GeoDataFrame, or dict).
        """
        import geopandas as gpd

        if hover_style is None:
            hover_style = {"color": "yellow", "fillOpacity": 0.2}

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            self.add_gdf(
                gdf, hover_style=hover_style, zoom_to_layer=zoom_to_layer, **kwargs
            )
        elif isinstance(data, gpd.GeoDataFrame):
            self.add_gdf(
                data, hover_style=hover_style, zoom_to_layer=zoom_to_layer, **kwargs
            )
        elif isinstance(data, dict):
            self.add_geojson(
                data, hover_style=hover_style, zoom_to_layer=zoom_to_layer, **kwargs
            )
        else:
            raise ValueError(
                "Unsupported data type. Please provide a file path, GeoDataFrame, or GeoJSON dictionary."
            )
