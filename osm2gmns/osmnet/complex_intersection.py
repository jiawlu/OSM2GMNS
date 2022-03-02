#from osm2gmns.networkclass.macronet import Node, Network
#import osm2gmns.settings as og_settings
#from shapely import geometry


def _identifyComplexIntersections(network, int_buffer):
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
    for link_id,link in network.link_dict.items():
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


def consolidateComplexIntersections(network, auto_identify=False, int_buffer=og_settings.default_int_buffer):
    """
    Consolidate each complex intersection that are original represented by multiple nodes in osm into one node. Nodes
    with the same intersection_id will be consolidated into one node. intersection_id of nodes can be obtained in two ways.
    1) set the argument auto_identify as True, then osm2gmns will automatically identify complex intersections and assign
    intersection_id for corresponding nodes; 2) user can assign intersection_id to nodes manually in network csv files (node.csv), and
    load the network using function loadNetFromCSV provided by osm2gmns. Note that, if the second approach is adopted, one
    should make sure the argument auto_identify is set as False to avoid intersection_id overwritten by osm2gmns.

    Rules used in osm2gmns to identify if two nodes belong to a complex intersection: 1) ctrl_type of the two nodes must be signal;
    2) there is a link connecting these two nodes, and the length of the link is shorter than or equal to the argument int_buffer

    Parameters
    ----------
    network: Network
        osm2gmns Network object
    auto_identify: bool
        if automatically identify complex intersections using built-in methods in osm2gmns. nodes that belong to a complex
        intersection will be assigned with the same intersection_id
    int_buffer: float
        the threshold used to check if two nodes belong to one complex intersection. the unit is meter

    Returns
    -------
    None

    """

    if auto_identify:
        _identifyComplexIntersections(network, int_buffer)

    if og_settings.verbose:
        print('Consolidating Complex Intersections')

    node_group_dict = {}
    node_group_ctrl_type_dict = {}
    for node_id, node in network.node_dict.items():
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
            # node.valid = False
            removal_node_set.add(node)
            osm_node_id_list.append(node.osm_node_id)
            x_coord_sum += node.geometry.x
            y_coord_sum += node.geometry.y
            x_coord_xy_sum += node.geometry_xy.x
            y_coord_xy_sum += node.geometry_xy.y

            for link in node.incoming_link_list:
                if link.from_node in node_group:
                    # link.valid = False
                    removal_link_set.add(link)
                else:
                    link.to_node = new_node
                    new_node.incoming_link_list.append(link)
            for link in node.outgoing_link_list:
                if link.to_node in node_group:
                    # link.valid = False
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


    for node in removal_node_set: del network.node_dict[node.node_id]
    for link in removal_link_set: del network.link_dict[link.link_id]