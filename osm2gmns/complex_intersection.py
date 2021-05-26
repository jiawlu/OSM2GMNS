from .settings import lonlat_precision, xy_precision
from .classes import Node
from shapely import geometry

def identifyComplexIntersections(network, int_buffer):
    network.complex_intersection_identified = True

    group_list = []
    group_status = []
    for link_id,link in network.link_dict.items():
        if link.length > int_buffer: continue
        if not(link.from_node.ctrl_type == 'signal' and link.to_node.ctrl_type == 'signal'): continue
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

    number_of_main_nodes = 0
    for group_no, group in enumerate(group_list):
        if group_status[group_no] == 0: continue
        for node in group: node.main_node_id = number_of_main_nodes
        number_of_main_nodes += 1


def consolidateComplexIntersections(network):
    node_group_dict = {}
    for node_id, node in network.node_dict.items():
        if node.main_node_id is not None:
            if node.main_node_id in node_group_dict.keys():
                node_group_dict[node.main_node_id].append(node)
            else:
                node_group_dict[node.main_node_id] = [node]

    removal_node_set = set()
    removal_link_set = set()

    for main_node_id, node_group in node_group_dict.items():
        new_node = Node()
        new_node.node_id = network.max_node_id
        new_node.main_node_id = main_node_id
        new_node.ctrl_type = 1
        osm_node_id_list = []
        x_coord_sum, y_coord_sum = 0.0, 0.0
        x_coord_xy_sum, y_coord_xy_sum = 0.0, 0.0

        for node in node_group:
            node.valid = False
            removal_node_set.add(node)

            osm_node_id_list.append(node.osm_node_id)
            x_coord_sum += node.geometry.x
            y_coord_sum += node.geometry.y
            x_coord_xy_sum += node.geometry_xy.x
            y_coord_xy_sum += node.geometry_xy.y

            for link in node.incoming_link_list:
                if link.from_node in node_group:
                    link.valid = False
                    removal_link_set.add(link)
                else:
                    link.to_node = new_node
                    new_node.incoming_link_list.append(link)
            for link in node.outgoing_link_list:
                if link.to_node in node_group:
                    link.valid = False
                    removal_link_set.add(link)
                else:
                    link.from_node = new_node
                    new_node.outgoing_link_list.append(link)

            new_node.osm_highway = node.osm_highway

        new_node.osm_node_id = '_'.join(osm_node_id_list)
        x_coord_ave = round(x_coord_sum / len(node_group),lonlat_precision)
        y_coord_ave = round(y_coord_sum / len(node_group),lonlat_precision)
        new_node.geometry = geometry.Point(x_coord_ave, y_coord_ave)
        x_coord_xy_ave = round(x_coord_xy_sum / len(node_group),xy_precision)
        y_coord_xy_ave = round(y_coord_xy_sum / len(node_group),xy_precision)
        new_node.geometry_xy = geometry.Point(x_coord_xy_ave, y_coord_xy_ave)

        network.node_dict[new_node.node_id] = new_node
        network.max_node_id += 1


    for node in removal_node_set: del network.node_dict[node.node_id]
    for link in removal_link_set: del network.link_dict[link.link_id]