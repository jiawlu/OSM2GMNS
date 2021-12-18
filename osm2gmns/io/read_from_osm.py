from osm2gmns.osmnet.osmclasses import OSMNode, Way, Relation, OSMNetwork
from osm2gmns.utils.util_coord import from_latlon
from osm2gmns.utils.util_geo import GeoTransformer
from osm2gmns.utils.util import getLogger
import osm2gmns.settings as og_settings
from shapely import geometry
import numpy as np
import sys
import osmium
import re


class NWRHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)

        self.strict_mode = True
        self.bounds = None
        self.POI = False

        self.osm_node_dict = {}
        self.osm_node_id_list = []
        self.osm_node_coord_list = []

        self.osm_way_dict = {}
        self.relation_list = []

    def node(self, n):
        osm_node_id = str(n.id)
        lon, lat = n.location.lon, n.location.lat
        node_geometry = geometry.Point(lon, lat)
        in_region = False if self.strict_mode and (not node_geometry.within(self.bounds)) else True

        osm_node_name = n.tags.get('name')
        osm_highway = n.tags.get('highway')
        ctrl_type = 'signal' if (osm_highway is not None) and 'signal' in osm_highway else None

        node = OSMNode(osm_node_name, osm_node_id, node_geometry, in_region, osm_highway, ctrl_type)
        self.osm_node_dict[node.osm_node_id] = node

        self.osm_node_id_list.append(osm_node_id)
        self.osm_node_coord_list.append((lon, lat))
        del n

    def way(self, w):
        way = Way()
        way.osm_way_id = str(w.id)
        way.ref_node_id_list = [str(node.ref) for node in w.nodes]

        way.highway = w.tags.get('highway')
        way.railway = w.tags.get('railway')
        way.aeroway = w.tags.get('aeroway')

        lane_info = w.tags.get('lanes')
        if lane_info is not None:
            lanes = re.findall(r'\d+\.?\d*', lane_info)
            if len(lanes) > 0:
                way.lanes = int(float(lanes[0]))  # in case of decimals
            else:
                logger = getLogger()
                if logger: logger.warning(f'new lanes type detected at way {way.osm_way_id}, {lane_info}')
        lane_info = w.tags.get('lanes:forward')
        if lane_info is not None:
            try:
                way.forward_lanes = int(lane_info)
            except:
                pass
        lane_info = w.tags.get('lanes:backward')
        if lane_info is not None:
            try:
                way.backward_lanes = int(lane_info)
            except:
                pass

        way.turn_lanes = w.tags.get('turn:lanes')
        way.turn_lanes_forward = w.tags.get('turn:lanes:forward')
        way.turn_lanes_backward = w.tags.get('turn:lanes:backward')

        way.name = w.tags.get('name')

        maxspeed_info = w.tags.get('maxspeed')
        if maxspeed_info is not None:
            try:
                way.maxspeed = int(float(maxspeed_info))
            except ValueError:
                speeds = re.findall(r'\d+\.?\d* mph', maxspeed_info)
                if len(speeds) > 0:
                    way.maxspeed = int(float(speeds[0][:-4]) * 1.6)
                else:
                    speeds = re.findall(r'\d+\.?\d* km/h', maxspeed_info)
                    if len(speeds) > 0:
                        way.maxspeed = int(float(speeds[0][:-5]))
                    else:
                        logger = getLogger()
                        if logger: logger.warning(f'new maxspeed type detected at way {way.osm_way_id}, {maxspeed_info}')

        oneway_info = w.tags.get('oneway')
        if oneway_info is not None:
            if oneway_info == 'yes' or oneway_info == '1':
                way.oneway = True
            elif oneway_info == 'no' or oneway_info == '0':
                way.oneway = False
            elif oneway_info == '-1':
                way.oneway = True
                way.is_reversed = True
            elif oneway_info in ['reversible', 'alternating']:
                # todo: reversible, alternating: https://wiki.openstreetmap.org/wiki/Tag:oneway%3Dreversible
                way.oneway = False
            else:
                logger = getLogger()
                if logger: logger.warning(f'new lane type detected at way {way.osm_way_id}, {oneway_info}')

        way.junction = w.tags.get('junction')
        way.area = w.tags.get('area')
        way.motor_vehicle = w.tags.get('motor_vehicle')
        way.motorcar = w.tags.get('motorcar')
        way.service = w.tags.get('service')
        way.foot = w.tags.get('foot')
        way.bicycle = w.tags.get('bicycle')
        way.building = w.tags.get('building')
        way.amenity = w.tags.get('amenity')

        self.osm_way_dict[way.osm_way_id] = way
        del w


    def relation(self, r):
        if not self.POI: return

        relation = Relation()
        relation.osm_relation_id = str(r.id)

        relation.building = r.tags.get('building')
        relation.amenity = r.tags.get('amenity')
        if (relation.building is None) and (relation.amenity is None):
            return
        relation.name = r.tags.get('name')

        for member in r.members:
            member_id, member_type, member_role = member.ref, member.type, member.role
            member_id_str = str(member_id)
            member_type_lc = member_type.lower()
            if member_type_lc == 'n':
                relation.member_id_list.append(member_id_str)
            elif member_type_lc == 'w':
                relation.member_id_list.append(member_id_str)
            elif member_type_lc == 'r':
                pass
            else:
                logger = getLogger()
                if logger: logger.warning(f'new member type at relation {relation.osm_relation_id}, {member_type}')
            relation.member_type_list.append(member_type_lc)
            relation.member_role_list.append(member_role)

        self.relation_list.append(relation)
        del r


