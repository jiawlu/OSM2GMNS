# -*- coding:utf-8 -*-
# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2020/11/3 22:37
# @desc         [script description]

from .classes import *


def checkTpologyForTwoDegreeNodes(node):
    ib_link, ob_link = node.incoming_link_list[0], node.outgoing_link_list[0]
    # if not (ib_link.valid and ob_link.valid): return False
    if ib_link.from_node is ob_link.to_node: return False
    ib_link.ob_comb_link = ob_link
    return True


def checkTpologyForFourDegreeNodes(node):
    for ib_link in node.incoming_link_list:
        # if not ib_link.valid: return False
        for ob_link in node.outgoing_link_list:
            # if not ob_link.valid: return False
            if ib_link.from_node is not ob_link.to_node:
                if ib_link.ob_comb_link is None:
                    ib_link.ob_comb_link = ob_link
                else:
                    return False
    for ib_link in node.incoming_link_list:
        if ib_link.ob_comb_link is None: return False
    return True


def getNameForTheCombinedLink(ib_link):
    if ib_link.name == ib_link.ob_comb_link.name:
        return ib_link.name
    elif ib_link.name == '' and ib_link.ob_comb_link.name != '':
        return ib_link.ob_comb_link.name
    elif ib_link.name != '' and ib_link.ob_comb_link.name == '':
        return ib_link.name
    else:
        return None


def getLinktypeForTheCombinedLink(ib_link):
    if ib_link.link_type == ib_link.ob_comb_link.link_type:
        return ib_link.link_type
    else:
        return None


def getSpeedForTheCombinedLink(ib_link):
    if ib_link.free_speed == ib_link.ob_comb_link.free_speed:
        return ib_link.free_speed
    elif ib_link.free_speed == -1 and ib_link.ob_comb_link.free_speed != -1:
        return ib_link.ob_comb_link.free_speed
    elif ib_link.free_speed != -1 and ib_link.ob_comb_link.free_speed == -1:
        return ib_link.free_speed
    else:
        return None


def newLinkFromLinks(up_link, down_link, new_link_attr_dict):
    link = Link()
    link.osm_way_id = f'{up_link.osm_way_id};{down_link.osm_way_id}'
    link.name = new_link_attr_dict['name']
    link.link_type = new_link_attr_dict['link_type']
    link.free_speed = new_link_attr_dict['free_speed']

    # self.ref_node_list = up_link.ref_node_list + down_link.ref_node_list[1:]
    link.from_node = up_link.from_node
    link.to_node = down_link.to_node
    link.from_node.outgoing_link_list.remove(up_link)
    link.to_node.incoming_link_list.remove(down_link)
    link.from_node.outgoing_link_list.append(link)
    link.to_node.incoming_link_list.append(link)

    # self.geometry_str = up_link.geometry_str[:-1] + ', ' + down_link.geometry_str[12:]
    link.geometry_point_list = up_link.geometry_point_list + down_link.geometry_point_list[1:]
    link.getGeometryStr()
    link.length = up_link.length + down_link.length

    up_lanes_list, down_lanes_list = up_link.lanes_list, down_link.lanes_list
    new_down_link_lanes_change_point_list = [point + up_link.length for point in down_link.lanes_change_point_list]
    if up_lanes_list[-1] == down_lanes_list[0]:
        link.lanes_list = up_lanes_list + down_lanes_list[1:]
        link.lanes_change_point_list = up_link.lanes_change_point_list + new_down_link_lanes_change_point_list
    else:
        link.lanes_list = up_lanes_list + down_lanes_list
        link.lanes_change_point_list = up_link.lanes_change_point_list + [up_link.length] + new_down_link_lanes_change_point_list
    link.lanes = link.lanes_list[0]
    return link


def combLinks(network):

    removal_node_set = set()
    removal_link_set = set()

    for node in network.node_set:
        if 'traffic_signals' in node.node_type: continue                         # todo: check node type before eliminating

        # check topology
        if len(node.incoming_link_list) == 1 and len(node.outgoing_link_list) == 1:
            topology_flag = checkTpologyForTwoDegreeNodes(node)
        elif len(node.incoming_link_list) == 2 and len(node.outgoing_link_list) == 2:
            topology_flag = checkTpologyForFourDegreeNodes(node)
        else:
            topology_flag = False
        if not topology_flag: continue

        # check link attributes, name, link_type, lanes, free_speed
        attr_flag = True
        new_link_attr_dict_list = []

        for ib_link in node.incoming_link_list:
            # if ib_link.ob_comb_link is None: continue

            name = getNameForTheCombinedLink(ib_link)
            if name is None:
                attr_flag = False
                break

            link_type = getLinktypeForTheCombinedLink(ib_link)
            if link_type is None:
                attr_flag = False
                break

            free_speed = getSpeedForTheCombinedLink(ib_link)
            if free_speed is None:
                attr_flag = False
                break

            new_link_attr_dict_list.append({'name': name, 'link_type': link_type, 'free_speed': free_speed})

        if not attr_flag: continue

        node.valid = False
        removal_node_set.add(node)
        for ib_link_idx, ib_link in enumerate(node.incoming_link_list):
            ob_comb_link = ib_link.ob_comb_link
            new_link = newLinkFromLinks(ib_link, ob_comb_link, new_link_attr_dict_list[ib_link_idx])
            network.link_set.add(new_link)
            ib_link.valid = False
            ob_comb_link.valid = False
            removal_link_set.add(ib_link)
            removal_link_set.add(ob_comb_link)

    for node in removal_node_set: network.node_set.remove(node)
    for link in removal_link_set: network.link_set.remove(link)


def generateSegments(network):
    for link in network.link_set:
        number_of_lanes_change_points = len(link.lanes_change_point_list)
        if number_of_lanes_change_points == 0: continue

        for i in range(number_of_lanes_change_points-1):
            segment = Segment()
            segment.link = link
            segment.start_lr = link.lanes_change_point_list[i]
            segment.end_lr = link.lanes_change_point_list[i+1]
            segment.l_lanes_added = link.lanes_list[i+1] - link.lanes
            network.segment_set.add(segment)

        segment = Segment()
        segment.link = link
        segment.start_lr = link.lanes_change_point_list[-1]
        segment.end_lr = link.length
        segment.l_lanes_added = link.lanes_list[-1] - link.lanes
        network.segment_set.add(segment)


def simplifyNetwork(network):
    network.simplified = True
    combLinks(network)
    generateSegments(network)
