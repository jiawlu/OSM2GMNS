import osm2gmns.settings as og_settings
from shapely import wkt, Point, Polygon, MultiPolygon
import csv


def generateNodeActivityInfo(network, zone_file=None):
    """
    Generate activity information, including activity_type, is_boundary, zone_id for nodes. activity_type includes
    motorway, primary, secondary, tertiary, residential, etc, and is determined by adjacent links,
    If a zone_file is provided, zone_id of boundary nodes will be determined by zones defined in the zone_file.
    Otherwise, for each boundary node, its node_id will be used as zone_id.

    Parameters
    ----------
    network: Network
        osm2gmns Network object
    zone_file: str, None
        filename of the zone file. optional

    Returns
    -------
    None
    """

    if og_settings.verbose:
        print('Generating Node Activity Information')

    # node activity
    node_adjacent_link_type_count_dict = {}

    for link_id, link in network.link_dict.items():
        if link.link_type_name == 'connector': continue

        from_node = link.from_node
        if from_node not in node_adjacent_link_type_count_dict.keys():
            node_adjacent_link_type_count_dict[from_node] = {}
        adjacent_link_type_count_dict = node_adjacent_link_type_count_dict[from_node]

        if link.link_type_name in adjacent_link_type_count_dict.keys():
            adjacent_link_type_count_dict[link.link_type_name] += 1
        else:
            adjacent_link_type_count_dict[link.link_type_name] = 1

        to_node = link.to_node
        if to_node not in node_adjacent_link_type_count_dict.keys():
            node_adjacent_link_type_count_dict[to_node] = {}
        adjacent_link_type_count_dict = node_adjacent_link_type_count_dict[to_node]

        if link.link_type_name in adjacent_link_type_count_dict.keys():
            adjacent_link_type_count_dict[link.link_type_name] += 1
        else:
            adjacent_link_type_count_dict[link.link_type_name] = 1

    for node_id, node in network.node_dict.items():
        if node.poi_id is not None:
            node.activity_type = 'poi'
        elif node in node_adjacent_link_type_count_dict.keys():
            adjacent_link_type_count_dict = node_adjacent_link_type_count_dict[node]
            max_count_type = ''
            max_count = 0
            for link_type_name, count in adjacent_link_type_count_dict.items():
                if count > max_count:
                    max_count = count
                    max_count_type = link_type_name
            node.activity_type = max_count_type

    # boundary
    for node_id, node in network.node_dict.items():
        node.is_boundary = 0
        if node.activity_type == 'poi': continue

        if len(node.outgoing_link_list) == 0:
            node.is_boundary = -1
        elif len(node.incoming_link_list) == 0:
            node.is_boundary = 1
        elif (len(node.incoming_link_list) == 1) and (len(node.outgoing_link_list) == 1):
            ib_link = node.incoming_link_list[0]
            ob_link = node.outgoing_link_list[0]
            if ib_link.from_node is ob_link.to_node:
                node.is_boundary = 2

    # zone
    point_zone_dict = {}
    polygon_zone_dict = {}
    if zone_file is not None:
        fin = open(zone_file, 'r')
        reader = csv.DictReader(fin)
        for zone_info in reader:
            zond_id = zone_info['zone_id']
            geo = wkt.loads(zone_info['geometry'])
            if isinstance(geo, Point):
                point_zone_dict[zond_id] = geo
            elif isinstance(geo, Polygon) or isinstance(geo, MultiPolygon):
                polygon_zone_dict[zond_id] = geo
            else:
                print(f'invalid geometry type detected for zone {zond_id}. only support Point, Polygon and MultiPolygon')

    for node_id, node in network.node_dict.items():
        if node.is_boundary == 0: continue
        if zone_file is None:
            node.zone_id = node.node_id
            continue
        polygon_zone_found = False
        for zone_id, polygon in polygon_zone_dict.items():
            if polygon.covers(node.geometry):
                polygon_zone_found = True
                node.zone_id = zone_id
                break
        if polygon_zone_found: continue
        min_distance = 1e10
        nearest_zone_id = None
        for zone_id, point in point_zone_dict.items():
            distance = node.geometry.distance(point)
            if distance < min_distance:
                min_distance = distance
                nearest_zone_id = zone_id
        node.zone_id = nearest_zone_id


def generateLinkVDFInfo(network):
    """
    Generate VDF information, including VDF_fftt1 and VDF_cap1 for links.
    The unit of VDF_fftt1 and VDF_cap1 are min and veh/hour/link, respectively

    Parameters
    ----------
    network: Network
        osm2gmns Network object

    Returns
    -------
    None
    """

    if og_settings.verbose:
        print('Generating Link VDF Information')

    for link_id, link in network.link_dict.items():
        if link.capacity is None:
            lanes = og_settings.default_lanes_dict[link.link_type_name] if link.lanes is None else link.lanes
            link.VDF_cap1 = lanes * og_settings.default_capacity_dict[link.link_type_name]
        else:
            link.VDF_cap1 = link.capacity

        if link.free_speed is None:
            free_speed = og_settings.default_speed_dict[link.link_type_name]
        else:
            free_speed = link.free_speed
        link.VDF_FFTT1 = link.length / free_speed * 0.06
