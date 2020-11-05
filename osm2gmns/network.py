# -*- coding:utf-8 -*-
# @author       Jiawei Lu (jiaweil9@asu.edu)
#               Xuesong Zhou (xzhou74@asu.edu)
# @time         2020/10/21 17:27
# @desc         [script description]


from .settings import *
from .readfile import *
from .simplification import *
from .complex_intersection import *
import re


def parseNodes(network, nodes, strict_mode):
    for osm_node in nodes:
        node = Node()
        node.osm_node_id = int(osm_node.attrib['id'])
        node.x_coord = float(osm_node.attrib['lon'])
        node.y_coord = float(osm_node.attrib['lat'])
        # node.node_no = network.number_of_nodes

        if strict_mode:
            if not ((network.minlon <= node.x_coord <= network.maxlon) and (network.minlat <= node.y_coord <= network.maxlat)):
                node.in_region = False

        for info in osm_node:
            if info.tag == 'tag':
                if info.attrib['k'] == 'highway':
                    node.node_type = info.attrib['v']

        network.node_set.add(node)
        network.osm_node_id_to_node_dict[node.osm_node_id] = node


def newLinkFromWay(way, direction, ref_node_list):
    link = Link()
    link.osm_way_id = way.osm_way_id
    link.name = way.name
    link.link_type = way.link_type
    link.free_speed = way.maxspeed

    if way.oneway:
        link.lanes_list = [way.lanes]
    else:
        if direction == 1:
            if way.forward_lanes != -1:
                link.lanes_list = [way.forward_lanes]
            elif way.lanes != -1:
                link.lanes_list = [math.ceil(way.lanes / 2)]
            else:
                link.lanes_list = [way.lanes]
        else:
            if way.backward_lanes != -1:
                link.lanes_list = [way.backward_lanes]
            elif way.lanes != -1:
                link.lanes_list = [math.ceil(way.lanes / 2)]
            else:
                link.lanes_list = [way.lanes]

    link.lanes = link.lanes_list[0]
    link.from_node = ref_node_list[0]
    link.to_node = ref_node_list[-1]
    link.from_node.outgoing_link_list.append(link)
    link.to_node.incoming_link_list.append(link)
    for ref_node in ref_node_list: link.geometry_point_list.append((ref_node.x_coord,ref_node.y_coord))
    link.getGeometryStr()
    link.calculateLength()

    return link



def createLinks(network, way_list):
    for way in way_list:
        if way.is_cycle:
            crossing_in_cycle = False
            for node in way.ref_node_list[1:-1]:
                if node.is_crossing:
                    crossing_in_cycle = True
                    break
            if not crossing_in_cycle: continue

        way.getNodeListForSegments()
        for segment_no in range(way.number_of_segments):
            m_segment_node_list = way.segment_node_list[segment_no]
            valid_flag = True
            for node in m_segment_node_list:
                if not node.in_region:
                    valid_flag = False
                    break
            if not valid_flag: continue

            link = newLinkFromWay(way, 1, m_segment_node_list)
            network.link_set.add(link)
            if not way.oneway:
                linkb = newLinkFromWay(way, -1, list(reversed(m_segment_node_list)))
                network.link_set.add(linkb)



def parseWays(network, ways):
    way_list = []

    for osm_way in ways:
        way = Way()
        way.osm_way_id = int(osm_way.attrib['id'])

        for info in osm_way:
            if info.tag == 'nd':
                ref_node_id = int(info.attrib['ref'])
                try:
                    way.ref_node_list.append(network.osm_node_id_to_node_dict[ref_node_id])
                except KeyError:
                    print(f'  warning: ref node {ref_node_id} in way {way.osm_way_id} is not defined')          # todo: exception
                    return
            elif info.tag == 'tag':
                if info.attrib['k'] == 'highway':
                    way.highway = info.attrib['v']
                elif info.attrib['k'] == 'lanes':
                    way.lanes = int(info.attrib['v'])
                elif info.attrib['k'] == 'lanes:forward':
                    way.forward_lanes = int(info.attrib['v'])
                elif info.attrib['k'] == 'lanes:backward':
                    way.backward_lanes = int(info.attrib['v'])
                elif info.attrib['k'] == 'name':
                    way.name = info.attrib['v']
                elif info.attrib['k'] == 'maxspeed':
                    way.maxspeed = re.findall(r'\d+\.?\d*', info.attrib['v'])[0]
                elif info.attrib['k'] == 'oneway':
                    oneway_flag = info.attrib['v']
                    if oneway_flag == 'no':
                        way.oneway = False
                    elif oneway_flag == 'yes':
                        way.oneway = True
                    else:
                        print(f'  warning: new oneway flag {oneway_flag} detected at way {way.osm_way_id}')

        if way.highway:
            try:
                way.link_type = osm_highway_type_dict[way.highway]
            except KeyError:
                continue

            if way.ref_node_list[0] is way.ref_node_list[-1]:
                way.is_cycle = True

            if way.oneway is None: way.oneway = default_oneway_flag_dict[way.link_type]
            way_list.append(way)


    used_node_set = set()
    for way in way_list:
        way.ref_node_list[0].is_crossing = True
        way.ref_node_list[-1].is_crossing = True
        for node in way.ref_node_list[1:-1]:
            if node in used_node_set:
                node.is_crossing = True
            else:
                used_node_set.add(node)

    createLinks(network, way_list)


