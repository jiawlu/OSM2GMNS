import os.path
import sys

from .readfile import *
from .combine_links import *
from .complex_intersection import *
from .wayfilters import *
from .pois import *
from .coordconvertor import from_latlon
from .check_args import _checkArgs_getNetFromFile
from shapely import wkt
import numpy as np


def _newLinkFromWay(link_id, way, direction, ref_node_list):
    link = Link()
    link.osm_way_id = way.osm_way_id
    link.link_id = link_id
    link.name = way.name
    link.link_class = way.link_class
    link.link_type_name = way.link_type_name
    link.link_type = way.link_type
    link.is_link = way.is_link
    link.free_speed = way.maxspeed
    link.allowed_uses = way.allowed_uses
    if not way.oneway: link.from_bidirectional_way = True

    if way.oneway:
        link.lanes_list = [way.lanes]
    else:
        if direction == 1:
            if way.forward_lanes is not None:
                link.lanes_list = [way.forward_lanes]
            elif way.lanes is not None:
                link.lanes_list = [math.ceil(way.lanes / 2)]
            else:
                link.lanes_list = [way.lanes]
        else:
            if way.backward_lanes is not None:
                link.lanes_list = [way.backward_lanes]
            elif way.lanes is not None:
                link.lanes_list = [math.ceil(way.lanes / 2)]
            else:
                link.lanes_list = [way.lanes]

    link.lanes = link.lanes_list[0]
    link.from_node = ref_node_list[0]
    link.to_node = ref_node_list[-1]
    link.from_node.outgoing_link_list.append(link)
    link.to_node.incoming_link_list.append(link)
    link.geometry, link.geometry_xy = getLineFromRefNodes(ref_node_list)
    link.calculateLength()
    return link


def _createNodeOnBoundary(node_in,node_outside,network):
    node = Node()
    node.node_id = network.max_node_id
    line = network.bounds.intersection(geometry.LineString([node_in.geometry,node_outside.geometry]))
    lon, lat = line.coords[1]
    node.geometry = geometry.Point((round(lon,lonlat_precision),round(lat,lonlat_precision)))
    x, y = from_latlon(lon, lat, network.central_lon)
    node.geometry_xy = geometry.Point((round(x,xy_precision),round(y,xy_precision)))
    node.is_crossing = True
    node.notes = 'boundary node created by osm2gmns'
    network.node_dict[node.node_id] = node
    network.max_node_id += 1
    return node


def _getSegmentNodeList(way, segment_no, network):
    m_segment_node_list = way.segment_node_list[segment_no]
    if way.is_reversed: m_segment_node_list = list(reversed(m_segment_node_list))
    number_of_nodes = len(m_segment_node_list)

    m_segment_node_list_group = []

    if m_segment_node_list[0].in_region:
        idx_first_outside = -1
        for idx, node in enumerate(m_segment_node_list):
            if not node.in_region:
                idx_first_outside = idx
                break

        if idx_first_outside == -1:
            m_segment_node_list_group.append(m_segment_node_list)
            return m_segment_node_list_group
        else:
            new_node = _createNodeOnBoundary(m_segment_node_list[idx_first_outside-1],m_segment_node_list[idx_first_outside], network)
            m_segment_node_list_group.append(m_segment_node_list[:idx_first_outside] + [new_node])

    if m_segment_node_list[-1].in_region:
        idx_last_outside = -1
        for idx in range(number_of_nodes-2,-1,-1):
            if not m_segment_node_list[idx].in_region:
                idx_last_outside = idx
                break
        new_node = _createNodeOnBoundary(m_segment_node_list[idx_last_outside+1],m_segment_node_list[idx_last_outside], network)
        m_segment_node_list_group.append([new_node] + m_segment_node_list[idx_last_outside+1:])

    return m_segment_node_list_group


def _createLinks(network, link_way_list):
    link_dict = {}
    max_link_id = network.max_link_id
    for way in link_way_list:
        if way.is_pure_cycle: continue
        way.getNodeListForSegments()
        for segment_no in range(way.number_of_segments):
            m_segment_node_list_group = _getSegmentNodeList(way, segment_no, network)
            for m_segment_node_list in m_segment_node_list_group:
                if len(m_segment_node_list) < 2: continue
                link = _newLinkFromWay(max_link_id, way, 1, m_segment_node_list)
                link_dict[link.link_id] = link
                max_link_id += 1
                if not way.oneway:
                    linkb = _newLinkFromWay(max_link_id, way, -1, list(reversed(m_segment_node_list)))
                    link_dict[linkb.link_id] = linkb
                    max_link_id += 1
    network.link_dict = link_dict
    network.max_link_id = max_link_id


