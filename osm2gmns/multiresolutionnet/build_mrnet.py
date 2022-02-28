# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2021/11/27 12:05
# @desc         [script description]


from osm2gmns.networkclass.macronet import Network
from osm2gmns.multiresolutionnet.netgen import NetGenerator
from osm2gmns.movement.generate_movements_old import generateMovementsForOneNode
from osm2gmns.utils.util_geo import offsetLine
import osm2gmns.settings as og_settings
from shapely import geometry
from shapely.ops import substring


# todo: connector and centroid

_length_of_short_cut = 0.1
_length_of_cut = {0: 2.0, 1: 8.0, 2: 12.0, 3: 14.0, 4: 16.0, 5: 18.0, 6: 20, 7:22, 8:24}  # e.g. 2:8.0 cut 8 meters if the original macro link has 2 lanes, etc
for i_ in range(9,100): _length_of_cut[i_] = 25
_minimum_cutted_length = 2.0


def _checkMovementLinkNecessity(node_dict):
    for node_id, node in node_dict.items():
        if node.ctrl_type == 'signal': continue

        if len(node.incoming_link_list) == 1 and len(node.outgoing_link_list) >= 1:
            # one imcoming link
            ob_link_set = set()
            multiple_connection = False
            for movement in node.movement_list:
                if movement.ob_link in ob_link_set:
                    multiple_connection = True
                    break
                else:
                    ob_link_set.add(movement.ob_link)
            if multiple_connection: continue

            node.movement_link_needed = False
            ib_link = node.incoming_link_list[0]
            ib_link.downstream_short_cut = True
            ib_link.downstream_is_target = True
            for ob_link in node.outgoing_link_list:
                ob_link.upstream_short_cut = True

        elif len(node.outgoing_link_list) == 1 and len(node.incoming_link_list) >= 1:
            # one outgoing link
            ib_link_set = set()
            multiple_connection = False
            for movement in node.movement_list:
                if movement.ib_link in ib_link_set:
                    multiple_connection = True
                    break
                else:
                    ib_link_set.add(movement.ib_link)
            if multiple_connection: continue

            node.movement_link_needed = False
            ob_link = node.outgoing_link_list[0]
            ob_link.upstream_short_cut = True
            ob_link.upstream_is_target = True
            for ib_link in node.incoming_link_list:
                ib_link.downstream_short_cut = True


def _checkLinkLanes(link_dict):
    for link_id, link in link_dict.items():
        if link.lanes is None:
            print(f'WARNING: lanes information is missing on link {link_id}, default value 1 is used')
            link.lanes_list = [1]


def _linkLaneListFromSegment(link_dict):
    resolution = 5.0
    for link_id, link in link_dict.items():
        lanes_change_point_list_temp = [0, link.length]

        if link.length <= resolution:
            link.lanes_change_point_list = lanes_change_point_list_temp.copy()
        else:
            for segment in link.segment_list:
                if segment.ref_node is link.from_node:      # todo: support link.to_node
                    lanes_change_point_list_temp.append(max(0.0, segment.start_lr))
                    lanes_change_point_list_temp.append(min(link.length, segment.end_lr))

            while lanes_change_point_list_temp:
                target_point = lanes_change_point_list_temp[0]
                remove_list = []
                for item in lanes_change_point_list_temp:
                    if target_point - resolution <= item <= target_point + resolution:
                        remove_list.append(item)
                link.lanes_change_point_list.append(target_point)
                for item in remove_list: lanes_change_point_list_temp.remove(item)
            link.lanes_change_point_list.sort()

        lanes = link.lanes
        link.lanes_list = []
        for i in range(len(link.lanes_change_point_list) - 1):
            link.lanes_list.append(lanes)
            link.lanes_change_list.append([0, 0])
            from_point = link.lanes_change_point_list[i]
            to_point = link.lanes_change_point_list[i+1]
            for segment in link.segment_list:
                length_of_overlapping = min(to_point, segment.end_lr) - max(from_point, segment.start_lr)
                if length_of_overlapping >= resolution:
                    link.lanes_list[-1] += (segment.l_lanes_added + segment.r_lanes_added)
                    link.lanes_change_list[-1][0] += segment.l_lanes_added
                    link.lanes_change_list[-1][1] += segment.r_lanes_added


