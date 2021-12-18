from osm2gmns.utils.util_coord import to_latlon, from_latlon
import osm2gmns.settings as og_settings
from shapely import geometry
import functools
import numpy as np



def getLineFromNodes(node_list):
    if len(node_list) < 2: return None, None
    point_list = [node.geometry for node in node_list]
    line = geometry.LineString(point_list)
    point_list_xy = [node.geometry_xy for node in node_list]
    line_xy = geometry.LineString(point_list_xy)
    return line, line_xy


def getPolygonFromNodes(node_list):
    if len(node_list) < 3: return None, None
    point_list = [node.geometry for node in node_list]
    poly = geometry.Polygon(point_list)
    point_list_xy = [node.geometry_xy for node in node_list]
    poly_xy = geometry.Polygon(point_list_xy)
    return poly, poly_xy


class GeoTransformer:
    def __init__(self, central_lon, central_lat, northern):
        self.central_lon = central_lon
        self.central_lat = central_lat
        self.northern = northern

        self.from_latlon = functools.partial(from_latlon, central_longitude=self.central_lon)
        self.to_latlon = functools.partial(to_latlon, central_longitude=self.central_lon, northern=self.northern)

    def _from_latlon_(self, p):
        return np.round(self.from_latlon(*p), og_settings.local_coord_precision)

    def _to_latlon_(self, p):
        return np.round(self.to_latlon(*p), og_settings.lonlat_coord_precision)

    def _transform(self, shape, func):
        construct = shape.__class__

        if shape.type.startswith('Multi'):
            parts = [self._transform(geom, func) for geom in shape.geoms]
            return construct(parts)

        if shape.type == 'Point':
            return construct(list(map(func, shape.coords))[0])

        if shape.type in ('Point', 'LineString'):
            return construct(map(func, shape.coords))

        if shape.type == 'Polygon':
            exterior = map(func, shape.exterior.coords)
            rings = [map(func, ring.coords) for ring in shape.interiors]
            return construct(exterior, rings)


    def geo_from_latlon(self, shape):
        return self._transform(shape, self._from_latlon_)

    def geo_to_latlon(self, shape):
        return self._transform(shape, self._to_latlon_)
