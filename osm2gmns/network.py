from .readfile import *
from .simplification import *
from .complex_intersection import *
from .wayfilters import *
from .pois import *
import re
from shapely import wkt

# todo: xml to dict

def parseNodes(network, nodes, strict_mode):
    osm_node_dict = {}
    for osm_node in nodes:
        node = Node()
        node.osm_node_id = osm_node.attrib['id']
        node.geometry = geometry.Point(float(osm_node.attrib['lon']), float(osm_node.attrib['lat']))

        if strict_mode:
            if not node.geometry.within(network.bounds):
                node.in_region = False

        for info in osm_node:
            if info.tag == 'tag':
                if info.attrib['k'] == 'highway':
                    node.osm_highway = info.attrib['v']

        if 'signal' in node.osm_highway: node.ctrl_type = 1         # todo: check signalized tag

        osm_node_dict[node.osm_node_id] = node
    network.osm_node_dict = osm_node_dict


def newLinkFromWay(link_id, way, direction, ref_node_list):
    link = Link()
    link.osm_way_id = way.osm_way_id
    link.link_id = link_id
    link.name = way.name
    link.link_type_name = way.link_type_name
    link.link_type = way.link_type
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
    link.geometry = getLineFromRefNodes(ref_node_list)
    link.calculateLength()
    return link


def createNodeOnBoundary(node_in,node_outside,network):
    node = Node()
    node.node_id = network.max_node_id
    line = network.bounds.intersection(geometry.LineString([node_in.geometry,node_outside.geometry]))
    node.geometry = geometry.Point(line.coords[1])
    node.is_crossing = True
    network.node_dict[node.node_id] = node
    network.max_node_id += 1
    return node


def getSegmentNodeList(way, segment_no, network):
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
            new_node = createNodeOnBoundary(m_segment_node_list[idx_first_outside-1],m_segment_node_list[idx_first_outside], network)
            m_segment_node_list_group.append(m_segment_node_list[:idx_first_outside] + [new_node])

    if m_segment_node_list[-1].in_region:
        idx_last_outside = -1
        for idx in range(number_of_nodes-2,-1,-1):
            if not m_segment_node_list[idx].in_region:
                idx_last_outside = idx
                break
        new_node = createNodeOnBoundary(m_segment_node_list[idx_last_outside+1],m_segment_node_list[idx_last_outside], network)
        m_segment_node_list_group.append([new_node] + m_segment_node_list[idx_last_outside+1:])

    return m_segment_node_list_group


def createLinks(network, link_way_list):
    link_dict = {}
    max_link_id = network.max_link_id
    for way in link_way_list:
        if way.is_pure_cycle: continue
        way.getNodeListForSegments()
        for segment_no in range(way.number_of_segments):
            m_segment_node_list_group = getSegmentNodeList(way, segment_no, network)
            for m_segment_node_list in m_segment_node_list_group:
                link = newLinkFromWay(max_link_id, way, 1, m_segment_node_list)
                link_dict[link.link_id] = link
                max_link_id += 1
                if not way.oneway:
                    linkb = newLinkFromWay(max_link_id, way, -1, list(reversed(m_segment_node_list)))
                    link_dict[linkb.link_id] = linkb
                    max_link_id += 1
    network.link_dict = link_dict
    network.max_link_id = max_link_id


def identifyCrossingNodes(link_way_list):
    used_node_set = set()
    for way in link_way_list:
        way.ref_node_list[0].is_crossing = True
        way.ref_node_list[-1].is_crossing = True
        for node in way.ref_node_list[1:-1]:
            if node in used_node_set:
                node.is_crossing = True
            else:
                used_node_set.add(node)


def identifyPureCycleWays(link_way_list):
    for way in link_way_list:
        if way.is_cycle:
            way.is_pure_cycle = True
            for node in way.ref_node_list[1:-1]:
                if node.is_crossing:
                    way.is_pure_cycle = False
                    break


def getNetworkNodes(network):
    node_dict = {}
    max_node_id = network.max_node_id
    for osm_node_id, node in network.osm_node_dict.items():
        if node.is_crossing and node.in_region:
            node.node_id = max_node_id
            node_dict[node.node_id] = node
            max_node_id += 1
    network.node_dict = node_dict
    network.max_node_id = max_node_id


