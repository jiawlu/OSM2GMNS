from .autoconintd import *
from .autoconm import *
from .classes import Movement
from .util import linexy2lonlat
from shapely import geometry


_indent = 8.0

def _getMovementStr(ib_start, ib_end, ob_end):
    angle_ib = math.atan2(ib_end[1] - ib_start[1], ib_end[0] - ib_start[0])
    if -0.75 * math.pi <= angle_ib < -0.25 * math.pi:
        direction = 'SB'
    elif -0.25 * math.pi <= angle_ib < 0.25 * math.pi:
        direction = 'EB'
    elif 0.25 * math.pi <= angle_ib < 0.75 * math.pi:
        direction = 'NB'
    else:
        direction = 'WB'

    angle_ob = math.atan2(ob_end[1] - ib_end[1], ob_end[0] - ib_end[0])
    # angle_ob = math.atan2(ob_end[1] - ob_start[1], ob_end[0] - ob_start[0])
    angle = angle_ob - angle_ib
    if angle < -1 * math.pi:
        angle += 2 * math.pi
    if angle > math.pi:
        angle -= 2 * math.pi

    if -0.25 * math.pi <= angle <= 0.25 * math.pi:
        mvmt = 'T'
        mvmt_type = 'thru'
    elif angle < -0.25 * math.pi:
        mvmt = 'R'
        mvmt_type = 'right'
    elif angle <= 0.75 * math.pi:
        mvmt = 'L'
        mvmt_type = 'left'
    else:
        mvmt = 'U'
        mvmt_type = 'uturn'

    mvmt_str = direction + mvmt
    return mvmt_str, mvmt_type


def _generateMovementsForOneNode(node):
    number_of_incoming_links = len(node.incoming_link_list)
    number_of_outgoing_links = len(node.outgoing_link_list)

    if number_of_incoming_links == 0 or number_of_outgoing_links == 0: return []
    if number_of_incoming_links == 1 and number_of_outgoing_links == 1: return []
    if number_of_incoming_links == 2 and number_of_outgoing_links == 2: return []

    mvmt_list = []

    if number_of_outgoing_links == 1:
        # merge
        ob_link = node.outgoing_link_list[0]
        ib_link_list = []
        for ib_link in node.incoming_link_list:
            if ib_link.from_node.node_id != ob_link.to_node.node_id:
                ib_link_list.append(ib_link)

        if len(ib_link_list) == 0: return []

        CAutoConnectorM.ob_link, CAutoConnectorM.ib_link_list = ob_link, ib_link_list
        connection_list = CAutoConnectorM.buildConnector()

        for ib_link_no, ib_link in enumerate(ib_link_list):
            ib_lane_index_start = connection_list[ib_link_no][0][0] + 1
            ib_lane_index_end = connection_list[ib_link_no][0][1] + 1
            ob_lane_index_start = connection_list[ib_link_no][1][0] + 1
            ob_lane_index_end = connection_list[ib_link_no][1][1] + 1

            ib_lane = '|'.join(list(map(str,range(ib_lane_index_start, ib_lane_index_end+1))))
            ob_lane = '|'.join(list(map(str, range(ob_lane_index_start, ob_lane_index_end + 1))))
            number_of_lanes = ib_lane_index_end - ib_lane_index_start + 1

            ib_start, ib_end = ib_link.geometry_xy.coords[0], ib_link.geometry_xy.coords[-1]
            ob_start, ob_end = ob_link.geometry_xy.coords[0], ob_link.geometry_xy.coords[-1]
            movement_str, mvmt_type = _getMovementStr(ib_start, ib_end, ob_end)

            mvmt = Movement()
            mvmt.node = node
            mvmt.ib_link = ib_link
            mvmt.ib_lane = ib_lane
            mvmt.ob_link = ob_link
            mvmt.ob_lane = ob_lane
            mvmt.start_ib_lane, mvmt.end_ib_lane = ib_lane_index_start, ib_lane_index_end
            mvmt.start_ob_lane, mvmt.end_ob_lane = ob_lane_index_start, ob_lane_index_end
            if number_of_lanes == 1:
                mvmt.end_ib_lane = ''
                mvmt.end_ob_lane = ''
            mvmt.lanes = number_of_lanes
            mvmt.movement_str = movement_str
            mvmt.type = mvmt_type
            if node.ctrl_type == 1: mvmt.ctrl_type = 'signal'
            mvmt.allowed_uses = ib_link.allowed_uses
            mvmt_list.append(mvmt)
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

                ib_lane = '|'.join(list(map(str, range(ib_lane_index_start, ib_lane_index_end + 1))))
                ob_lane = '|'.join(list(map(str, range(ob_lane_index_start, ob_lane_index_end + 1))))
                number_of_lanes = ib_lane_index_end - ib_lane_index_start + 1

                ib_start, ib_end = ib_link.geometry_xy.coords[0], ib_link.geometry_xy.coords[-1]
                ob_start, ob_end = ob_link.geometry_xy.coords[0], ob_link.geometry_xy.coords[-1]
                movement_str, mvmt_type = _getMovementStr(ib_start, ib_end, ob_end)

                mvmt = Movement()
                mvmt.node = node
                mvmt.ib_link = ib_link
                mvmt.ib_lane = ib_lane
                mvmt.ob_link = ob_link
                mvmt.ob_lane = ob_lane
                mvmt.start_ib_lane, mvmt.end_ib_lane = ib_lane_index_start, ib_lane_index_end
                mvmt.start_ob_lane, mvmt.end_ob_lane = ob_lane_index_start, ob_lane_index_end
                if number_of_lanes == 1:
                    mvmt.end_ib_lane = ''
                    mvmt.end_ob_lane = ''
                mvmt.lanes = number_of_lanes
                mvmt.movement_str = movement_str
                mvmt.type = mvmt_type
                if node.ctrl_type == 1: mvmt.ctrl_type = 'signal'
                mvmt.allowed_uses = ib_link.allowed_uses
                mvmt_list.append(mvmt)

    return mvmt_list


