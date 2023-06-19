from osm2gmns.networkclass.macronet import Node, Link, Network
from osm2gmns.io.read_from_osm import readOSMFile
from osm2gmns.osmnet.osmclasses import OSMNode
from osm2gmns.osmnet.combine_links import combineShortLinks
from osm2gmns.osmnet.pois import generatePOIs
from osm2gmns.osmnet.wayfilters import *
from osm2gmns.osmnet.check_args import checkArgs_getNetFromFile
from osm2gmns.utils.util import getLogger
from osm2gmns.utils.util_geo import offsetLine
import osm2gmns.settings as og_settings
from shapely import geometry

# todo: remove useless nodes link_type

def _createNodeOnBoundary(node_in, node_outside, network):
    line = network.bounds.intersection(geometry.LineString([node_in.geometry,node_outside.geometry]))
    lon, lat = line.coords[1]
    geometry_lonlat = geometry.Point((round(lon,og_settings.lonlat_coord_precision),round(lat,og_settings.lonlat_coord_precision)))
    boundary_osm_node = OSMNode('', '', geometry_lonlat, True, '', '')
    boundary_osm_node.geometry_xy = network.GT.geo_from_latlon(geometry_lonlat)
    boundary_osm_node.is_crossing = True
    boundary_osm_node.notes = 'boundary node created by osm2gmns'
    return boundary_osm_node


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


def _createNodeFromOSMNode(network, osmnode):
    if osmnode.node is None:
        node = Node(network.max_node_id)
        node.buildFromOSMNode(osmnode)
        osmnode.node = node
        network.node_dict[node.node_id] = node
        network.max_node_id += 1


def _createNodesAndLinks(network, link_way_list):
    if og_settings.verbose:
        print('    generating nodes and links')

    link_dict = {}
    max_link_id = network.max_link_id
    for way in link_way_list:
        if way.is_pure_cycle: continue
        way.getNodeListForSegments()
        for segment_no in range(way.number_of_segments):
            m_segment_node_list_group = _getSegmentNodeList(way, segment_no, network)
            for m_segment_node_list in m_segment_node_list_group:
                if len(m_segment_node_list) < 2: continue
                _createNodeFromOSMNode(network, m_segment_node_list[0])
                _createNodeFromOSMNode(network, m_segment_node_list[-1])

                link = Link(max_link_id)
                link.buildFromOSMWay(way, 1, m_segment_node_list, network.default_lanes, network.default_speed, network.default_capacity)
                link_dict[link.link_id] = link
                max_link_id += 1
                if not way.oneway:
                    linkb = Link(max_link_id)
                    linkb.buildFromOSMWay(way, -1, list(reversed(m_segment_node_list)), network.default_lanes, network.default_speed, network.default_capacity)
                    link_dict[linkb.link_id] = linkb
                    max_link_id += 1
    network.link_dict = link_dict
    network.max_link_id = max_link_id


def _identifyPureCycleWays(link_way_list):
    for way in link_way_list:
        if way.is_cycle:
            way.is_pure_cycle = True
            for node in way.ref_node_list[1:-1]:
                if node.is_crossing:
                    way.is_pure_cycle = False
                    break


def _addSignalFromLink(network):
    for link_id, link in network.link_dict.items():
        if link.ctrl_type == 'signal':
            to_node = link.to_node
            if to_node.ctrl_type != 'signal':
                if len(to_node.incoming_link_list) > 1 or len(to_node.outgoing_link_list) > 1:
                    to_node.ctrl_type = 'signal'


def _removeIsolated(network, min_nodes):
    if og_settings.verbose:
        print(f'    removing sub networks with less than {min_nodes} nodes')

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
        idx = 0
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
            network.default_lanes = og_settings.default_lanes_dict
        elif isinstance(default_lanes,dict):
            network.default_lanes = default_lanes
            for link_type_name, lanes in og_settings.default_lanes_dict.items():
                if link_type_name not in default_lanes.keys():
                    network.default_lanes[link_type_name] = lanes

    if default_speed:
        if isinstance(default_speed,bool):
            network.default_speed = og_settings.default_speed_dict
        elif isinstance(default_speed,dict):
            network.default_speed = default_speed
            for link_type_name, speed in og_settings.default_speed_dict.items():
                if link_type_name not in default_speed.keys():
                    network.default_speed[link_type_name] = speed

    if default_capacity:
        if isinstance(default_capacity,bool):
            network.default_capacity = og_settings.default_capacity_dict
        elif isinstance(default_capacity,dict):
            network.default_capacity = default_capacity
            for link_type_name, capacity in og_settings.default_capacity_dict.items():
                if link_type_name not in default_speed.keys():
                    network.default_capacity[link_type_name] = capacity


