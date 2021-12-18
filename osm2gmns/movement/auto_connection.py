from osm2gmns.movement.util_mvmt import getLinkAngle
from enum import Enum

Direction = Enum('Direction', ('RIGHTMOST', 'LEFTMOST', 'FORWARD'))

class MainDirections:
    def __init__(self, parent, outgoing, available_lanes):
        pass

    def getStraightest(self):
        return 0

    def empty(self):
        pass

    def includes(self, d):
        pass



def _prepareLinkPriorities(current_link, outgoing, available_lanes):
    priorities = []
    main_directions = MainDirections(current_link, outgoing, available_lanes)
    dist = main_directions.getStraightest()
    if dist == -1:
        return priorities





    return 0


def _divideOnEdges(current_link, connected_links):
    available_lanes = list(range(current_link.lanes))
    priorities = _prepareLinkPriorities(current_link, connected_links, available_lanes)




def _getConnectedSorted(link):
    connected_link_list = []
    for outgoing_link in link.to_node.outgoing_link_list:
        # if outgoing_link in link.forbidden_outgoing_link_list:
        #     continue
        if outgoing_link.to_node is link.from_node:
            continue
        connected_link_list.append(outgoing_link)

    # no need to sort if empty or only with one element
    if len(connected_link_list) <= 1:
        return connected_link_list

    angle_dict = {}
    for connected_link in connected_link_list:
        angle_dict[connected_link] = getLinkAngle(link,connected_link)

    # direction: clockwise
    connected_link_list_sorted = sorted(connected_link_list, key=lambda x: angle_dict[x], reverse=True)
    return connected_link_list_sorted


def _computeLanes2Edges_(current_link):
    connected_links = _getConnectedSorted(current_link)
    if connected_links:
        _divideOnEdges(current_link, connected_links)


def _computeLanes2Edges(link_dict, processed_node_set):
    for link_id, link in link_dict.items():
        if link.to_node.node_id in processed_node_set:
            continue
        _computeLanes2Edges_(link)


def _computeLanes2Lanes(net):
    pass


def guessMovements(net, processed_node_set):
    _computeLanes2Edges(net.link_dict, processed_node_set)
    _computeLanes2Lanes(net)