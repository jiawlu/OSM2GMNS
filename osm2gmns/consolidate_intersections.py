from .classes import *


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
            osm_node_id_list.append(node.osm_node_id)

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

        new_node.x_coord = x_coord_sum / len(node_group)
        new_node.y_coord = y_coord_sum / len(node_group)
        new_node.osm_node_id = ';'.join(osm_node_id_list)

        network.node_set.add(new_node)
        current_node_id += 1

    for node in removal_node_set: network.node_set.remove(node)
    for link in removal_link_set: network.link_set.remove(link)