def _identifyCrossingNodes(link_way_list):
    used_node_set = set()
    for way in link_way_list:
        way.ref_node_list[0].is_crossing = True
        way.ref_node_list[-1].is_crossing = True
        for node in way.ref_node_list[1:-1]:
            if node in used_node_set:
                node.is_crossing = True
            else:
                used_node_set.add(node)


def _identifyPureCycleWays(link_way_list):
    for way in link_way_list:
        if way.is_cycle:
            way.is_pure_cycle = True
            for node in way.ref_node_list[1:-1]:
                if node.is_crossing:
                    way.is_pure_cycle = False
                    break


def _getNetworkNodes(network):
    node_dict = {}
    max_node_id = network.max_node_id
    for osm_node_id, node in network.osm_node_dict.items():
        if node.is_crossing and node.in_region:
            node.node_id = max_node_id
            node_dict[node.node_id] = node
            max_node_id += 1
    network.node_dict = node_dict
    network.max_node_id = max_node_id


def _removeIsolated(network,min_nodes):
    node_list = []
    node_to_idx_dict = {}
    for idx, (node_id,node) in enumerate(network.node_dict.items()):
        node_list.append(node)
        node_to_idx_dict[node] = idx

    number_of_nodes = len(node_list)
    node_group_id_list = [-1] * number_of_nodes

    group_id = 0
    start_idx = 0

    while True:
        unprocessed_node_list = [node_list[start_idx]]
        node_group_id_list[start_idx] = group_id
        while unprocessed_node_list:
            node = unprocessed_node_list.pop()
            for ob_link in node.outgoing_link_list:
                ob_node = ob_link.to_node
                if node_group_id_list[node_to_idx_dict[ob_node]] == -1:
                    node_group_id_list[node_to_idx_dict[ob_node]] = group_id
                    unprocessed_node_list.append(ob_node)

            for ib_link in node.incoming_link_list:
                ib_node = ib_link.from_node
                if node_group_id_list[node_to_idx_dict[ib_node]] == -1:
                    node_group_id_list[node_to_idx_dict[ib_node]] = group_id
                    unprocessed_node_list.append(ib_node)

        unreachable_node_exits = False
        for idx in range(start_idx+1,number_of_nodes):
            if node_group_id_list[idx] == -1:
                unreachable_node_exits = True
                break

        if unreachable_node_exits:
            start_idx = idx
            group_id += 1
        else:
            break

    group_id_set = set(node_group_id_list)
    group_isolated_dict = {}
    for group_id in group_id_set:
        group_size = node_group_id_list.count(group_id)
        if group_size < min_nodes:
            group_isolated_dict[group_id] = True
        else:
            group_isolated_dict[group_id] = False

    removal_link_set = set()
    for idx, node in enumerate(node_list):
        if group_isolated_dict[node_group_id_list[idx]]:
            del network.node_dict[node.node_id]
            for ob_link in node.outgoing_link_list: removal_link_set.add(ob_link)
            for ib_link in node.incoming_link_list: removal_link_set.add(ib_link)
    for link in removal_link_set:
        del network.link_dict[link.link_id]


def _updateDefaultLSC(default_lanes, default_speed, default_capacity, network):
    if default_lanes:
        if isinstance(default_lanes,bool):
            network.default_lanes = default_lanes_dict
        elif isinstance(default_lanes,dict):
            network.default_lanes = default_lanes
            for link_type_name, lanes in default_lanes_dict.items():
                if link_type_name not in default_lanes.keys():
                    network.default_lanes[link_type_name] = lanes

    if default_speed:
        if isinstance(default_speed,bool):
            network.default_speed = default_speed_dict
        elif isinstance(default_speed,dict):
            network.default_speed = default_speed
            for link_type_name, speed in default_speed_dict.items():
                if link_type_name not in default_speed.keys():
                    network.default_speed[link_type_name] = speed

    if default_capacity:
        if isinstance(default_capacity,bool):
            network.default_capacity = default_capacity_dict
        elif isinstance(default_capacity,dict):
            network.default_capacity = default_capacity
            for link_type_name, capacity in default_capacity_dict.items():
                if link_type_name not in default_speed.keys():
                    network.default_capacity[link_type_name] = capacity


def _offsetLinks(network, offset):
    for link_id, link in network.link_dict.items():
        if link.from_bidirectional_way:
            # distance = max(link.lanes_list) / 2 * 3.5
            geometry_xy = link.geometry_xy.parallel_offset(distance=2, side=offset, join_style=2)
            if offset == 'right':
                link.geometry_xy = geometry.LineString(list(geometry_xy.coords)[::-1])
            elif offset == 'left':
                link.geometry_xy = geometry_xy

            link.geometry = linexy2lonlat(link.geometry_xy, network.central_lon, network.northern)