def parseWays(network, ways, relations, network_type, POIs):
    osm_way_dict = {}

    for osm_way in ways:
        way = Way()
        way.osm_way_id = osm_way.attrib['id']

        for info in osm_way:
            if info.tag == 'nd':
                ref_node_id = info.attrib['ref']
                try:
                    way.ref_node_list.append(network.osm_node_dict[ref_node_id])
                except KeyError:
                    print(f'  warning: ref node {ref_node_id} in way {way.osm_way_id} is not defined')
            elif info.tag == 'tag':
                if info.attrib['k'] == 'highway':
                    way.highway = info.attrib['v']
                elif info.attrib['k'] == 'railway':
                    way.railway = info.attrib['v']
                elif info.attrib['k'] == 'aeroway':
                    way.aeroway = info.attrib['v']
                elif info.attrib['k'] == 'lanes':
                    lanes = re.findall(r'\d+\.?\d*', info.attrib['v'])
                    if len(lanes) > 0:
                        way.lanes = int(float(lanes[0]))        # in case of decimals
                    else:
                        printlog(f'new lanes type detected at way {way.osm_way_id}, {info.attrib["v"]}','warning')
                elif info.attrib['k'] == 'lanes:forward':
                    way.forward_lanes = int(info.attrib['v'])
                elif info.attrib['k'] == 'lanes:backward':
                    way.backward_lanes = int(info.attrib['v'])
                elif info.attrib['k'] == 'name':
                    way.name = info.attrib['v']
                elif info.attrib['k'] == 'maxspeed':
                    speeds = re.findall(r'\d+\.?\d*', info.attrib['v'])
                    if len(speeds) > 0:
                        way.maxspeed = speeds[0]
                    else:
                        printlog(f'new maxspeed type detected at way {way.osm_way_id}, {info.attrib["v"]}','warning')
                elif info.attrib['k'] == 'oneway':
                    oneway_flag = info.attrib['v']
                    if oneway_flag == 'yes' or oneway_flag == '1':
                        way.oneway = True
                    elif oneway_flag == 'no' or oneway_flag == '0':
                        way.oneway = False
                    elif oneway_flag == '-1':
                        way.oneway = True
                        way.is_reversed = True
                    elif oneway_flag in ['reversible', 'alternating']:
                        # todo: reversible, alternating: https://wiki.openstreetmap.org/wiki/Tag:oneway%3Dreversible
                        way.oneway = False
                    else:
                        printlog(f'new maxspeed type detected at way {way.osm_way_id}, {info.attrib["v"]}','warning')
                elif info.attrib['k'] == 'area':
                    way.area = info.attrib['v']
                elif info.attrib['k'] == 'motor_vehicle':
                    way.motor_vehicle = info.attrib['v']
                elif info.attrib['k'] == 'motorcar':
                    way.motorcar = info.attrib['v']
                elif info.attrib['k'] == 'service':
                    way.service = info.attrib['v']
                elif info.attrib['k'] == 'foot':
                    way.foot = info.attrib['v']
                elif info.attrib['k'] == 'bicycle':
                    way.bicycle = info.attrib['v']
                elif info.attrib['k'] == 'building':
                    way.building = info.attrib['v']
                elif info.attrib['k'] == 'amenity':
                    way.amenity = info.attrib['v']

        osm_way_dict[way.osm_way_id] = way
    network.osm_way_dict = osm_way_dict

    link_way_list = []
    POI_way_list = []
    network_type_set = set(network_type)

    include_railway = True if 'railway' in network_type_set else False
    include_aeroway = True if 'aeroway' in network_type_set else False

    for osm_way_id, way in osm_way_dict.items():
        if way.highway:
            try:
                way.link_type_name = osm_highway_type_dict[way.highway]
                way.link_type = link_type_no_dict[way.link_type_name]
            except KeyError:
                if way.highway not in negligible_link_type_list:
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
            link_way_list.append(way)

        elif way.railway:
            if not include_railway: continue
            if way.area: continue
            way.link_type_name = 'railway'
            way.link_type = link_type_no_dict[way.link_type_name]
            if way.oneway is None:
                way.oneway = default_oneway_flag_dict[way.link_type_name]
            link_way_list.append(way)
        elif way.aeroway:
            if not include_aeroway: continue
            if way.area: continue
            way.link_type_name = 'aeroway'
            way.link_type = link_type_no_dict[way.link_type_name]
            if way.oneway is None:
                way.oneway = default_oneway_flag_dict[way.link_type_name]
            link_way_list.append(way)
        elif way.building or way.amenity:
            POI_way_list.append(way)
        else:
            pass

    identifyCrossingNodes(link_way_list)
    getNetworkNodes(network)

    identifyPureCycleWays(link_way_list)
    createLinks(network, link_way_list)

    if POIs:
        POI_list = generatePOIs(POI_way_list, relations, network)
        network.POI_list = POI_list


