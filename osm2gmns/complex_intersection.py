# -*- coding:utf-8 -*-
# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2020/11/3 20:21
# @desc         [script description]



def identifyComplexIntersections(network, int_buffer):
    network.complex_intersection_identified = True

    complex_intersection_set = set()
    for link in network.link_set:
        if link.length > int_buffer: continue
        if not('traffic_signals' in link.from_node.node_type and 'traffic_signals' in link.to_node.node_type): continue
        new_group = (link.from_node, link.to_node)
        accessible_group_set = set()
        for node_group in complex_intersection_set:
            if (link.from_node in node_group) or (link.to_node in node_group):
                accessible_group_set.add(node_group)

        for node_group in accessible_group_set:
            new_group += node_group
            complex_intersection_set.remove(node_group)
        new_group = tuple(set(new_group))
        complex_intersection_set.add(new_group)

    network.complex_intersection_set = complex_intersection_set