def _offsetLinks(network, offset):
    if og_settings.verbose:
        print('    offseting link geometries')

    distance_sp = -2 if offset == 'right' else 2
    distance_ma = 2 if offset == 'right' else -2

    GT = network.GT

    for _, link in network.link_dict.items():
        if link.from_bidirectional_way:
            geometry_xy = link.geometry_xy.offset_curve(distance=distance_sp, join_style=2)
            if isinstance(geometry_xy, geometry.MultiLineString):
                geometry_xy = offsetLine(link.geometry_xy, distance_ma)

            link.geometry_xy = geometry_xy
            link.geometry = GT.geo_to_latlon(link.geometry_xy)

            # distance = max(link.lanes_list) / 2 * 3.5
            # geometry_xy = link.geometry_xy.parallel_offset(distance=2, side=offset, join_style=2)
            # if offset == 'right':
            #     if isinstance(geometry_xy, geometry.MultiLineString):
            #         coords = []
            #         for ls in geometry_xy.geoms: coords += list(ls.coords)[::-1]
            #         link.geometry_xy = geometry.LineString(coords)
            #     else:
            #         link.geometry_xy = geometry.LineString(list(geometry_xy.coords)[::-1])
            # elif offset == 'left':
            #     link.geometry_xy = geometry_xy
            #
            # link.geometry = GT.geo_to_latlon(link.geometry_xy)


def _preprocessWays(osmnetwork, link_types, network_types):
    link_way_list = []
    POI_way_list = []
    network_types_set = set(network_types)
    include_railway = True if 'railway' in network_types_set else False
    include_aeroway = True if 'aeroway' in network_types_set else False

    for _, way in osmnetwork.osm_way_dict.items():
        if way.building or way.amenity or way.leisure:
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
            if len(way.ref_node_list) < 2:
                continue

            try:
                way.link_type_name, way.is_link = og_settings.osm_highway_type_dict[way.highway]
                way.link_type = og_settings.link_type_no_dict[way.link_type_name]
            except KeyError:
                logger = getLogger()
                if logger: logger.warning(f'new highway type at way {way.osm_way_id}, {way.highway}')
                continue

            valid_link_type = link_types == 'all' or way.link_type_name in link_types
            if not valid_link_type:
                continue

            allowable_agent_type_list = getAllowableAgentType(way)
            way.allowable_agent_type_list = list(set(allowable_agent_type_list).intersection(network_types_set))
            if len(way.allowable_agent_type_list) == 0:
                continue
            way.allowed_uses = way.allowable_agent_type_list

            way.ref_node_list[0].is_crossing = True
            way.ref_node_list[-1].is_crossing = True
            for node in way.ref_node_list:
                node.usage_count += 1

            if way.ref_node_list[0] is way.ref_node_list[-1]:
                way.is_cycle = True
            if way.oneway is None:
                if way.junction in ['circular', 'roundabout']:
                    way.oneway = True
                else:
                    way.oneway = og_settings.default_oneway_flag_dict[way.link_type_name]
            way.link_class = 'highway'
            link_way_list.append(way)

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
            if len(way.ref_node_list) < 2:
                continue

            way.ref_node_list[0].is_crossing = True
            way.ref_node_list[-1].is_crossing = True
            for node in way.ref_node_list[1:-1]: node.usage_count += 1

            way.link_type_name = way.railway
            way.link_type = og_settings.link_type_no_dict['railway']
            if way.oneway is None:
                way.oneway = og_settings.default_oneway_flag_dict['railway']
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
            if len(way.ref_node_list) < 2:
                continue

            way.ref_node_list[0].is_crossing = True
            way.ref_node_list[-1].is_crossing = True
            for node in way.ref_node_list[1:-1]: node.usage_count += 1

            way.link_type_name = way.aeroway
            way.link_type = og_settings.link_type_no_dict['aeroway']
            if way.oneway is None:
                way.oneway = og_settings.default_oneway_flag_dict['aeroway']
            way.link_class = 'aeroway'
            link_way_list.append(way)

        else:
            pass

    osmnetwork.link_way_list = link_way_list
    osmnetwork.POI_way_list = POI_way_list


def _identifyCrossingOSMNodes(osm_node_dict):
    for _, osmnode in osm_node_dict.items():
        if osmnode.usage_count >= 2 or osmnode.ctrl_type == 'signal':
            osmnode.is_crossing = True


def _createNLPs(osmnetwork, network, link_types, network_types, POI, POI_percentage):
    _preprocessWays(osmnetwork, link_types, network_types)
    _identifyCrossingOSMNodes(osmnetwork.osm_node_dict)
    _identifyPureCycleWays(osmnetwork.link_way_list)
    _createNodesAndLinks(network, osmnetwork.link_way_list)
    _addSignalFromLink(network)

    if POI: generatePOIs(osmnetwork.POI_way_list, osmnetwork.osm_relation_list, network, POI_percentage)