def _movementGeometry(net):
    central_lon, northern = net.central_lon, net.northern

    for movement in net.movement_list:
        ib_geometry_xy = movement.ib_link.geometry_xy
        ib_indent = _indent if ib_geometry_xy.length > _indent else ib_geometry_xy.length / 2
        ib_point = ib_geometry_xy.interpolate(-1 * ib_indent)

        ob_geometry_xy = movement.ob_link.geometry_xy
        ob_indent = _indent if ob_geometry_xy.length > _indent else ob_geometry_xy.length / 2
        ob_point = ob_geometry_xy.interpolate(ob_indent)

        movement.geometry_xy = geometry.LineString([ib_point, ob_point])
        movement.geometry = linexy2lonlat(movement.geometry_xy, central_lon, northern)


def generateMovements(net):
    if not net.complete_highway_lanes:
        print('Movement generation needs complete link lanes information.\n'
              'Argument "default_lanes" must be set as "True" when parsing networks.\n'
              'Function "generateMovements()" will be skipped in this run')
        return

    movement_list_all = []
    number_of_movements = 0

    for node_id, node in net.node_dict.items():

        # only generate movements for highways
        valid = True
        for outgoing_link in node.outgoing_link_list:
            if outgoing_link.link_class != 'highway':
                valid = False
                break
        if not valid: continue
        for incoming_link in node.incoming_link_list:
            if incoming_link.link_class != 'highway':
                valid = False
                break
        if not valid: continue

        movement_list = _generateMovementsForOneNode(node)
        for movement in movement_list:
            movement.movement_id = number_of_movements
            movement_list_all.append(movement)
            number_of_movements += 1

    net.movement_list = movement_list_all

    _movementGeometry(net)