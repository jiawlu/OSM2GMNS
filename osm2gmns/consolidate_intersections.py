from .classes import *
import pandas as pd


def consolidateComplexIntersections_old(network,external_file=None):
    network.consolidated = True

    max_node_id = 0
    node_group_dict = {}
    for node in network.node_set:
        if node.node_id > max_node_id:
            max_node_id = node.node_id
        if node.main_node_id is not None:
            if node.main_node_id in node_group_dict.keys():
                node_group_dict[node.main_node_id].append(node)
            else:
                node_group_dict[node.main_node_id] = [node]

    current_node_id = max_node_id + 1
    removal_node_set = set()
    removal_link_set = set()

    if external_file is None:
        complex_intersection_set = network.complex_intersection_set
    else:
        complex_intersection_set = set()

        complex_int_data = pd.read_csv(external_file)
        for i in range(len(complex_int_data)):
            group_id = complex_int_data.loc[i,'group_id']
            node_id_str = complex_int_data.loc[i,'node_id']
            node_id_str_list = node_id_str.split(';')

            try:
                node_group_list = [network.node_id_to_node_dict[int(node_id_str)] for node_id_str in node_id_str_list]
            except KeyError as e:
                print(f'cannot find node {e.args[0]} in the network when consolidating intersection group {group_id}, this group will keep unchanged')
                continue
            node_group = tuple(node_group_list)
            complex_intersection_set.add(node_group)

    for node_group in complex_intersection_set:
        new_node = Node()
        new_node.node_id = current_node_id
        x_coord_sum = 0
        y_coord_sum = 0
        osm_node_id_list = []

        for node in node_group:
            node.valid = False
            removal_node_set.add(node)

            x_coord_sum += node.x_coord
            y_coord_sum += node.y_coord
            osm_node_id_list.append(str(node.osm_node_id))

            for link in node.incoming_link_list:
                if link.from_node in node_group:
                    link.valid = False
                    removal_link_set.add(link)
                else:
                    link.to_node = new_node
            for link in node.outgoing_link_list:
                if link.to_node in node_group:
                    link.valid = False
                    removal_link_set.add(link)
                else:
                    link.from_node = new_node

            new_node.osm_highway = node.osm_highway

        new_node.x_coord = x_coord_sum / len(node_group)
        new_node.y_coord = y_coord_sum / len(node_group)
        new_node.osm_node_id = ';'.join(osm_node_id_list)

        network.node_set.add(new_node)
        current_node_id += 1

    for node in removal_node_set: network.node_set.remove(node)
    for link in removal_link_set: network.link_set.remove(link)



def consolidateComplexIntersections(network):
    max_node_id = 0
    node_group_dict = {}
    for node in network.node_set:
        if node.node_id > max_node_id:
            max_node_id = node.node_id
        if node.main_node_id is not None:
            if node.main_node_id in node_group_dict.keys():
                node_group_dict[node.main_node_id].append(node)
            else:
                node_group_dict[node.main_node_id] = [node]

    current_node_id = max_node_id + 1
    removal_node_set = set()
    removal_link_set = set()

    for main_node_id, node_group in node_group_dict.items():
        new_node = Node()
        new_node.node_id = current_node_id
        new_node.main_node_id = main_node_id
        new_node.ctrl_type = 1
        x_coord_sum = 0
        y_coord_sum = 0
        osm_node_id_list = []

        for node in node_group:
            node.valid = False
            removal_node_set.add(node)

            x_coord_sum += node.x_coord
            y_coord_sum += node.y_coord
            osm_node_id_list.append(str(node.osm_node_id))

            for link in node.incoming_link_list:
                if link.from_node in node_group:
                    link.valid = False
                    removal_link_set.add(link)
                else:
                    link.to_node = new_node
            for link in node.outgoing_link_list:
                if link.to_node in node_group:
                    link.valid = False
                    removal_link_set.add(link)
                else:
                    link.from_node = new_node

            new_node.osm_highway = node.osm_highway

        new_node.x_coord = x_coord_sum / len(node_group)
        new_node.y_coord = y_coord_sum / len(node_group)
        new_node.osm_node_id = ';'.join(osm_node_id_list)

        network.node_set.add(new_node)
        current_node_id += 1

    for node in removal_node_set: network.node_set.remove(node)
    for link in removal_link_set: network.link_set.remove(link)