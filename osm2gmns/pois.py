from .classes import *
import numpy as np


def parseRelations(relations, network):
    POI_relation_list = []
    for osm_relation in relations:
        relation = Relation()
        relation.osm_relation_id = osm_relation.attrib['id']

        for info in osm_relation:
            if info.tag == 'member':
                ref_id = info.attrib['ref']
                member_type = info.attrib['type']
                if member_type == 'node':
                    try:
                        relation.member_list.append(network.osm_node_dict[ref_id])
                    except KeyError:
                        printlog(f'ref node {ref_id} in relation {relation.osm_relation_id} is not defined', 'info')
                elif member_type == 'way':
                    try:
                        relation.member_list.append(network.osm_way_dict[ref_id])
                    except KeyError:
                        printlog(f'ref way {ref_id} in relation {relation.osm_relation_id} is not defined', 'info')
                elif member_type == 'relation':
                    pass
                else:
                    printlog(f'new member type at relation {relation.osm_relation_id}, {member_type}', 'warning')
                try:
                    relation.member_role_list.append(info.attrib['role'])
                except KeyError:
                    relation.member_role_list.append(None)

            elif info.tag == 'tag':
                if info.attrib['k'] == 'building':
                    relation.building = info.attrib['v']
                elif info.attrib['k'] == 'amenity':
                    relation.amenity = info.attrib['v']
                elif info.attrib['k'] == 'name':
                    relation.name = info.attrib['v']

        if relation.building or relation.amenity:
            POI_relation_list.append(relation)
    return POI_relation_list


def POIFromWay(POI_way_list):
    POI_list1 = []
    for way in POI_way_list:
        poi = POI()
        poi.osm_way_id = way.osm_way_id
        poi.name = way.name
        poi.building = way.building
        poi.amenity = way.amenity
        ln = getPolygonFromRefNodes(way.ref_node_list)
        if ln is None: continue
        poi.geometry = ln
        POI_list1.append(poi)
    return POI_list1


def POIFromRelation(POI_relation_list):
    POI_list2 = []
    for relation in POI_relation_list:
        poi = POI()
        poi.osm_relation_id = relation.osm_relation_id
        poi.name = relation.name
        poi.building = relation.building
        poi.amenity = relation.amenity
        polygon_list = []
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
                        combined_ref_node_list = m_ref_node_list + list(reversed(member.ref_node_list[1:]))
                    elif m_ref_node_list[0] is member.ref_node_list[0]:
                        combined_ref_node_list = list(reversed(m_ref_node_list)) + member.ref_node_list[1:]
                    elif m_ref_node_list[0] is member.ref_node_list[-1]:
                        combined_ref_node_list = list(reversed(m_ref_node_list)) + list(reversed(member.ref_node_list[1:]))

                    if combined_ref_node_list:
                        if combined_ref_node_list[0] is combined_ref_node_list[-1]:
                            poly = getPolygonFromRefNodes(combined_ref_node_list)
                            if poly is not None: polygon_list.append(poly)
                            m_ref_node_list = []
                        else:
                            m_ref_node_list = combined_ref_node_list
                    else:
                        poly = getPolygonFromRefNodes(m_ref_node_list)
                        if poly is not None: polygon_list.append(poly)
                        if member.ref_node_list[0] is member.ref_node_list[-1]:
                            poly = getPolygonFromRefNodes(m_ref_node_list)
                            if poly is not None: polygon_list.append(poly)
                            m_ref_node_list = []
                        else:
                            m_ref_node_list = member.ref_node_list
                else:
                    if member.ref_node_list[0] is member.ref_node_list[-1]:
                        poly = getPolygonFromRefNodes(member.ref_node_list)
                        if poly is not None: polygon_list.append(poly)
                    else:
                        m_ref_node_list = member.ref_node_list
            else:
                printlog(f'node member detected at building {relation.osm_relation_id}', 'warning')

        if m_ref_node_list:
            poly = getPolygonFromRefNodes(m_ref_node_list)
            if poly is not None: polygon_list.append(poly)

        if len(polygon_list) == 0: continue
        poi.geometry = geometry.MultiPolygon(polygon_list)
        POI_list2.append(poi)
    return POI_list2


def generatePOIs(POI_way_list,relations, network):
    POI_list1 = POIFromWay(POI_way_list)

    POI_relation_list = parseRelations(relations, network)
    POI_list2 = POIFromRelation(POI_relation_list)

    POI_list = POI_list1 + POI_list2

    max_poi_id = network.max_poi_id
    for poi in POI_list:
        poi.poi_id = max_poi_id
        max_poi_id += 1
    network.max_poi_id = max_poi_id
    return POI_list


def findNearestNode(network):
    coord_list = []
    idx_to_node_dict = {}
    for idx, (node_id, node) in enumerate(network.node_dict.items()):
        coord_list.append((node.geometry.x, node.geometry.y))
        idx_to_node_dict[idx] = node
    coord_array = np.array(coord_list)

    for poi in network.POI_list:
        coord = np.array((poi.geometry.centroid.x,poi.geometry.centroid.y))
        coord_diff = coord_array - coord
        coord_diff_square = np.power(coord_diff,2)
        coord_diff_sum_square = coord_diff_square.sum(axis=1)
        distance = np.sqrt(coord_diff_sum_square)
        idx = np.argmin(distance)
        poi.nearest_node = idx_to_node_dict[idx]


def createConnector(from_node, to_node, link_id):
    link = Link()
    # link.osm_way_id = way.osm_way_id
    link.link_id = link_id
    # link.name = way.name
    link.link_type_name = 'connector'
    link.link_type = link_type_no_dict[link.link_type_name]
    link.free_speed = default_speed_dict[link.link_type_name]
    link.allowed_uses = 'all'
    link.from_bidirectional_way = True
    link.lanes_list = [default_lanes_dict[link.link_type_name]]
    link.lanes = link.lanes_list[0]
    link.from_node = from_node
    link.to_node = to_node
    link.from_node.outgoing_link_list.append(link)
    link.to_node.incoming_link_list.append(link)
    link.geometry = getLineFromRefNodes([link.from_node, link.to_node])
    link.calculateLength()
    return link


def addPOIs(network):
    for poi in network.POI_list:
        node = Node()
        node.node_id = network.max_node_id
        node.geometry = poi.geometry.centroid
        node.is_crossing = True
        node.poi_id = poi.poi_id
        network.node_dict[node.node_id] = node
        network.max_node_id += 1

        link1 = createConnector(node,poi.nearest_node,network.max_link_id)
        network.link_dict[link1.link_id] = link1
        network.max_link_id += 1
        link2 = createConnector(poi.nearest_node, node, network.max_link_id)
        network.link_dict[link2.link_id] = link2
        network.max_link_id += 1


def connectPOIWithNet(network):
    if len(network.POI_list) == 0:
        print('No POIs found in the network. Please set POIs=True when creating network from osm file')
        return

    findNearestNode(network)
    addPOIs(network)







