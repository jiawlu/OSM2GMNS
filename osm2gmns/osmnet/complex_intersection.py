from osm2gmns.networkclass.macronet import Node, Network
import osm2gmns.settings as og_settings
from shapely import geometry
import csv
import os
import sys


def _designateComplexIntersectionsFromIntFile(network, int_file, int_buffer):
    if not os.path.exists(int_file):
        sys.exit(f'ERROR: int_file {int_file} does not exist')

    fin = open(int_file, 'r')
    reader = csv.DictReader(fin)

    for field in ['x_coord', 'y_coord']:
        if field not in reader.fieldnames:
            sys.exit(f'ERROR: required field ({field}) does not exist in the int_file')

    max_intersection_id = network.max_intersection_id
    for int_info in reader:
        int_center = geometry.Point(float(int_info['x_coord']), float(int_info['y_coord']))
        int_center_xy = network.GT.geo_from_latlon(int_center)
        if 'int_buffer' in reader.fieldnames:
            buffer_ = int_info['int_buffer']
            buffer_ = float(buffer_) if buffer_ else int_buffer
        else:
            buffer_ = int_buffer

        intersection_nodes = [node for _, node in network.node_dict.items() if node.intersection_id is None and int_center_xy.distance(node.geometry_xy) <= buffer_]

        if len(intersection_nodes) < 2:
            continue

        for node in intersection_nodes:
            node.intersection_id = max_intersection_id
        max_intersection_id += 1

    network.max_intersection_id = max_intersection_id



def _autoidentifyComplexIntersections(network, int_buffer):
    """
    Identify nodes that belongs to one intersection in real life. Nodes that
    belong to one intersection will be assigned with the same intersection_id.
    Only signalized nodes will be checked.

    The reason why only signalized nodes will be checked is that we use a
    distance-based rule here, and there are many short links in osm. If all
    nodes are checked, some short links will be indentified as intersections
    by mistake.

    Parameters
    ----------
    network : Network
        Network instance
    int_buffer : float
        A threshold to check if two connected nodes belong to one intersection.
        If the length of a link that connects two nodes is shorter than int_buffer,
        these two nodes come from one intersection.

    Returns
    -------
    None
    """

    group_list = []
    group_status = []
    for _,link in network.link_dict.items():
        if link.length > int_buffer: continue
        if not (link.from_node.intersection_id is None and link.to_node.intersection_id is None): continue
        if not (link.from_node.ctrl_type == 'signal' and link.to_node.ctrl_type == 'signal'): continue
        group_list.append({link.from_node, link.to_node})
        group_status.append(1)

    number_of_valid_groups = sum(group_status)
    while True:
        for group_no1,group1 in enumerate(group_list):
            if group_status[group_no1] == 0: continue
            for group_no2,group2 in enumerate(group_list):
                if group_status[group_no2] == 0: continue
                if group_no1 == group_no2: continue
                if len(group1.intersection(group2)) > 0:
                    group1.update(group2)
                    group_status[group_no2] = 0

        new_number_of_valid_groups = sum(group_status)
        if number_of_valid_groups == new_number_of_valid_groups:
            break
        else:
            number_of_valid_groups = new_number_of_valid_groups

    max_intersection_id = network.max_intersection_id
    for group_no, group in enumerate(group_list):
        if group_status[group_no] == 0: continue
        for node in group: node.intersection_id = max_intersection_id
        max_intersection_id += 1
    network.max_intersection_id = max_intersection_id


