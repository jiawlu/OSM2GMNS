from osm2gmns.movement.autoconintd import CAutoConnectorIntD
from osm2gmns.movement.autoconm import CAutoConnectorM
from osm2gmns.movement.util_mvmt import getMovementDescription, getMovementGeometry
from osm2gmns.networkclass.macronet import Movement
import osm2gmns.settings as og_settings


def _generateMovementsForOneNode(node, max_movement_id, GT):
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
            ib_lane_index_start = connection_list[ib_link_no][0][0]
            ib_lane_index_end = connection_list[ib_link_no][0][1]
            ob_lane_index_start = connection_list[ib_link_no][1][0]
            ob_lane_index_end = connection_list[ib_link_no][1][1]
            number_of_lanes = ib_lane_index_end - ib_lane_index_start + 1

            mvmt = Movement(movement_id)
            mvmt.node = node
            mvmt.ib_link = ib_link
            mvmt.ob_link = ob_link
            mvmt.start_ib_lane_seq_no, mvmt.end_ib_lane_seq_no = ib_lane_index_start, ib_lane_index_end
            mvmt.start_ob_lane_seq_no, mvmt.end_ob_lane_seq_no = ob_lane_index_start, ob_lane_index_end
            mvmt.start_ib_lane, mvmt.end_ib_lane = ib_link.outgoing_lane_indices[ib_lane_index_start], ib_link.outgoing_lane_indices[ib_lane_index_end]
            mvmt.start_ob_lane, mvmt.end_ob_lane = ob_link.incoming_lane_indices[ob_lane_index_start], ob_link.incoming_lane_indices[ob_lane_index_end]
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
                ib_lane_index_start = connection_list[ob_link_no][0][0]
                ib_lane_index_end = connection_list[ob_link_no][0][1]
                ob_lane_index_start = connection_list[ob_link_no][1][0]
                ob_lane_index_end = connection_list[ob_link_no][1][1]
                number_of_lanes = ib_lane_index_end - ib_lane_index_start + 1

                mvmt = Movement(movement_id)
                mvmt.node = node
                mvmt.ib_link = ib_link
                mvmt.ob_link = ob_link
                mvmt.start_ib_lane_seq_no, mvmt.end_ib_lane_seq_no = ib_lane_index_start, ib_lane_index_end
                mvmt.start_ob_lane_seq_no, mvmt.end_ob_lane_seq_no = ob_lane_index_start, ob_lane_index_end
                mvmt.start_ib_lane, mvmt.end_ib_lane = ib_link.outgoing_lane_indices[ib_lane_index_start], ib_link.outgoing_lane_indices[ib_lane_index_end]
                mvmt.start_ob_lane, mvmt.end_ob_lane = ob_link.incoming_lane_indices[ob_lane_index_start], ob_link.incoming_lane_indices[ob_lane_index_end]
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


def validateUserInputMovements(network):
    for movement in network.user_input_movement_list:
        ib_link, ob_link = movement.ib_link, movement.ob_link

        if movement.start_ib_lane not in ib_link.outgoing_lane_indices:
            print(f'WARNING: start_ib_lane of movement {movement.movement_id} does not belong to ib_link {ib_link.link_id} outgoing lane indices {ib_link.outgoing_lane_indices}')
            continue
        start_ib_lane_seq_no = ib_link.outgoing_lane_indices.index(movement.start_ib_lane)

        if movement.end_ib_lane not in ib_link.outgoing_lane_indices:
            print(f'WARNING: end_ib_lane of movement {movement.movement_id} does not belong to ib_link {ib_link.link_id} outgoing lane indices {ib_link.outgoing_lane_indices}')
            continue
        end_ib_lane_seq_no = ib_link.outgoing_lane_indices.index(movement.end_ib_lane)

        if movement.start_ob_lane not in ob_link.incoming_lane_indices:
            print(f'WARNING: start_ob_lane of movement {movement.movement_id} does not belong to ob_link {ob_link.link_id} incoming lane indices {ob_link.incoming_lane_indices}')
            continue
        start_ob_lane_seq_no = ob_link.incoming_lane_indices.index(movement.start_ob_lane)

        if movement.end_ob_lane not in ob_link.incoming_lane_indices:
            print(f'WARNING: end_ob_lane of movement {movement.movement_id} does not belong to ob_link {ob_link.link_id} incoming lane indices {ob_link.incoming_lane_indices}')
            continue
        end_ob_lane_seq_no = ob_link.incoming_lane_indices.index(movement.end_ob_lane)

        ib_lanes, ob_lanes = end_ib_lane_seq_no - start_ib_lane_seq_no + 1, end_ob_lane_seq_no - start_ob_lane_seq_no + 1

        if ib_lanes < ob_lanes:
            end_ob_lane_seq_no -= (ob_lanes - ib_lanes)
            end_ob_lane = ob_link.incoming_lane_indices[end_ob_lane_seq_no]
            print(f'WARNING: movement {movement.movement_id} - number of ib lanes ({ib_lanes}) is less than that of ob lanes ({ob_lanes}), end_ob_lane is changed to {end_ob_lane}')
            movement.lanes = ib_lanes
        elif ib_lanes > ob_lanes:
            end_ib_lane_seq_no -= (ib_lanes - ob_lanes)
            end_ib_lane = ib_link.outgoing_lane_indices[end_ib_lane_seq_no]
            print(f'WARNING: movement {movement.movement_id} - number of ib lanes ({ib_lanes}) is more than that of ob lanes ({ob_lanes}), end_ib_lane is changed to {end_ib_lane}')
            movement.lanes = ob_lanes
        else:
            movement.lanes = ib_lanes

        movement.end_ib_lane, movement.start_ib_lane_seq_no, movement.end_ib_lane_seq_no = movement.end_ib_lane, start_ib_lane_seq_no, end_ib_lane_seq_no
        movement.end_ob_lane, movement.start_ob_lane_seq_no, movement.end_ob_lane_seq_no = movement.end_ob_lane, start_ob_lane_seq_no, end_ob_lane_seq_no
        movement.node.movement_list.append(movement)


def generateMovements(network):
    """
    Use osm2gmns built-in methods to generate movements for each node (intersection) in a network

    Parameters
    ----------
    network: Network
        an osm2gmns Network object

    Returns
    -------
    None
    """

    if og_settings.verbose:
        print('Generating Movements')

    if not network.complete_link_lane_info:
        print('WARNING: Movement generation will be skipped because some links do not have lanes information.\n'
              '         If the network is parsed from a OSM file, set "default_lanes" as "True" when parsing networks to assign default lanes for links without lanes information.\n'
              '         If the network is loaded from a CSV file, make sure all links have lanes information before loading the network.')
        return

    for _, link in network.link_dict.items():
        link.linkLaneListFromSegment()

    validateUserInputMovements(network)

    max_movement_id = network.max_movement_id
    for node_id, node in network.node_dict.items():

        if node.movement_list:
            continue

        _generateMovementsForOneNode(node, max_movement_id, network.GT)
        max_movement_id += len(node.movement_list)

    network.max_movement_id = max_movement_id