def _offsetLinkGeometry(link_dict, width_of_lane, GT):
    # check if a link needs offset
    link_offset_dict = {}
    link_ids = tuple(link_dict.keys())
    for link_no_a, link_id_a in enumerate(link_ids):
        link_a = link_dict[link_id_a]
        if link_a in link_offset_dict.keys():
            continue
        geometry_xy_a_r = geometry.LineString(list(link_a.geometry_xy.coords)[::-1])
        reversed_link_found = False
        for link_id_b in link_ids[link_no_a+1:]:
            link_b = link_dict[link_id_b]
            if geometry_xy_a_r.almost_equals(link_b.geometry_xy, decimal=1):
                reversed_link_found = True
                link_offset_dict[link_a] = True
                link_offset_dict[link_b] = True
                break
        if not reversed_link_found:
            link_offset_dict[link_a] = False

    # offset links
    for link, need_offset in link_offset_dict.items():
        if need_offset:
            offset_distance = (link.max_lanes / 2 + 0.5) * width_of_lane
            geometry_xy_offset_ = link.geometry_xy.parallel_offset(distance=offset_distance, side='right', join_style=2)
            if isinstance(geometry_xy_offset_, geometry.MultiLineString):
                link.geometry_xy_offset = offsetLine(link.geometry_xy, offset_distance)
            else:
                link.geometry_xy_offset = geometry.LineString(list(geometry_xy_offset_.coords)[::-1])
            link.geometry_offset = GT.geo_to_latlon(link.geometry_xy_offset)
        else:
            link.geometry_offset = link.geometry
            link.geometry_xy_offset = link.geometry_xy

    # update breakpoints due to the change of geometry
    for link_id, link in link_dict.items():
        link.lanes_change_point_list = [item / link.length * link.length_offset for item in link.lanes_change_point_list]


def _linkLengthToCut(link):
    downstream_max_cut = max(_length_of_short_cut, link.lanes_change_point_list[-1] - link.lanes_change_point_list[-2] - 3)

    if link.upstream_short_cut and link.downstream_short_cut:
        total_length_needed = 2 * _length_of_short_cut + _minimum_cutted_length
        if link.length_offset > total_length_needed:
            link.length_of_cut_upstream = _length_of_short_cut
            link.length_of_cut_downstream = _length_of_short_cut
        else:
            link.length_of_cut_upstream = link.length_offset / total_length_needed * _length_of_short_cut
            link.length_of_cut_downstream = link.length_offset / total_length_needed * _length_of_short_cut

    elif link.upstream_short_cut:
        length_found = False
        ii = 0
        for i in range(link.lanes_list[-1], -1, -1):
            if link.length_offset > min(downstream_max_cut, _length_of_cut[i]) + _length_of_short_cut + _minimum_cutted_length:
                ii = i
                length_found = True
                break

        if length_found:
            link.length_of_cut_upstream = _length_of_short_cut
            link.length_of_cut_downstream = min(downstream_max_cut, _length_of_cut[ii])
        else:
            downstream_needed = min(downstream_max_cut, _length_of_cut[0])
            total_length_needed = downstream_needed + _length_of_short_cut + _minimum_cutted_length
            link.length_of_cut_upstream = link.length_offset / total_length_needed * _length_of_short_cut
            link.length_of_cut_downstream = link.length_offset / total_length_needed * downstream_needed

    elif link.downstream_short_cut:
        length_found = False
        ii = 0
        for i in range(link.lanes_list[-1], -1, -1):
            if link.length_offset > _length_of_cut[i] + _length_of_short_cut + _minimum_cutted_length:
                ii = i
                length_found = True
                break

        if length_found:
            link.length_of_cut_upstream = _length_of_cut[ii]
            link.length_of_cut_downstream = _length_of_short_cut
        else:
            total_length_needed = _length_of_cut[0] + _length_of_short_cut + _minimum_cutted_length
            link.length_of_cut_upstream = link.length_offset / total_length_needed * _length_of_cut[0]
            link.length_of_cut_downstream = link.length_offset / total_length_needed * _length_of_short_cut

    else:
        length_found = False
        ii = 0
        for i in range(link.lanes_list[-1], -1, -1):
            if link.length_offset > _length_of_cut[i] + min(downstream_max_cut, _length_of_cut[i]) + _minimum_cutted_length:
                ii = i
                length_found = True
                break

        if length_found:
            link.length_of_cut_upstream = _length_of_cut[ii]
            link.length_of_cut_downstream = min(downstream_max_cut, _length_of_cut[ii])
        else:
            downstream_needed = min(downstream_max_cut, _length_of_cut[0])
            total_length_needed = downstream_needed + _length_of_cut[0] + _minimum_cutted_length
            link.length_of_cut_upstream = link.length_offset / total_length_needed * _length_of_cut[0]
            link.length_of_cut_downstream = link.length_offset / total_length_needed * downstream_needed