def parseOSM(network, nodes, ways, relations, strict_mode, network_type, POIs):
    parseNodes(network, nodes, strict_mode)
    parseWays(network, ways, relations, network_type, POIs)


def removeIsolated(network):
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
        if group_size < isolated_threshold:
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


def getValidNetworkType(network_type):
    if isinstance(network_type,str):
        network_type_temp = (network_type,)
    else:
        network_type_temp = network_type

    network_type_valid = []
    for net_type in network_type_temp:
        if net_type not in network_type_all:
            print(f'network type \'{net_type}\' does not belong to {network_type_all}, it will be skipped')
        else:
            network_type_valid.append(net_type)
    return network_type_valid


def updateDefaultLaneSpeed(default_lanes, default_speed, network):
    if default_lanes:
        if isinstance(default_lanes,bool):
            network.default_lanes = default_lanes_dict
        elif isinstance(default_lanes,dict):
            network.default_lanes = default_lanes
            for link_type_name, lanes in default_lanes_dict.items():
                if link_type_name not in default_lanes.keys():
                    network.default_lanes[link_type_name] = lanes
        else:
            print('unsupported type for argument default_lanes, has set it to default value: False')
    if default_speed:
        if isinstance(default_speed,bool):
            network.default_speed = default_speed_dict
        elif isinstance(default_speed,dict):
            network.default_speed = default_speed
            for link_type_name, speed in default_speed_dict.items():
                if link_type_name not in default_speed.keys():
                    network.default_speed[link_type_name] = speed
        else:
            print('unsupported type for argument default_lanes, has set it to default value: False')


def getNetFromOSMFile(osm_filename='map.osm', network_type=('auto',), POIs=False,strict_mode=True, remove_isolated=True,
                      simplify=True, int_buffer=default_int_buffer, bbox=None, default_lanes=False, default_speed=False):
    """
    :param osm_filename:
    :param network_type:
    :param POIs:
    :param strict_mode:
    :param remove_isolated:
    :param simplify:
    :param int_buffer:
    :param bbox:  (minlat, minlon, maxlat, maxlon)
    :param default_lanes:  True; False; Dict
    :param default_speed:  True; False; Dict
    :return:  a network instance
    """

    # build network
    network = Network()
    updateDefaultLaneSpeed(default_lanes, default_speed, network)

    bounds, nodes, ways, relations = readXMLFile(osm_filename)

    minlat, minlon, maxlat, maxlon = bbox if bbox else bounds['minlat'], bounds['minlon'], bounds['maxlat'], bounds['maxlon']
    network.bounds = geometry.Polygon([(minlon,maxlat),(maxlon,maxlat),(maxlon,minlat),(minlon,minlat)])

    network_type_valid = getValidNetworkType(network_type)
    parseOSM(network, nodes, ways, relations, strict_mode, network_type_valid, POIs)
    del nodes, ways, relations

    # remove isolated nodes and links
    if remove_isolated: removeIsolated(network)

    # merge adjacent links at two-degree nodes
    if simplify: simplifyNetwork(network)

    # identify complex intersections which contains multiple nodes
    identifyComplexIntersections(network,int_buffer)

    return network