def _buildNet(osmnetwork, network_types, link_types, POI, POI_percentage, offset, min_nodes, combine, default_lanes,
              default_speed, default_capacity, start_node_id, start_link_id):
    if og_settings.verbose:
        print('  parsing osm network')

    network = Network()
    network.max_node_id = start_node_id
    network.max_link_id = start_link_id

    network.GT, network.bounds = osmnetwork.GT, osmnetwork.bounds

    # update default lanes, speed, and capacity
    _updateDefaultLSC(default_lanes, default_speed, default_capacity, network)

    # create node, link, poi
    _createNLPs(osmnetwork, network, link_types, network_types, POI, POI_percentage)

    # remove isolated nodes and links
    if min_nodes > 1: _removeIsolated(network, min_nodes)

    # combine adjacent links at two-degree nodes
    if combine: combineShortLinks(network)

    # offset two-way overlapping links
    if offset != 'no': _offsetLinks(network, offset)

    return network


def getNetFromFile(filename='map.osm', network_types=('auto',), link_types='all', POI=True, POI_sampling_ratio=1.0,
                   strict_mode=True, offset='no', min_nodes=1, combine=False, bbox=None,
                   default_lanes=False, default_speed=False, default_capacity=False, start_node_id=0, start_link_id=0):
    """
    Get an osm2gmns Network object from an osm file

    Parameters
    ----------
    filename: str
        path of an osm file; can be absolute or relative path; supported osm file formats: .osm, .xml, and .pbf
    network_types: str, tuple of strings, list of strings, or set of strings
        osm2gmns supports five different network types, including auto, bike, walk, railway, and aeroway.
        network_types can be any one or any combinations of the five supported network types
    link_types: str, tuple of strings, list of strings, or set of strings
        supported link types: motorway, trunk, primary, secondary, tertiary, residential, service, cycleway,
        footway, track, unclassified, connector, railway, and aeroway.
    POI: bool
        if extract point of interest information
    POI_sampling_ratio: float
        prcentage of POIs to be extracted if POI is set as True. this value should be a float number between 0.0 and 1.0.
    strict_mode: bool
        if True, network elements (node, link, poi) outside the boundary will be discarded
    offset: str
        offset overlapping links. the value of this argument can be 'left', 'right', or 'no'
    min_nodes: int
        a network return by the function may contain several sub-networks that are disconnected from each other.
        sub-networks with the number of nodes less than min_nodes will be discarded
    combine: bool
        if True, adjacent short links with the same attributes will be combined into a long link. the operation will only
        be performed on short links connected with a two-degree nodes (one incoming link and one outgoing link)
    bbox: tuple of four float/int values, list of four float/int values, None
        specify the boundary of the network to be extracted, consisting of minimum latitude, minimum longtitude, maximum latitude, and maximum longitud.
        if None, osm2gmns will try to find network boundary from the input osm file
    default_lanes: bool, dict
        if True, assign a default value for links without lanes information based on built-in settings. if a dict,
        assign a default value for links without lanes information based on the dict passed by users.
    default_speed: bool, dict
        if True, assign a default value for links without speed information based on built-in settings. if a dict,
        assign a default value for links without speed information based on the dict passed by users.
    default_capacity: bool, dict
        if True, assign a default value for links without capacity information based on built-in settings. if a dict,
        assign a default value for links without capacity information based on the dict passed by users.
    start_node_id: int
        osm2gmns assigns node_ids to generated nodes starting from start_node_id.
    start_link_id: int
        osm2gmns assigns link_ids to generated links starting from start_link_id

    Returns
    -------
    network: Network
        osm2gmns Network object
    """

    if og_settings.verbose:
        print('arguments used for network parsing:')
        print(f'  filename: {filename}')
        print(f'  network_types: {network_types}')
        print(f'  link_types: {link_types}')
        print(f'  POI: {POI}')
        print(f'  POI_sampling_ratio: {POI_sampling_ratio}')
        print(f'  strict_mode: {strict_mode}')
        print(f'  offset: {offset}')
        print(f'  min_nodes: {min_nodes}')
        print(f'  combine: {combine}')
        print(f'  bbox: {bbox}')
        print(f'  default_lanes: {default_lanes}')
        print(f'  default_speed: {default_speed}')
        print(f'  default_capacity: {default_capacity}')
        print(f'  start_node_id: {start_node_id}')
        print(f'  start_link_id: {start_link_id}\n')

        print('Building Network from OSM file')

    network_types_, link_types_, POI_, POI_sampling_ratio_, strict_mode_, offset_, min_nodes_, combine_, \
        bbox_, default_lanes_, default_speed_, default_capacity_, start_node_id_, start_link_id_ = \
        checkArgs_getNetFromFile(filename, network_types, link_types, POI, POI_sampling_ratio, strict_mode, offset,
                                min_nodes, combine, bbox, default_lanes, default_speed, default_capacity, start_node_id,
                                 start_link_id)

    osmnetwork = readOSMFile(filename, POI_, strict_mode_, bbox_)

    network = _buildNet(osmnetwork, network_types_, link_types_, POI_, POI_sampling_ratio_, offset_, min_nodes_, combine_,
                        default_lanes_, default_speed_, default_capacity_, start_node_id_, start_link_id_)

    if og_settings.verbose:
        print(f'  number of nodes: {len(network.node_dict)}, number of links: {len(network.link_dict)}, number of pois: {len(network.POI_list)}')

    return network