def _performLinkCut(link, GT):
    link.cutted_lanes_change_point_list = link.lanes_change_point_list.copy()
    link.cutted_lanes_list = link.lanes_list.copy()
    link.cutted_lanes_change_list = link.lanes_change_list.copy()

    for i in range(1, len(link.cutted_lanes_change_point_list)):
        if link.cutted_lanes_change_point_list[i] > link.length_of_cut_upstream: break
    del link.cutted_lanes_change_point_list[0:i]
    link.cutted_lanes_change_point_list.insert(0, link.length_of_cut_upstream)
    del link.cutted_lanes_list[0:i-1]
    del link.cutted_lanes_change_list[0:i-1]

    for i in range(len(link.cutted_lanes_change_point_list)-2, -1, -1):
        if link.length_offset - link.cutted_lanes_change_point_list[i] > link.length_of_cut_downstream: break
    del link.cutted_lanes_change_point_list[i+1:]
    link.cutted_lanes_change_point_list.append(link.length_offset - link.length_of_cut_downstream)
    del link.cutted_lanes_list[i+1:]
    del link.cutted_lanes_change_list[i+1:]

    # self.cutted_number_of_sections = len(self.cutted_number_of_lanes_list)

    for i in range(len(link.cutted_lanes_list)):
        start_position = link.cutted_lanes_change_point_list[i]
        end_position = link.cutted_lanes_change_point_list[i+1]

        segment_geometry_xy = substring(link.geometry_xy_offset, start_dist=start_position, end_dist=end_position)
        link.cutted_geometry_xy_list.append(segment_geometry_xy)
        link.cutted_geometry_list.append(GT.geo_to_latlon(segment_geometry_xy))


def _cutMacroLinks(link_dict, GT):
    # cut macro links to stop lines to enable movement links generation
    for link_id, link in link_dict.items():
        _linkLengthToCut(link)
        _performLinkCut(link, GT)


def _autoGenerateMovements(macronet):

    max_movement_id = macronet.max_movement_id
    for macronode_id, macronode in macronet.node_dict.items():
        if macronode.movement_list:
            continue
        generateMovementsForOneNode(macronode, max_movement_id, macronet.GT)
        max_movement_id += len(macronode.movement_list)

    macronet.max_movement_id = max_movement_id


def buildMultiResolutionNets(macronet, auto_movement_generation=True, exclusive_bike_walk_lanes=True, connector_type=None,
                             width_of_lane=3.5, length_of_cell=7.0):
    """
    Build multi-resolution networks from the source network

    Parameters
    ----------
    macronet: Network
        soucrce macroscopic network
    auto_movement_generation: bool
        automatically generate movements for intersections without movement information. If auto_movement_generation is
        set as False, movements at intersections without movement information will not be generated
    exclusive_bike_walk_lanes: bool
        build exclusive lanes for bike and walk
    connector_type: int
        link_type of connectors
    width_of_lane: float
        width of lanes in meter
    length_of_cell: float
        lenght of cells in meter

    Returns
    -------

    """
    if og_settings.verbose:
        print('Building Multiresolution Networks')

    _checkLinkLanes(macronet.link_dict)
    _linkLaneListFromSegment(macronet.link_dict)
    _offsetLinkGeometry(macronet.link_dict, width_of_lane, macronet.GT)

    _checkMovementLinkNecessity(macronet.node_dict)
    _cutMacroLinks(macronet.link_dict, macronet.GT)

    if auto_movement_generation:
        _autoGenerateMovements(macronet)

    net_generator = NetGenerator(macronet, exclusive_bike_walk_lanes, length_of_cell, width_of_lane)
    net_generator.generateNet()
    macronet.mesonet = net_generator.mesonet
    macronet.micronet = net_generator.micronet