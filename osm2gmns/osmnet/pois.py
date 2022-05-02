from osm2gmns.networkclass.macronet import Node, Link, POI
from osm2gmns.osmnet.osmclasses import Way, Relation
from osm2gmns.utils.util import getLogger
from osm2gmns.utils.util_geo import getLineFromNodes, getPolygonFromNodes
import osm2gmns.settings as og_settings
from shapely import geometry
import numpy as np
import random



def _parseRelations(relations, network):
    POI_relation_list = []
    for osm_relation in relations:
        relation = Relation()
        relation.osm_relation_id = str(osm_relation.id)

        for member_id, member_type, member_role in osm_relation.members:
            member_id_str = str(member_id)
            member_type_lc = member_type.lower()
            if member_type_lc == 'node':
                try:
                    relation.member_list.append(network.osm_node_dict[member_id_str])
                except KeyError:
                    logger = getLogger()
                    if logger: logger.info(f'ref node {member_id} in relation {relation.osm_relation_id} is not defined')
            elif member_type_lc == 'way':
                try:
                    relation.member_list.append(network.osm_way_dict[member_id_str])
                except KeyError:
                    logger = getLogger()
                    if logger: logger.info(f'ref way {member_id} in relation {relation.osm_relation_id} is not defined')
            elif member_type_lc == 'relation':
                pass
            else:
                logger = getLogger()
                if logger: logger.warning(f'new member type at relation {relation.osm_relation_id}, {member_type}')

            relation.member_role_list.append(member_role)

        tags = osm_relation.tags
        if 'building' in tags.keys():
            relation.building = tags['building']
        if 'amenity' in tags.keys():
            relation.amenity = tags['amenity']
        if 'name' in tags.keys():
            relation.name = tags['name']

        if relation.building or relation.amenity:
            POI_relation_list.append(relation)
    return POI_relation_list


def _POIFromWay(POI_way_list, net_bound):
    POI_list1 = []
    for way in POI_way_list:
        poly, poly_xy = getPolygonFromNodes(way.ref_node_list)
        if poly is None: continue
        if poly.disjoint(net_bound): continue

        poi = POI()
        poi.osm_way_id = way.osm_way_id
        poi.name = way.name
        poi.building = way.building
        poi.amenity = way.amenity
        poi.way = way.way_poi

        poi.geometry, poi.geometry_xy = poly, poly_xy
        lon, lat = poi.geometry.centroid.x, poi.geometry.centroid.y
        poi.centroid = geometry.Point((round(lon,og_settings.lonlat_coord_precision),round(lat,og_settings.lonlat_coord_precision)))
        x, y = poi.geometry_xy.centroid.x, poi.geometry_xy.centroid.y
        poi.centroid_xy = geometry.Point((round(x,og_settings.local_coord_precision),round(y,og_settings.local_coord_precision)))
        POI_list1.append(poi)
    return POI_list1


def _POIFromRelation(POI_relation_list, net_bound):
    POI_list2 = []
    for relation in POI_relation_list:
        poi = POI()
        poi.osm_relation_id = relation.osm_relation_id
        poi.name = relation.name
        poi.building = relation.building
        poi.amenity = relation.amenity
        polygon_list = []
        polygon_list_xy = []
        number_of_members = len(relation.member_list)
        m_ref_node_list = []
        for m in range(number_of_members):
            member = relation.member_list[m]
            role = relation.member_role_list[m]
            if isinstance(member, Way):
                if role != 'outer': continue
                if m_ref_node_list:
                    combined_ref_node_list = []
                    if m_ref_node_list[-1] is member.ref_node_list[0]:
                        combined_ref_node_list = m_ref_node_list + member.ref_node_list[1:]
                    elif m_ref_node_list[-1] is member.ref_node_list[-1]:
                        combined_ref_node_list = m_ref_node_list + list(reversed(member.ref_node_list[:-1]))
                    elif m_ref_node_list[0] is member.ref_node_list[0]:
                        combined_ref_node_list = list(reversed(m_ref_node_list)) + member.ref_node_list[1:]
                    elif m_ref_node_list[0] is member.ref_node_list[-1]:
                        combined_ref_node_list = list(reversed(m_ref_node_list)) + list(reversed(member.ref_node_list[:-1]))

                    if combined_ref_node_list:
                        if combined_ref_node_list[0] is combined_ref_node_list[-1]:
                            poly, poly_xy = getPolygonFromNodes(combined_ref_node_list)
                            if poly is not None:
                                polygon_list.append(poly)
                                polygon_list_xy.append(poly_xy)
                            m_ref_node_list = []
                        else:
                            m_ref_node_list = combined_ref_node_list
                    else:
                        poly, poly_xy = getPolygonFromNodes(m_ref_node_list)
                        if poly is not None:
                            polygon_list.append(poly)
                            polygon_list_xy.append(poly_xy)
                        if member.ref_node_list[0] is member.ref_node_list[-1]:
                            poly, poly_xy = getPolygonFromNodes(m_ref_node_list)
                            if poly is not None:
                                polygon_list.append(poly)
                                polygon_list_xy.append(poly_xy)
                            m_ref_node_list = []
                        else:
                            m_ref_node_list = member.ref_node_list
                else:
                    if member.ref_node_list[0] is member.ref_node_list[-1]:
                        poly, poly_xy = getPolygonFromNodes(member.ref_node_list)
                        if poly is not None:
                            polygon_list.append(poly)
                            polygon_list_xy.append(poly_xy)
                    else:
                        m_ref_node_list = member.ref_node_list
            else:
                logger = getLogger()
                if logger: logger.warning(f'node member detected at building {relation.osm_relation_id}')

        if m_ref_node_list:
            poly, poly_xy = getPolygonFromNodes(m_ref_node_list)
            if poly is not None:
                polygon_list.append(poly)
                polygon_list_xy.append(poly_xy)

        if len(polygon_list) == 0:
            continue
        else:
            if len(polygon_list) == 1:
                poi.geometry = polygon_list[0]
                if poi.geometry.disjoint(net_bound): continue
                poi.geometry_xy = polygon_list_xy[0]
            else:
                disjoint = True
                for poly in polygon_list:
                    if not poly.disjoint(net_bound):
                        disjoint = False
                        break
                if disjoint: continue
                poi.geometry = geometry.MultiPolygon(polygon_list)
                poi.geometry_xy = geometry.MultiPolygon(polygon_list_xy)

            lon, lat = poi.geometry.centroid.x, poi.geometry.centroid.y
            poi.centroid = geometry.Point((round(lon, og_settings.lonlat_coord_precision), round(lat, og_settings.lonlat_coord_precision)))
            x, y = poi.geometry_xy.centroid.x, poi.geometry_xy.centroid.y
            poi.centroid_xy = geometry.Point((round(x, og_settings.local_coord_precision), round(y, og_settings.local_coord_precision)))

            POI_list2.append(poi)

    return POI_list2


