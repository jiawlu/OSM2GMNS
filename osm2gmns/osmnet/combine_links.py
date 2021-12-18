from osm2gmns.networkclass.macronet import Link
import osm2gmns.settings as og_settings
from shapely import ops


def _checkLinkAttr(ib_link, ob_link):
    if ib_link.name != ob_link.name: return False
    if ib_link.link_type != ob_link.link_type: return False
    if ib_link.is_link != ob_link.is_link: return False
    if ib_link.free_speed != ob_link.free_speed: return False
    if ib_link.allowed_uses != ob_link.allowed_uses: return False

    if len(ib_link.lanes_list) > 1 or len(ob_link.lanes_list) > 1: return False
    if ib_link.lanes != ob_link.lanes: return False

    if ib_link.from_bidirectional_way != ob_link.from_bidirectional_way: return False
    if ib_link.ctrl_type != ob_link.ctrl_type: return False
    return True


def _newLinkFromLinks(link_id, up_link, down_link):
    link = Link(link_id)
    link.osm_way_id = f'{up_link.osm_way_id};{down_link.osm_way_id}'
    link.name = up_link.name
    link.link_class = up_link.link_class
    link.link_type_name = up_link.link_type_name
    link.link_type = up_link.link_type
    link.is_link = up_link.is_link
    link.free_speed = up_link.free_speed
    link.capacity = up_link.capacity
    link.allowed_uses = up_link.allowed_uses
    link.from_bidirectional_way = up_link.from_bidirectional_way
    link.lanes_list = up_link.lanes_list
    link.ctrl_type = up_link.ctrl_type

    link.from_node = up_link.from_node
    link.to_node = down_link.to_node
    link.from_node.outgoing_link_list.remove(up_link)
    link.to_node.incoming_link_list.remove(down_link)
    link.from_node.outgoing_link_list.append(link)
    link.to_node.incoming_link_list.append(link)

    link.geometry = ops.linemerge([up_link.geometry, down_link.geometry])
    link.geometry_xy = ops.linemerge([up_link.geometry_xy, down_link.geometry_xy])
    return link


def _combLinks(network):

    removal_node_set = set()
    removal_link_set = set()

    for node_id, node in network.node_dict.items():
        if node.osm_highway and 'traffic_signals' in node.osm_highway: continue

        if len(node.incoming_link_list) != 1 or len(node.outgoing_link_list) != 1:
            continue

        ib_link, ob_link = node.incoming_link_list[0], node.outgoing_link_list[0]
        if ib_link.from_node is ob_link.to_node:
            continue

        if (ib_link.ctrl_type is not None) or (ob_link.ctrl_type is not None):
            continue

        if not _checkLinkAttr(ib_link, ob_link):
            continue

        new_link = _newLinkFromLinks(network.max_link_id, ib_link, ob_link)
        network.link_dict[new_link.link_id] = new_link
        network.max_link_id += 1

        removal_node_set.add(node.node_id)
        removal_link_set.add(ib_link.link_id)
        removal_link_set.add(ob_link.link_id)

    for node_id in removal_node_set: del network.node_dict[node_id]
    for link_id in removal_link_set: del network.link_dict[link_id]



def combineShortLinks(network):
    if og_settings.verbose:
        print('    combining links')

    number_of_nodes_before_combination = len(network.node_dict)
    number_of_links_before_combination = len(network.link_dict)

    _combLinks(network)

    if og_settings.verbose:
        print(f'    link combination finished. before: {number_of_nodes_before_combination} nodes {number_of_links_before_combination} links, after {len(network.node_dict)} nodes {len(network.link_dict)} links')