# def parsePoints(network, nodes, strict_mode):
#     osm_node_dict = {}
#     node_coordstr_to_node_dict = {}
#
#     for osm_node in nodes:
#         attrs = osm_node['properties']
#
#         node = Node()
#         node.osm_node_id = attrs['osm_id']
#         coord_list = osm_node['geometry']['coordinates']
#         node.geometry = geometry.Point(coord_list)
#
#         if strict_mode:
#             if not node.geometry.within(network.bounds):
#                 node.in_region = False
#
#         if attrs['highway']:
#             node.osm_highway = attrs['highway']
#         if 'signal' in node.osm_highway: node.ctrl_type = 1         # todo: check signalized tag
#
#         coord_str_list = list(map(str, coord_list))
#         node_coordstr_to_node_dict[' '.join(coord_str_list)] = node
#         osm_node_dict[node.osm_node_id] = node
#
#     network.osm_node_dict = osm_node_dict
#     network.node_coordstr_to_node_dict = node_coordstr_to_node_dict
#
#
# def parseLines(network, lines):
#     osm_way_dict = {}
#     for osm_way in lines:
#         attrs = osm_way['properties']
#         way = Way()
#         way.osm_way_id = attrs['osm_id']
#
#         coord_list = osm_way['geometry']['coordinates']
#         for coord in coord_list:
#             coord_str_list = list(map(str, coord))
#             coord_str = ' '.join(coord_str_list)
#             way.ref_node_list.append(network.node_coordstr_to_node_dict[coord_str])
#
#
#
# def parseAreas(network, areas):
#     if areas is None: return
#
#
# def parseOSMJSON(network, points, lines, areas, strict_mode):
#     parsePoints(network, points, strict_mode)
#     parseLines(network, lines)
#     parseAreas(network, areas)
#
#
# def getNetFromJSONFile(folder='', POIs=False,strict_mode=True, remove_isolated=True, simplify=True,
#                        int_buffer=default_int_buffer, bbox=None, default_lanes=False, default_speed=False):
#     network = Network()
#     updateDefaultLaneSpeed(default_lanes, default_speed, network)
#
#     points, lines, areas = readJSONFile(folder, POIs)
#
#     bounds = default_bounds.copy()
#     minlat, minlon, maxlat, maxlon = bbox if bbox else bounds['minlat'], bounds['minlon'], bounds['maxlat'], bounds['maxlon']
#     network.bounds = geometry.Polygon([(minlon,maxlat),(maxlon,maxlat),(maxlon,minlat),(minlon,minlat)])
#
#     parseOSMJSON(network, points, lines, areas, strict_mode)
#     del points, lines, areas
#
#     # remove isolated nodes and links
#     if remove_isolated: removeIsolated(network)
#
#     # merge adjacent links at two-degree nodes
#     if simplify: simplifyNetwork(network)
#
#     # identify complex intersections which contains multiple nodes
#     identifyComplexIntersections(network,int_buffer)
#
#     return network



def getNetFromCSV(folder=''):
    node_data, link_data = readCSVFile(folder)
    network = Network()
    max_node_id = 0
    max_link_id = 0

    for i in range(len(node_data)):
        node = Node()
        node.node_id = node_data.loc[i, 'node_id']
        if node.node_id > max_node_id: max_node_id = node.node_id
        osm_node_id = node_data.loc[i, 'osm_node_id']
        if osm_node_id == osm_node_id: node.osm_node_id = osm_node_id
        osm_highway = node_data.loc[i, 'osm_highway']
        if osm_highway == osm_highway: node.osm_highway = osm_highway
        x_coord, y_coord = node_data.loc[i, 'x_coord'], node_data.loc[i, 'y_coord']
        node.geometry = geometry.Point(x_coord,y_coord)
        main_node_id = node_data.loc[i, 'main_node_id']
        if main_node_id == main_node_id: node.main_node_id = int(main_node_id)
        node.ctrl_type = node_data.loc[i, 'ctrl_type']
        poi_id = node_data.loc[i, 'poi_id']
        if poi_id == poi_id: node.poi_id = int(poi_id)
        network.node_dict[node.node_id] = node
    network.max_node_id = max_node_id + 1

    for i in range(len(link_data)):
        link = Link()
        name = link_data.loc[i, 'name']
        if name == name: link.name = name
        link.link_id = link_data.loc[i, 'link_id']
        if link.link_id > max_link_id: max_link_id = link.link_id
        link.osm_way_id = link_data.loc[i, 'osm_way_id']
        link.from_node = network.node_dict[link_data.loc[i, 'from_node_id']]
        link.to_node = network.node_dict[link_data.loc[i, 'to_node_id']]
        link.length = link_data.loc[i, 'length']
        lanes = link_data.loc[i, 'lanes']
        if lanes == lanes: link.lanes = lanes
        free_speed = link_data.loc[i, 'free_speed']
        if free_speed == free_speed: link.free_speed = free_speed
        link.link_type_name = link_data.loc[i, 'link_type_name']
        link.link_type = link_data.loc[i, 'link_type']
        link.geometry = wkt.loads(link_data.loc[i, 'geometry'])
        from_biway = link_data.loc[i, 'from_biway']
        if from_biway == from_biway:
            if int(from_biway) == 1: link.from_bidirectional_way = True

        network.link_dict[link.link_id] = link
        link.from_node.outgoing_link_list.append(link)
        link.to_node.incoming_link_list.append(link)
    network.max_link_id = max_link_id + 1

    return network