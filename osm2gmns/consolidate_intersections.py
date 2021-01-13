from .classes import *


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
        x_coord_sum = 0
        y_coord_sum = 0

        for node in node_group:
            node.valid = False
            removal_node_set.add(node)

            osm_node_id_list.append(node.osm_node_id)
            x_coord_sum += node.geometry.x
            y_coord_sum += node.geometry.y

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

        new_node.osm_node_id = ';'.join(osm_node_id_list)
        new_node.geometry = geometry.Point(x_coord_sum / len(node_group), y_coord_sum / len(node_group))

        network.node_dict[new_node.node_id] = new_node
        network.max_node_id += 1


    for node in removal_node_set: del network.node_dict[node.node_id]
    for link in removal_link_set: del network.link_dict[link.link_id]