import csv
import os
import osmium
from .classes import *
from shapely import geometry
import numpy as np
from .coordconvertor import from_latlon
import re


class NWRHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)

        self.strict_mode = True
        self.bounds = None
        self.POIs = False

        self.osm_node_dict = {}
        self.osm_node_id_list = []
        self.osm_node_coord_list = []

        self.osm_way_dict = {}
        self.relation_list = []

    def node(self, n):
        node = Node()
        node.osm_node_id = str(n.id)
        lon, lat = n.location.lon, n.location.lat
        node.geometry = geometry.Point((round(lon, lonlat_precision), round(lat, lonlat_precision)))

        if self.strict_mode:
            if not node.geometry.within(self.bounds):
                node.in_region = False

        self.osm_node_id_list.append(node.osm_node_id)
        self.osm_node_coord_list.append((lon, lat))

        node.osm_highway = n.tags.get('highway')
        if node.osm_highway is not None:
            if 'signal' in node.osm_highway: node.ctrl_type = 'signal'
        self.osm_node_dict[node.osm_node_id] = node
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
                printlog(f'new lanes type detected at way {way.osm_way_id}, {lane_info}', 'warning')
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
                        printlog(f'new maxspeed type detected at way {way.osm_way_id}, {maxspeed_info}', 'warning')

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
                printlog(f'new lane type detected at way {way.osm_way_id}, {oneway_info}', 'warning')

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
        if not self.POIs: return

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
                printlog(f'new member type at relation {relation.osm_relation_id}, {member_type}', 'warning')
            relation.member_type_list.append(member_type_lc)
            relation.member_role_list.append(member_role)

        self.relation_list.append(relation)
        del r


def _processNodes(net, h):
    coord_array = np.array(h.osm_node_coord_list)
    central_lon, central_lat = np.mean(coord_array, axis=0)
    net.central_lon, net.central_lat = float(central_lon), float(central_lat)
    net.northern = True if central_lat >= 0 else False

    xs, ys = from_latlon(coord_array[:, 0], coord_array[:, 1], central_lon)
    for node_no, node_id in enumerate(h.osm_node_id_list):
        node = h.osm_node_dict[node_id]
        node.geometry_xy = geometry.Point((round(xs[node_no], xy_precision), round(ys[node_no], xy_precision)))

    net.osm_node_dict = h.osm_node_dict


def _processWays(net, h):
    for osm_way_id, osm_way in h.osm_way_dict.items():
        try:
            osm_way.ref_node_list = [net.osm_node_dict[ref_node_id] for ref_node_id in osm_way.ref_node_id_list]
            net.osm_way_dict[osm_way_id] = osm_way
        except KeyError as e:
            print(f'  warning: ref node {e} in way {osm_way_id} is not defined, way {osm_way_id} will not be imported')


def _processRelations(net, h):
    for relation in h.relation_list:
        valid = True
        for member_no, member_id in enumerate(relation.member_id_list):
            member_type = relation.member_type_list[member_no]
            if member_type == 'n':
                try:
                    relation.member_list.append(net.osm_node_dict[member_id])
                except KeyError as e:
                    print(f'  warning: ref node {e} in relation {relation.osm_relation_id} is not defined, relation {relation.osm_relation_id} will not be imported')
                    valid = False
                    break
            elif member_type == 'w':
                try:
                    relation.member_list.append(net.osm_way_dict[member_id])
                except KeyError as e:
                    print(f'  warning: ref way {e} in relation {relation.osm_relation_id} is not defined, relation {relation.osm_relation_id} will not be imported')
                    valid = False
                    break
            else:
                pass

        if valid:
            net.osm_relation_list.append(relation)


def _getBounds(filename, bbox):
    if bbox is None:
        f = osmium.io.Reader(filename)
        header = f.header()
        box = header.box()
        bottom_left = box.bottom_left
        top_right = box.top_right
        try:
            minlat, minlon = bottom_left.lat, bottom_left.lon
            maxlat, maxlon = top_right.lat, top_right.lon
        except:
            minlat, minlon, maxlat, maxlon = default_bounds['minlat'], default_bounds['minlon'], default_bounds['maxlat'], default_bounds['maxlon']
    else:
        minlat, minlon, maxlat, maxlon = bbox

    bounds = geometry.Polygon([(minlon, maxlat), (maxlon, maxlat), (maxlon, minlat), (minlon, minlat)])
    return bounds


def readOSMFile(filename, POIs, strict_mode, bbox):
    net = Network()

    net.bounds = _getBounds(filename, bbox)

    h = NWRHandler()
    h.strict_mode = strict_mode
    h.bounds = net.bounds
    h.POIs = POIs
    h.apply_file(filename)

    _processNodes(net,h)
    _processWays(net,h)
    _processRelations(net, h)

    return net



def readCSVFile(folder, encoding):
    node_filepath = os.path.join(folder,'node.csv')
    link_filepath = os.path.join(folder,'link.csv')

    if encoding is None:
        nfin = open(node_filepath, 'r')
        lfin = open(link_filepath, 'r')
    else:
        nfin = open(node_filepath, 'r', encoding=encoding)
        lfin = open(link_filepath, 'r', encoding=encoding)

    reader = csv.DictReader(nfin)
    node_data = [line for line in reader]
    nfin.close()

    reader = csv.DictReader(lfin)
    link_data = [line for line in reader]
    lfin.close()

    return node_data, link_data