def _createNLPs(network, link_type, offset, network_type, POIs, POI_percentage):
    link_way_list = []
    POI_way_list = []
    network_type_set = set(network_type)
    include_railway = True if 'railway' in network_type_set else False
    include_aeroway = True if 'aeroway' in network_type_set else False

    for osm_way_id, way in network.osm_way_dict.items():
        if way.building or way.amenity:
            POI_way_list.append(way)
        elif way.highway:
            if way.highway in highway_poi_set:
                way.way_poi = way.highway
                POI_way_list.append(way)
                continue
            if way.area and way.area != 'no':
                continue
            if way.highway in negligible_highway_type_set:
                continue

            try:
                way.link_type_name, way.is_link = osm_highway_type_dict[way.highway]
                way.link_type = link_type_no_dict[way.link_type_name]
                if link_type != 'all' and way.link_type_name not in link_type:
                    continue
            except KeyError:
                printlog(f'new highway type at way {way.osm_way_id}, {way.highway}', 'warning')
                continue

            if len(way.ref_node_list) < 2: continue

            allowable_agent_type_list = getAllowableAgentType(way)
            way.allowable_agent_type_list = list(set(allowable_agent_type_list).intersection(network_type_set))
            if len(way.allowable_agent_type_list) == 0:
                continue
            way.allowed_uses = ';'.join(way.allowable_agent_type_list)

            if way.ref_node_list[0] is way.ref_node_list[-1]:
                way.is_cycle = True
            if way.oneway is None:
                way.oneway = default_oneway_flag_dict[way.link_type_name]
            if way.lanes is None:
                if network.default_lanes:
                    way.lanes = network.default_lanes[way.link_type_name]
            if way.maxspeed is None:
                if network.default_speed:
                    way.maxspeed = network.default_speed[way.link_type_name]
            way.link_class = 'highway'
            link_way_list.append(way)
            if way.lanes is None: network.complete_highway_lanes = False

        elif way.railway:
            if not include_railway: continue

            if way.railway in railway_poi_set:
                way.way_poi = way.railway
                POI_way_list.append(way)
                continue
            if way.area and way.area != 'no':
                continue
            if way.railway in negligible_railway_type_set:
                continue

            way.link_type_name = way.railway
            way.link_type = link_type_no_dict['railway']
            if way.oneway is None:
                way.oneway = default_oneway_flag_dict['railway']
            way.link_class = 'railway'
            link_way_list.append(way)

        elif way.aeroway:
            if not include_aeroway: continue

            if way.aeroway in aeroway_poi_set:
                way.way_poi = way.aeroway
                POI_way_list.append(way)
                continue
            if way.area and way.area != 'no':
                continue
            if way.aeroway in negligible_aeroway_type_set:
                continue

            way.link_type_name = way.aeroway
            way.link_type = link_type_no_dict['aeroway']
            if way.oneway is None:
                way.oneway = default_oneway_flag_dict['aeroway']
            way.link_class = 'aeroway'
            link_way_list.append(way)

        else:
            pass

    _identifyCrossingNodes(link_way_list)
    _getNetworkNodes(network)               # osm node -> node

    _identifyPureCycleWays(link_way_list)
    _createLinks(network, link_way_list)
    if offset != 'no': _offsetLinks(network, offset)

    if POIs: generatePOIs(POI_way_list, network, POI_percentage)

    network.osm_node_dict = {}
    network.osm_way_dict = {}
    network.osm_relation_list = []


def _buildNet(network,network_type, link_type, POIs, POI_percentage, offset, min_nodes, combine, int_buffer, default_lanes, default_speed, default_capacity):

    _updateDefaultLSC(default_lanes, default_speed, default_capacity, network)

    _createNLPs(network, link_type, offset, network_type, POIs, POI_percentage)

    # remove isolated nodes and links
    if min_nodes > 1: _removeIsolated(network, min_nodes)

    # combine adjacent links at two-degree nodes
    if combine: combineShortLinks(network)

    # identify complex intersections which contains multiple nodes
    identifyComplexIntersections(network, int_buffer)


def getNetFromOSMFile(osm_filename='map.osm', network_type=('auto',), link_type='all', POIs=False, POI_sampling_ratio=1.0,
                      strict_mode=True, offset='no', min_nodes=1, combine=False, int_buffer=default_int_buffer, bbox=None,
                      default_lanes=False, default_speed=False):
    print('Warning: getNetFromOSMFile() and getNetFromPBFFile() are deprecated and will be removed in a future release.\n'
          '         Please use getNetFromFile().')

    network = getNetFromFile(osm_filename, network_type, link_type, POIs, POI_sampling_ratio, strict_mode, offset, min_nodes,
                             combine, int_buffer, bbox, default_lanes, default_speed)
    return network