def _processNodes(net, h):
    coord_array = np.array(h.osm_node_coord_list)
    central_lon, central_lat = np.mean(coord_array, axis=0)
    central_lon, central_lat = float(central_lon), float(central_lat)
    northern = True if central_lat >= 0 else False

    xs, ys = from_latlon(coord_array[:, 0], coord_array[:, 1], central_lon)
    for node_no, node_id in enumerate(h.osm_node_id_list):
        node = h.osm_node_dict[node_id]
        node.geometry_xy = geometry.Point((xs[node_no], ys[node_no]))

    net.osm_node_dict = h.osm_node_dict
    net.GT = GeoTransformer(central_lon, central_lat, northern)


def _processWays(net, h):
    for osm_way_id, osm_way in h.osm_way_dict.items():
        try:
            osm_way.ref_node_list = [net.osm_node_dict[ref_node_id] for ref_node_id in osm_way.ref_node_id_list]
            net.osm_way_dict[osm_way_id] = osm_way
        except KeyError as e:
            print(f'WARNING: ref node {e} in way {osm_way_id} is not defined, way {osm_way_id} will not be imported')


def _processRelations(net, h):
    for relation in h.relation_list:
        valid = True
        for member_no, member_id in enumerate(relation.member_id_list):
            member_type = relation.member_type_list[member_no]
            if member_type == 'n':
                try:
                    relation.member_list.append(net.osm_node_dict[member_id])
                except KeyError as e:
                    print(f'WARNING: ref node {e} in relation {relation.osm_relation_id} is not defined, relation {relation.osm_relation_id} will not be imported')
                    valid = False
                    break
            elif member_type == 'w':
                try:
                    relation.member_list.append(net.osm_way_dict[member_id])
                except KeyError as e:
                    print(f'WARNING: ref way {e} in relation {relation.osm_relation_id} is not defined, relation {relation.osm_relation_id} will not be imported')
                    valid = False
                    break
            else:
                pass

        if valid:
            net.osm_relation_list.append(relation)


def _getBounds(filename, bbox):
    """
    Get network bounds from osm file or user given bbox

    Parameters
    ----------
    filename: str
        filename of the osm file
    bbox: tuple
        user given bound box

    Returns
    -------
    bounds: geometry.Polygon
        network boundary
    """

    try:
        f = osmium.io.Reader(filename)
    except:
        sys.exit(f'Error: filepath {filename} contains invalid characters. Please use english characters only')

    if bbox is None:
        header = f.header()
        box = header.box()
        bottom_left = box.bottom_left
        top_right = box.top_right
        try:
            minlat, minlon = bottom_left.lat, bottom_left.lon
            maxlat, maxlon = top_right.lat, top_right.lon
        except:
            minlat, minlon = og_settings.default_bounds['minlat'], og_settings.default_bounds['minlon']
            maxlat, maxlon = og_settings.default_bounds['maxlat'], og_settings.default_bounds['maxlon']
    else:
        minlat, minlon, maxlat, maxlon = bbox

    bounds = geometry.Polygon([(minlon, maxlat), (maxlon, maxlat), (maxlon, minlat), (minlon, minlat)])
    return bounds


def readOSMFile(filename, POI, strict_mode, bbox):
    """
    Get nodes, ways and relations from osm file

    Parameters
    ----------
    filename: str
        filename of the osm file
    POI: bool
        get POI information or not
    strict_mode: bool
        use strcit_mode or not.
    bbox: tuple
        user given network boundary

    Returns
    -------
    osmnet: OSMNetwork
        OSMNetwork from the osm file
    """

    if og_settings.verbose:
        print('  reading osm file')

    osmnet = OSMNetwork()

    osmnet.bounds = _getBounds(filename, bbox)

    h = NWRHandler()
    h.strict_mode = strict_mode
    h.bounds = osmnet.bounds
    h.POI = POI
    h.apply_file(filename)

    _processNodes(osmnet,h)
    _processWays(osmnet,h)
    _processRelations(osmnet, h)

    return osmnet





