import math
from .settings import *
from shapely import geometry

default_bounds = {'minlat':-90.0, 'minlon':-180.0, 'maxlat':90.0, 'maxlon':180.0}


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
    if len(ref_node_list) < 2: return None
    point_list = [node.geometry for node in ref_node_list]
    line = geometry.LineString(point_list)
    return line


def getPolygonFromRefNodes(ref_node_list):
    if len(ref_node_list) < 3: return None
    point_list = [node.geometry for node in ref_node_list]
    poly = geometry.Polygon(point_list)
    return poly


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