def getNetFromPBFFile(pbf_filename='map.osm.pbf', network_type=('auto',), link_type='all', POIs=False, POI_sampling_ratio=1.0,
                      strict_mode=True, offset='no', min_nodes=1, combine=False, int_buffer=default_int_buffer, bbox=None,
                      default_lanes=False, default_speed=False):

    print('Warning: getNetFromOSMFile() and getNetFromPBFFile() are deprecated and will be removed in a future release.\n'
          '         Please use getNetFromFile().')
    network = getNetFromFile(pbf_filename, network_type, link_type, POIs, POI_sampling_ratio, strict_mode, offset, min_nodes,
                             combine, int_buffer, bbox, default_lanes, default_speed)
    return network


def getNetFromFile(filename='map.osm', network_type=('auto',), link_type='all', POIs=False, POI_sampling_ratio=1.0,
                   strict_mode=True, offset='no', min_nodes=1, combine=False, int_buffer=default_int_buffer, bbox=None,
                   default_lanes=False, default_speed=False, default_capacity=False):

    network_type_, link_type_, POIs_, POI_sampling_ratio_, strict_mode_, offset_, min_nodes_, combine_, int_buffer_, \
      bbox_, default_lanes_, default_speed_, default_capacity_ = \
      _checkArgs_getNetFromFile(filename, network_type, link_type, POIs, POI_sampling_ratio,
                 strict_mode, offset, min_nodes, combine, int_buffer, bbox,
                 default_lanes, default_speed, default_capacity)

    network = readOSMFile(filename, POIs_, strict_mode_, bbox_)
    _buildNet(network, network_type_, link_type_, POIs_, POI_sampling_ratio_, offset_, min_nodes_, combine_, int_buffer_,
              default_lanes_, default_speed_, default_capacity_)
    return network


def getNetFromCSV(folder='', enconding=None):
    print('Warning: getNetFromCSV() is deprecated and will be removed in a future release. Please use loadNetFromCSV().\n'
          '         For more information, please refer to the document at https://osm2gmns.readthedocs.io')
    network = loadNetFromCSV(folder, enconding)
    return network


def loadNetFromCSV(folder='', enconding=None):
    # check arguments
    node_data, link_data = readCSVFile(folder, enconding)
    network = Network()
    max_node_id = 0
    max_link_id = 0
    node_id_list = []
    node_coord_list = []

    for node_info in node_data:
        node = Node()
        node.name = node_info['name']
        node.node_id = int(node_info['node_id'])
        if node.node_id > max_node_id: max_node_id = node.node_id
        node.osm_node_id = node_info['osm_node_id']
        node.osm_highway = node_info['osm_highway']
        x_coord, y_coord = float(node_info['x_coord']), float(node_info['y_coord'])
        node.geometry = geometry.Point(x_coord, y_coord)

        node_id_list.append(node.node_id)
        node_coord_list.append((x_coord, y_coord))

        main_node_id = node_info['main_node_id']
        if main_node_id: node.main_node_id = main_node_id
        node.ctrl_type = node_info['ctrl_type']
        poi_id = node_info['poi_id']
        if poi_id: node.poi_id = poi_id

        network.node_dict[node.node_id] = node
    network.max_node_id = max_node_id + 1

    coord_array = np.array(node_coord_list)
    central_lon = coord_array[:,0].mean()
    network.central_lon = central_lon
    xs, ys = from_latlon(coord_array[:,0], coord_array[:,1], central_lon)
    for node_no, node_id in enumerate(node_id_list):
        node = network.node_dict[node_id]
        node.geometry_xy = geometry.Point((round(xs[node_no],xy_precision),round(ys[node_no],xy_precision)))


    for link_info in link_data:
        link = Link()
        link.name = link_info['name']
        link.link_id = int(link_info['link_id'])
        link.osm_way_id = link_info['osm_way_id']
        link.from_node = network.node_dict[int(link_info['from_node_id'])]
        link.to_node = network.node_dict[int(link_info['to_node_id'])]
        link.length = float(link_info['length'])
        lanes = link_info['lanes']
        if lanes:
            link.lanes = int(lanes)
        else:
            network.complete_highway_lanes = False
        free_speed = link_info['free_speed']
        if free_speed: link.free_speed = float(free_speed)
        link.link_type_name = link_info['link_type_name']
        link.link_type = int(link_info['link_type'])

        link.geometry = wkt.loads(link_info['geometry'])
        coord_array = np.array(link.geometry.coords)
        xs, ys = from_latlon(coord_array[:, 0], coord_array[:, 1], central_lon)
        xys = np.vstack((xs, ys)).T
        link.geometry_xy = geometry.LineString(xys)

        link.allowed_uses = link_info['allowed_uses']
        from_biway = int(link_info['from_biway'])
        if from_biway == 1:
            link.from_bidirectional_way = True

        network.link_dict[link.link_id] = link
        link.from_node.outgoing_link_list.append(link)
        link.to_node.incoming_link_list.append(link)
    network.max_link_id = max_link_id + 1

    return network