# todo: strict mode
def parseOSM(network, nodes, ways, strict_mode):
    parseNodes(network, nodes, strict_mode)
    parseWays(network, ways)


def removeUseless(network):
    remove_node_set = set()
    for node in network.node_set:
        if not (node.is_crossing and node.in_region):
            remove_node_set.add(node)
    for node in remove_node_set:
        network.node_set.remove(node)



def removeIsolated(network):
    isolated_node_set = set()
    isolated_link_set = set()

    for node in network.node_set:
        if len(node.incoming_link_list) + len(node.outgoing_link_list) == 0:
            node.is_isolated = True
            isolated_node_set.add(node)

    node_group_set = set()
    for link in network.link_set:
        new_group = (link.from_node, link.to_node)
        accessible_group_set = set()
        for node_group in node_group_set:
            if (link.from_node in node_group) or (link.to_node in node_group):
                accessible_group_set.add(node_group)

        for node_group in accessible_group_set:
            new_group += node_group
            node_group_set.remove(node_group)
        new_group = tuple(set(new_group))
        node_group_set.add(new_group)

    # select the set with the maximum number of nodes
    max_number_of_nodes = 0
    max_group = None
    for node_group in node_group_set:
        if len(node_group) > max_number_of_nodes:
            max_number_of_nodes = len(node_group)
            max_group = node_group

    for node_group in node_group_set:
        if node_group != max_group:
            for node in node_group:
                node.is_isolated = True
                isolated_node_set.add(node)

    for link in network.link_set:
        if link.from_node.is_isolated or link.to_node.is_isolated:
            link.is_isolated = True
            isolated_link_set.add(link)

    for node in isolated_node_set: network.node_set.remove(node)
    for link in isolated_link_set: network.link_set.remove(link)


def assignNewID(network):
    number_of_nodes = 0
    number_of_links = 0

    for node in network.node_set:
        node.node_id = number_of_nodes
        network.node_id_to_node_dict[node.node_id] = node
        number_of_nodes += 1

    for link in network.link_set:
        link.link_id = number_of_links
        number_of_links += 1



def getNetFromOSMFile(osm_filename='map.osm', strict_mode=True, remove_isolated=True, simplify=True, int_buffer=default_int_buffer, bbox=None):
    """
    :param osm_filename:
    :param strict_mode:
    :param remove_isolated:
    :param simplify:
    :param int_buffer:
    :param bbox: [minlat, minlon, maxlat, maxlon]
    :return: a network instance
    """

    # build network
    bounds, nodes, ways = readXMLFile(osm_filename)
    network = Network()
    if bbox is None:
        network.minlat, network.minlon, network.maxlat, network.maxlon = bounds['minlat'], bounds['minlon'], bounds['maxlat'], bounds['maxlon']
    else:
        network.minlat, network.minlon, network.maxlat, network.maxlon = bbox
    parseOSM(network, nodes, ways, strict_mode)
    removeUseless(network)

    # remove isolated nodes and links
    if remove_isolated:
        removeIsolated(network)

    # merge adjacent links at two-degree nodes
    if simplify:
        simplifyNetwork(network)


    # identify complex intersections which contains multiple nodes
    identifyComplexIntersections(network,int_buffer)

    # assign new ids starting from 0 to nodes and links
    assignNewID(network)

    return network


def getNetFromCSV(folder=''):
    node_data, link_data = readCSVFile(folder)
    network = Network()

    for i in range(len(node_data)):
        node = Node()
        node.node_id = node_data.loc[i, 'node_id']
        node.osm_node_id = node_data.loc[i, 'osm_node_id']
        node_type = node_data.loc[i, 'node_type']
        if node_type == node_type: node.node_type = node_type
        node.x_coord = node_data.loc[i, 'x_coord']
        node.y_coord = node_data.loc[i, 'y_coord']
        network.node_set.add(node)

        network.node_id_to_node_dict[node.node_id] = node
        # network.osm_node_id_to_node_dict[node.osm_node_id] = node

    for i in range(len(link_data)):
        link = Link()
        link.name = link_data.loc[i, 'name']
        link.link_id = link_data.loc[i, 'link_id']
        link.osm_way_id = link_data.loc[i, 'osm_way_id']
        link.from_node = network.node_id_to_node_dict[link_data.loc[i, 'from_node_id']]
        link.to_node = network.node_id_to_node_dict[link_data.loc[i, 'to_node_id']]
        link.length = link_data.loc[i, 'length']
        link.lanes = link_data.loc[i, 'lanes']
        link.free_speed = link_data.loc[i, 'free_speed']
        link.link_type = link_data.loc[i, 'link_type_name']
        link.geometry_str = link_data.loc[i, 'geometry']

        network.link_set.add(link)

        link.from_node.outgoing_link_list.append(link)
        link.to_node.incoming_link_list.append(link)

    return network

