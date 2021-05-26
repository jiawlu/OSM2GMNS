from .settings import default_lanes_dict, default_speed_dict, default_capacity_dict

def generateNodeActivityInfo(network):
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

    for node_id, node in network.node_dict.items():
        node.is_boundary = False
        if node.activity_type == 'poi': continue
        if (len(node.incoming_link_list) == 0) or (len(node.outgoing_link_list) == 0):
            node.is_boundary = True
            continue

        if (len(node.incoming_link_list) == 1) and (len(node.outgoing_link_list) == 1):
            ib_link = node.incoming_link_list[0]
            ob_link = node.outgoing_link_list[0]
            if ib_link.from_node is ob_link.to_node:
                node.is_boundary = True


def generateLinkVDFInfo(network):
    for link_id, link in network.link_dict.items():
        if link.capacity is None:
            lanes = default_lanes_dict[link.link_type_name] if link.lanes is None else link.lanes
            link.VDF_cap1 = lanes * default_capacity_dict[link.link_type_name]
        else:
            link.VDF_cap1 = link.capacity

        if link.free_speed is None:
            free_speed = default_speed_dict[link.link_type_name]
        else:
            free_speed = link.free_speed
        link.VDF_FFTT1 = link.length / free_speed * 0.06




