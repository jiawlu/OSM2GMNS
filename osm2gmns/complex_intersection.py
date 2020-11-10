def identifyComplexIntersections(network, int_buffer):
    network.complex_intersection_identified = True

    link_list = sorted(network.link_set, key=lambda x: x.link_no)
    group_list = []
    group_status = []
    for link in link_list:
        if link.length > int_buffer: continue
        if not('traffic_signals' in link.from_node.osm_highway and 'traffic_signals' in link.to_node.osm_highway): continue
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





