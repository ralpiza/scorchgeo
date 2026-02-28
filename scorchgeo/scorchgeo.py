"""Main module."""

import ipyleaflet
import geopandas as gpd


class Map(ipyleaflet.Map):
    def __init__(self, center=[0, 0], zoom=2, height="600px", basemap=None, **kwargs):
        """Initialize an interactive map using ipyleaflet.

        Args:
            center (list): Latitude and longitude coordinates for map center.
                Defaults to [0, 0].
            zoom (int): Initial zoom level. Defaults to 2.
            height (str): Height of the map in CSS units. Defaults to "600px".
            basemap (str, optional): Name of the basemap to add. Defaults to None.
            **kwargs: Additional keyword arguments to pass to ipyleaflet.Map.
        """
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.add_control(ipyleaflet.LayersControl())
        self.layout.height = height
        self.scroll_wheel_zoom = True

    def add_basemap(self, basemap="OpenTopoMap"):
        """Add a basemap tile layer to the map.

        Args:
            basemap (str, optional): Basemap name from ipyleaflet.basemaps.
                Defaults to "OpenTopoMap". Examples: "OpenStreetMap", "CartoDB Positron",
                "CartoDB Voyager", etc.
        """

    def add_basemap(self, basemap="OpenTopoMap"):

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
        gdf = None

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__
        elif isinstance(data, dict):
            # convert GeoJSON dict to GeoDataFrame so that we can
            # calculate bounds for zooming
            geojson = data
            try:
                # geopandas >=0.10 has from_features
                gdf = gpd.GeoDataFrame.from_features(geojson)
            except AttributeError:
                # fallback for older versions
                gdf = gpd.GeoDataFrame.from_features(geojson.get("features", []))
        layer = ipyleaflet.GeoJSON(data=geojson, hover_style=hover_style, **kwargs)
        self.add_layer(layer)

        if zoom_to_layer and gdf is not None:
            if gdf.crs is not None and gdf.crs.to_string() != "EPSG:4326":
                gdf = gdf.to_crs(epsg=4326)

            bounds = gdf.total_bounds
            self.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    def add_shp(self, data, **kwargs):
        """Add a shapefile to the map.

        Args:
            data (str): Path to the shapefile.
            **kwargs: Additional keyword arguments to pass to add_geojson.
        """
        import geopandas as gpd

        gdf = gpd.read_file(data)
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_gdf(self, gdf, **kwargs):
        """Add a GeoDataFrame to the map.

        Converts the GeoDataFrame to WGS84 (EPSG:4326) if necessary before adding to map.

        Args:
            gdf (geopandas.GeoDataFrame): The GeoDataFrame to add to the map.
            **kwargs: Additional keyword arguments to pass to add_geojson.
        """
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_vector(self, data, **kwargs):
        """Add vector data to the map.

        Args:
            data (str, geopandas.GeoDataFrame, or dict): Vector data as a file path,
                GeoDataFrame, or GeoJSON dictionary.
            **kwargs: Additional keyword arguments to pass to the appropriate add method.

        Raises:
            ValueError: If data is not a file path, GeoDataFrame, or GeoJSON dict.
        """
        import geopandas as gpd

        # allow callers to supply a custom hover_style
        hover_style = kwargs.pop("hover_style", None)
        if hover_style is None:
            hover_style = {"color": "yellow", "fillOpacity": 0.2}

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            self.add_gdf(gdf, hover_style=hover_style, **kwargs)
        elif isinstance(data, gpd.GeoDataFrame):
            self.add_gdf(data, hover_style=hover_style, **kwargs)
        elif isinstance(data, dict):
            self.add_geojson(data, hover_style=hover_style, **kwargs)
        else:
            raise ValueError("Invalid data type")

    def add_raster(self, filepath, **kwargs):

        from localtileserver import TileClient, get_leaflet_tile_layer

        client = TileClient(filepath)
        tile_layer = get_leaflet_tile_layer(client, **kwargs)

        self.add_layer(tile_layer)
        self.center = client.center()
        self.zoom = client.default_zoom

    def add_image(self, image, bounds=None, **kwargs):

        if bounds is None:
            bounds = [[-90, 180], [90, 180]]
        overlay = ipyleaflet.ImageOverlay(url=image, bounds=bounds, **kwargs)
        self.add(overlay)

    def add_video(self, video, bounds=None, opacity=1.0, **kwargs):

        if bounds is None:
            bounds = [[-90, 180], [90, 180]]
        overlay = ipyleaflet.VideoOverlay(
            url=video, bounds=bounds, opacity=opacity, **kwargs
        )
        self.add(overlay)

    def add_wms_layer(
        self, url, layers, format="image/png", transparent=True, **kwargs
    ):
        layer = ipyleaflet.WMSLayer(
            url=url, layers=layers, format=format, transparent=transparent, **kwargs
        )
        self.add(layer)