def generatePOIs(POI_way_list, osm_relation_list, network, POI_percentage):
    if og_settings.verbose:
        print('    generating POIs')

    POI_list1 = _POIFromWay(POI_way_list, network.bounds)
    POI_list2 = _POIFromRelation(osm_relation_list, network.bounds)

    POI_list_ = POI_list1 + POI_list2
    if POI_percentage == 1:
        POI_list = POI_list_
    else:
        POI_list = random.sample(POI_list_,int(len(POI_list_)*POI_percentage))

    max_poi_id = network.max_poi_id
    for poi in POI_list:
        poi.poi_id = max_poi_id
        max_poi_id += 1
    network.max_poi_id = max_poi_id
    network.POI_list = POI_list


def _findNearestNode(network):
    coord_list = []
    idx_to_node_dict = {}
    for idx, (node_id, node) in enumerate(network.node_dict.items()):
        coord_list.append((node.geometry_xy.x, node.geometry_xy.y))
        idx_to_node_dict[idx] = node
    coord_array = np.array(coord_list)

    for poi in network.POI_list:
        coord = np.array((poi.centroid_xy.x,poi.centroid_xy.y))
        coord_diff = coord_array - coord
        coord_diff_square = np.power(coord_diff,2)
        coord_diff_sum_square = coord_diff_square.sum(axis=1)
        distance = np.sqrt(coord_diff_sum_square)
        idx = int(np.argmin(distance))
        poi.nearest_node = idx_to_node_dict[idx]


def _createConnector(from_node, to_node, link_id):
    link = Link(link_id)
    link.link_type_name = 'connector'
    link.link_type = og_settings.link_type_no_dict[link.link_type_name]
    link.free_speed = og_settings.default_speed_dict[link.link_type_name]
    link.allowed_uses = ['auto','bike','walk']
    link.from_bidirectional_way = True
    link.lanes_list = [og_settings.default_lanes_dict[link.link_type_name]]
    # link.lanes = link.lanes_list[0]
    link.from_node = from_node
    link.to_node = to_node
    link.from_node.outgoing_link_list.append(link)
    link.to_node.incoming_link_list.append(link)
    link.geometry, link.geometry_xy = getLineFromNodes([link.from_node, link.to_node])
    return link


def _addPOIs(network):
    for poi in network.POI_list:
        node = Node(network.max_node_id)
        node.geometry = poi.geometry.centroid
        node.geometry_xy = poi.geometry_xy.centroid
        node.is_crossing = True
        node.poi_id = poi.poi_id
        network.node_dict[node.node_id] = node
        network.max_node_id += 1

        link1 = _createConnector(node,poi.nearest_node,network.max_link_id)
        network.link_dict[link1.link_id] = link1
        network.max_link_id += 1
        link2 = _createConnector(poi.nearest_node, node, network.max_link_id)
        network.link_dict[link2.link_id] = link2
        network.max_link_id += 1


def connectPOIWithNet(network):
    """
    Connect POIs with the traffic network. Specifically, for each POI, osm2gmns will build a bi-directional connector to connect the POI
    with its nearest node in the traffic network

    Parameters
    ----------
    network: Network
        an osm2gmns Network object

    Returns
    -------
    None
    """
    if len(network.POI_list) == 0:
        print('No POIs found in the network. Please set POIs=True when creating network from osm file')
        return

    _findNearestNode(network)
    _addPOIs(network)







