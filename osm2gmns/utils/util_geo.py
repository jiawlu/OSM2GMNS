from osm2gmns.utils.util_coord import to_latlon, from_latlon
import osm2gmns.settings as og_settings
from shapely import geometry
import functools
import numpy as np
import math



def getLineFromNodes(node_list):
    if len(node_list) < 2: return None, None
    point_list = [node.geometry for node in node_list]
    line = geometry.LineString(point_list)
    point_list_xy = [node.geometry_xy for node in node_list]
    line_xy = geometry.LineString(point_list_xy)
    return line, line_xy


def getPolygonFromNodes(node_list):
    if len(node_list) < 3: return None, None
    point_list = [(node.geometry.x, node.geometry.y) for node in node_list]
    poly = geometry.Polygon(point_list)
    point_list_xy = [(node.geometry_xy.x, node.geometry_xy.y) for node in node_list]
    poly_xy = geometry.Polygon(point_list_xy)
    return poly, poly_xy


def getLineAngle(ib_line, ob_line, complete_line=True):
    # complete_line - True (False): use the last and first (second last) coords to calculate line direction
    # ob_line counter clockwise: 0 to 180; ob_line clockwise: 0 to -180

    if complete_line:
        angle_ib = math.atan2(ib_line.coords[-1][1] - ib_line.coords[0][1],
                              ib_line.coords[-1][0] - ib_line.coords[0][0])
        angle_ob = math.atan2(ob_line.coords[-1][1] - ob_line.coords[0][1],
                              ob_line.coords[-1][0] - ob_line.coords[0][0])
    else:
        angle_ib = math.atan2(ib_line.coords[-1][1] - ib_line.coords[-2][1],
                              ib_line.coords[-1][0] - ib_line.coords[-2][0])
        angle_ob = math.atan2(ob_line.coords[-1][1] - ob_line.coords[-2][1],
                              ob_line.coords[-1][0] - ob_line.coords[-2][0])

    angle = angle_ob - angle_ib
    if angle < -1 * math.pi:
        angle += 2 * math.pi
    if angle > math.pi:
        angle -= 2 * math.pi
    return angle


def offsetLine(line, distance):
    coords = list(line.coords)
    offset_coord_list_temp = []
    for i in range(len(coords) - 1):
        start_x, start_y = coords[i]
        end_x, end_y = coords[i+1]

        delta_x = end_x - start_x
        delta_y = end_y - start_y
        length = (delta_x ** 2 + delta_y ** 2) ** 0.5
        offset_x = delta_y / length * distance
        offset_y = -1 * delta_x / length * distance

        offset_coord_list_temp.append(((start_x + offset_x, start_y + offset_y), (end_x + offset_x, end_y + offset_y)))

    coords_offset = [offset_coord_list_temp[0][0]]
    for i in range(len(offset_coord_list_temp) - 1):
        uf = offset_coord_list_temp[i][0]
        ut = offset_coord_list_temp[i][1]
        df = offset_coord_list_temp[i + 1][0]
        dt = offset_coord_list_temp[i + 1][1]

        d_utdf = ((ut[0] - df[0]) ** 2 + ((ut[1] - df[1]) ** 2)) ** 0.5
        if d_utdf < 0.1:
            x, y = (ut[0] + df[0]) * 0.5, (ut[1] + df[1]) * 0.5
            coords_offset.append((x, y))
        else:
            A = [[ut[1] - uf[1], uf[0] - ut[0]], [dt[1] - df[1], df[0] - dt[0]]]
            b = [(ut[1] - uf[1]) * uf[0] - (ut[0] - uf[0]) * uf[1],
                 (dt[1] - df[1]) * df[0] - (dt[0] - df[0]) * df[1]]
            A_mat = np.mat(A)
            b_mat = np.mat(b).T
            solution = np.linalg.inv(A_mat) * b_mat
            x, y = solution[0, 0], solution[1, 0]

            d_mut = ((ut[0] - x) ** 2 + ((ut[1] - y) ** 2)) ** 0.5
            if d_mut > 200:
                x, y = (ut[0] + df[0]) * 0.5, (ut[1] + df[1]) * 0.5
            coords_offset.append((x, y))

    coords_offset.append(offset_coord_list_temp[-1][1])
    return geometry.LineString(coords_offset)


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

        if shape.geom_type.startswith('Multi'):
            parts = [self._transform(geom, func) for geom in shape.geoms]
            return construct(parts)

        if shape.geom_type == 'Point':
            return construct(list(map(func, shape.coords))[0])

        if shape.geom_type in ('Point', 'LineString'):
            return construct(map(func, shape.coords))

        if shape.geom_type == 'Polygon':
            exterior = map(func, shape.exterior.coords)
            rings = [map(func, ring.coords) for ring in shape.interiors]
            return construct(exterior, rings)


    def geo_from_latlon(self, shape):
        return self._transform(shape, self._from_latlon_)

    def geo_to_latlon(self, shape):
        return self._transform(shape, self._to_latlon_)
