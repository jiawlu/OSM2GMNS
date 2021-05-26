import math
from .settings import *
from.coordconvertor import to_latlon
from shapely import geometry


def getDistanceFromCoord(lon1, lat1, lon2, lat2):
    # return km
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371
    return c * r


def getLineFromRefNodes(ref_node_list):
    if len(ref_node_list) < 2: return None, None
    point_list = [node.geometry for node in ref_node_list]
    line = geometry.LineString(point_list)
    point_list_xy = [node.geometry_xy for node in ref_node_list]
    line_xy = geometry.LineString(point_list_xy)
    return line, line_xy


def getPolygonFromRefNodes(ref_node_list):
    if len(ref_node_list) < 3: return None, None
    point_list = [node.geometry for node in ref_node_list]
    poly = geometry.Polygon(point_list)
    point_list_xy = [node.geometry_xy for node in ref_node_list]
    poly_xy = geometry.Polygon(point_list_xy)
    return poly, poly_xy


def printlog(msg,log_level='info'):
    if not print_log: return

    logger = logging.getLogger()

    if log_level == 'debug':
        logger.debug(msg)
    elif log_level == 'info':
        logger.info(msg)
    elif log_level == 'warning':
        logger.warning(msg)
    elif log_level == 'error':
        logger.error(msg)
    elif log_level == 'critical':
        logger.critical(msg)


def linexy2lonlat(line_xy, central_lon, northern):
    coords = [to_latlon(*coord_xy, central_lon, northern) for coord_xy in list(line_xy.coords)]
    line = geometry.LineString(coords)
    return line