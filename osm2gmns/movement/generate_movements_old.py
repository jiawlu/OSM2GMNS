from osm2gmns.movement.autoconintd import CAutoConnectorIntD
from osm2gmns.movement.autoconm import CAutoConnectorM
from osm2gmns.movement.util_mvmt import getMovementDescription, getMovementGeometry
from osm2gmns.networkclass.macronet import Movement
import osm2gmns.settings as og_settings


def generateMovementsForOneNode(node, max_movement_id, GT):
    number_of_incoming_links = len(node.incoming_link_list)
    number_of_outgoing_links = len(node.outgoing_link_list)

    if number_of_incoming_links == 0 or number_of_outgoing_links == 0: return

    movement_id = max_movement_id

    if number_of_outgoing_links == 1:
        # merge
        ob_link = node.outgoing_link_list[0]
        ib_link_list = []
        for ib_link in node.incoming_link_list:
            if ib_link.from_node.node_id != ob_link.to_node.node_id:
                ib_link_list.append(ib_link)

        if len(ib_link_list) == 0: return

        CAutoConnectorM.ob_link, CAutoConnectorM.ib_link_list = ob_link, ib_link_list
        connection_list = CAutoConnectorM.buildConnector()

        for ib_link_no, ib_link in enumerate(ib_link_list):
            ib_lane_index_start = connection_list[ib_link_no][0][0] + 1
            ib_lane_index_end = connection_list[ib_link_no][0][1] + 1
            ob_lane_index_start = connection_list[ib_link_no][1][0] + 1
            ob_lane_index_end = connection_list[ib_link_no][1][1] + 1
            number_of_lanes = ib_lane_index_end - ib_lane_index_start + 1

            mvmt = Movement(movement_id)
            mvmt.node = node
            mvmt.ib_link = ib_link
            mvmt.ob_link = ob_link
            mvmt.start_ib_lane, mvmt.end_ib_lane = ib_lane_index_start, ib_lane_index_end
            mvmt.start_ob_lane, mvmt.end_ob_lane = ob_lane_index_start, ob_lane_index_end
            mvmt.lanes = number_of_lanes
            mvmt_txt_id, mvmt_type = getMovementDescription(ib_link, ob_link)
            mvmt.mvmt_txt_id = mvmt_txt_id
            mvmt.type = mvmt_type
            mvmt.geometry_xy = getMovementGeometry(ib_link, ob_link)
            mvmt.geometry = GT.geo_to_latlon(mvmt.geometry_xy)
            mvmt.generated_by_osm2gmns = True

            if node.ctrl_type == 1: mvmt.ctrl_type = 'signal'               # todo: check ctrl_type
            mvmt.allowed_uses = ib_link.allowed_uses
            node.movement_list.append(mvmt)
            movement_id += 1
    else:
        # diverge and intersections
        for ib_link in node.incoming_link_list:
            ob_link_list = []
            for ob_link in node.outgoing_link_list:
                if ib_link.from_node.node_id != ob_link.to_node.node_id:
                    ob_link_list.append(ob_link)

            if len(ob_link_list) == 0: continue

            CAutoConnectorIntD.ib_link, CAutoConnectorIntD.ob_link_list = ib_link, ob_link_list
            connection_list = CAutoConnectorIntD.buildConnector()

            for ob_link_no, ob_link in enumerate(ob_link_list):
                ib_lane_index_start = connection_list[ob_link_no][0][0] + 1
                ib_lane_index_end = connection_list[ob_link_no][0][1] + 1
                ob_lane_index_start = connection_list[ob_link_no][1][0] + 1
                ob_lane_index_end = connection_list[ob_link_no][1][1] + 1
                number_of_lanes = ib_lane_index_end - ib_lane_index_start + 1

                mvmt = Movement(movement_id)
                mvmt.node = node
                mvmt.ib_link = ib_link
                mvmt.ob_link = ob_link
                mvmt.start_ib_lane, mvmt.end_ib_lane = ib_lane_index_start, ib_lane_index_end
                mvmt.start_ob_lane, mvmt.end_ob_lane = ob_lane_index_start, ob_lane_index_end
                mvmt.lanes = number_of_lanes
                mvmt_txt_id, mvmt_type = getMovementDescription(ib_link, ob_link)
                mvmt.mvmt_txt_id = mvmt_txt_id
                mvmt.type = mvmt_type
                mvmt.geometry_xy = getMovementGeometry(ib_link, ob_link)
                mvmt.geometry = GT.geo_to_latlon(mvmt.geometry_xy)
                mvmt.generated_by_osm2gmns = True

                if node.ctrl_type == 1: mvmt.ctrl_type = 'signal'
                mvmt.allowed_uses = ib_link.allowed_uses
                node.movement_list.append(mvmt)
                movement_id += 1


def generateMovements(network):
    network.movement_generated = True

    if og_settings.verbose:
        print('Generating Movements')

    max_movement_id = network.max_movement_id
    first_intersection_lacking_lanes = True

    for node_id, node in network.node_dict.items():

        if node.movement_list:
            continue

        lack_lanes = False
        for link in node.outgoing_link_list + node.incoming_link_list:
            if link.lanes is None:
                lack_lanes = True
                break

        if lack_lanes:
            if first_intersection_lacking_lanes:
                print('WARNING: Movement generation will be skipped at some intersections due to the lack of link lanes information.\n'
                      '         Set "default_lanes" as "True" when parsing networks to assign default lanes for links without lanes information.')
                first_intersection_lacking_lanes = False
            continue

        generateMovementsForOneNode(node, max_movement_id, network.GT)
        max_movement_id += len(node.movement_list)

    network.max_movement_id = max_movement_id