def consolidateComplexIntersections(network, auto_identify=False, intersection_file=None, int_buffer=og_settings.default_int_buffer):
    """
    Consolidate each complex intersection that are originally represented by multiple nodes in osm into one node. Nodes
    with the same intersection_id will be consolidated into one node. intersection_id of nodes can be obtained in three ways.

    (1) set the argument auto_identify as True, then osm2gmns will automatically identify complex intersections and assign
    intersection_id for corresponding nodes;

    (2) provide an intersection file that specifies the central position (required) and buffer (optional) of each complex intersection.

    (3) user can assign intersection_id to nodes manually in network csv files (node.csv), and load the network using function
    loadNetFromCSV provided by osm2gmns.

    The priority of the three approaches is (3) > (2) > (1).
    Rules used in the approach (1) to identify if two nodes belong to a complex intersection: (a) ctrl_type of the two nodes must be signal;
    (b) there is a link connecting these two nodes, and the length of the link is shorter than or equal to the argument int_buffer.

    Parameters
    ----------
    network: Network
        osm2gmns Network object
    auto_identify: bool
        if automatically identify complex intersections using built-in methods in osm2gmns. nodes that belong to a complex
        intersection will be assigned with the same intersection_id
    intersection_file: str
        path of an intersction csv file that specifies complex intersections. required fields: central position of intersections
        (in the form of x_coord and y_coord); optional field: int_buffer (if not specified, the global int_buffer will be used,
        i.e., the forth arugment). For each record in the int_file, osm2gmns consolidates all nodes with a distance to the
        central position shorter than buffer.
    int_buffer: float
        the threshold used to check if two nodes belong to one complex intersection. the unit is meter

    Returns
    -------
    None

    """

    if intersection_file is not None:
        _designateComplexIntersectionsFromIntFile(network, intersection_file, int_buffer)

    if auto_identify:
        _autoidentifyComplexIntersections(network, int_buffer)

    if og_settings.verbose:
        print('Consolidating Complex Intersections')

    node_group_dict = {}
    node_group_ctrl_type_dict = {}
    for _, node in network.node_dict.items():
        if node.intersection_id is not None:
            if node.intersection_id in node_group_dict.keys():
                node_group_dict[node.intersection_id].append(node)
            else:
                node_group_dict[node.intersection_id] = [node]
                node_group_ctrl_type_dict[node.intersection_id] = False
            if node.ctrl_type == 'signal':
                node_group_ctrl_type_dict[node.intersection_id] = True

    removal_node_set = set()
    removal_link_set = set()
    number_of_intersections_consolidated = 0

    for intersection_id, node_group in node_group_dict.items():
        if len(node_group) < 2:
            continue

        new_node = Node(network.max_node_id)
        new_node.intersection_id = intersection_id
        if node_group_ctrl_type_dict[intersection_id]:
            new_node.ctrl_type = 'signal'
        osm_node_id_list = []
        x_coord_sum, y_coord_sum = 0.0, 0.0
        x_coord_xy_sum, y_coord_xy_sum = 0.0, 0.0

        for node in node_group:
            removal_node_set.add(node)
            osm_node_id_list.append(node.osm_node_id if node.osm_node_id is not None else 'None')
            x_coord_sum += node.geometry.x
            y_coord_sum += node.geometry.y
            x_coord_xy_sum += node.geometry_xy.x
            y_coord_xy_sum += node.geometry_xy.y

            for link in node.incoming_link_list:
                if link.from_node in node_group:
                    removal_link_set.add(link)
                else:
                    link.to_node = new_node
                    new_node.incoming_link_list.append(link)
            for link in node.outgoing_link_list:
                if link.to_node in node_group:
                    removal_link_set.add(link)
                else:
                    link.from_node = new_node
                    new_node.outgoing_link_list.append(link)

            new_node.osm_highway = node.osm_highway

        new_node.osm_node_id = '_'.join(osm_node_id_list)
        x_coord_ave = round(x_coord_sum / len(node_group), og_settings.lonlat_coord_precision)
        y_coord_ave = round(y_coord_sum / len(node_group), og_settings.lonlat_coord_precision)
        new_node.geometry = geometry.Point(x_coord_ave, y_coord_ave)
        x_coord_xy_ave = round(x_coord_xy_sum / len(node_group), og_settings.local_coord_precision)
        y_coord_xy_ave = round(y_coord_xy_sum / len(node_group), og_settings.local_coord_precision)
        new_node.geometry_xy = geometry.Point(x_coord_xy_ave, y_coord_xy_ave)

        network.node_dict[new_node.node_id] = new_node
        network.max_node_id += 1
        number_of_intersections_consolidated += 1

    for node in removal_node_set: del network.node_dict[node.node_id]
    for link in removal_link_set: del network.link_dict[link.link_id]

    if og_settings.verbose:
        print(f'    {number_of_intersections_consolidated} intersections have been consolidated')