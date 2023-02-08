# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2021/11/27 15:34
# @desc         [script description]

from osm2gmns.networkclass.basenet import BaseNode, BaseLink, BaseNetwork
from osm2gmns.osmnet.osmclasses import OSMNode
from osm2gmns.utils.util_geo import getLineFromNodes
import osm2gmns.settings as og_settings
import math


class Node(BaseNode):
    def __init__(self, node_id):
        super().__init__(node_id)
        self.zone_id = None
        self.osm_node_id = None     # str
        self.intersection_id = None
        self.osm_highway = None
        self.node_type = ''
        self.ctrl_type = ''
        self.activity_type = ''
        self.controller_id = None
        self.is_boundary = None        # -1:in, 1:out, 2:in&out, 0:no
        self.poi_id = None
        self.notes = ''

        self.movement_list = []

        # ======== FOR MULTIRESOLUTION ========
        self.is_centroid = False
        self.centroid_mesonode = None
        self.movement_link_needed = True


    def buildFromOSMNode(self, osmnode):
        """
        initialize the node from an osmnode

        Parameters
        ----------
        osmnode: OSMNode
            osmnode instance

        Returns
        -------

        """
        self.name = osmnode.name
        self.osm_node_id = osmnode.osm_node_id
        self.osm_highway = osmnode.osm_highway
        self.ctrl_type = osmnode.ctrl_type
        self.geometry = osmnode.geometry
        self.geometry_xy = osmnode.geometry_xy
        self.notes = osmnode.notes



class Link(BaseLink):
    def __init__(self, link_id):
        super().__init__(link_id)
        self.osm_way_id = None      # str
        self.free_speed = None
        self.capacity = None
        self.link_class = ''        # highway, railway, aeroway
        self.link_type_name = ''
        self.link_type = 0
        self.allowed_uses = None
        self.is_link = False
        self.is_connector = False


        self.from_bidirectional_way = False
        self.VDF_fftt1 = None
        self.VDF_cap1 = None
        self.ctrl_type = None       # signal node in the middle

        self.segment_list = []

        # ======== FOR MULTIRESOLUTION ========
        self.lanes_list = []
        self.lanes_change_point_list = []
        self.lanes_change_list = []
        self.geometry_offset = None
        self.geometry_xy_offset = None

        self.upstream_short_cut = False         # no movement needed at upstream
        self.upstream_is_target = False         # connect with other links while keeping its upstream unchanged
        self.downstream_short_cut = False       # no movement needed at downstream
        self.downstream_is_target = False       # connect with other links while keeping its upstream unchanged

        self.length_of_cut_upstream = 0.0
        self.length_of_cut_downstream = 0.0

        # self.cutted_number_of_sections = 0
        # self.cutted_length = 0.0
        # self.cutted_length_in_km = 0.0
        self.cutted_geometry_list = []      # for each segment
        self.cutted_geometry_xy_list = []  # for each segment
        self.cutted_lanes_list = []
        self.cutted_lanes_change_point_list = []
        self.cutted_lanes_change_list = []

        self.mesolink_list = []

    @property
    def incoming_lanes(self):
        return self.lanes_list[0]
    @property
    def outgoing_lanes(self):
        return self.lanes_list[-1]
    @property
    def max_lanes(self):
        return max(self.lanes_list)
    def _lane_indices(self, lanes_change_left, lanes_change_right):
        lane_indices = list(range(1, self.lanes+1))
        if lanes_change_left < 0:
            lane_indices = lane_indices[-1*lanes_change_left:]
        elif lanes_change_left > 0:
            lane_indices = list(range(-1*lanes_change_left,0)) + lane_indices
        if lanes_change_right < 0:
            lane_indices = lane_indices[:lanes_change_right]
        elif lanes_change_right > 0:
            lane_indices = lane_indices + list(range(self.lanes+1, self.lanes+1+lanes_change_right))
        return lane_indices
    @property
    def incoming_lane_indices(self):
        return self._lane_indices(*self.lanes_change_list[0])
    @property
    def outgoing_lane_indices(self):
        return self._lane_indices(*self.lanes_change_list[-1])
    @property
    def length_offset(self):
        return round(self.geometry_xy_offset.length, og_settings.local_coord_precision)

    def buildFromOSMWay(self, way, direction, ref_node_list, default_lanes, default_speed, default_capacity):
        self.osm_way_id = way.osm_way_id
        self.name = way.name
        self.link_class = way.link_class
        self.link_type_name = way.link_type_name
        self.link_type = way.link_type
        self.is_link = way.is_link

        if way.maxspeed:
            self.free_speed = way.maxspeed
        elif default_speed:
            self.free_speed = default_speed[self.link_type_name]

        if default_capacity:
            self.capacity = default_capacity[self.link_type_name]

        self.allowed_uses = way.allowed_uses
        if not way.oneway: self.from_bidirectional_way = True

        if way.oneway:
            self.lanes = way.lanes
        else:
            if direction == 1:
                if way.forward_lanes is not None:
                    self.lanes = way.forward_lanes
                elif way.lanes is not None:
                    self.lanes = math.ceil(way.lanes / 2)
                else:
                    self.lanes = way.lanes
            else:
                if way.backward_lanes is not None:
                    self.lanes = way.backward_lanes
                elif way.lanes is not None:
                    self.lanes = math.ceil(way.lanes / 2)
                else:
                    self.lanes = way.lanes

        if (self.lanes is None) and default_lanes:
            self.lanes = default_lanes[self.link_type_name]

        for ref_node in ref_node_list[1:-1]:
            if ref_node.ctrl_type == 'signal':
                self.ctrl_type = 'signal'

        self.from_node = ref_node_list[0].node
        self.to_node = ref_node_list[-1].node
        self.geometry, self.geometry_xy = getLineFromNodes(ref_node_list)
        self.from_node.outgoing_link_list.append(self)
        self.to_node.incoming_link_list.append(self)

    def linkLaneListFromSegment(self):
        self.lanes_list = []
        self.lanes_change_point_list = []
        self.lanes_change_list = []

        lanes_change_point_list_temp = [0.0, self.length]

        if self.length <= og_settings.segment_resolution:
            self.lanes_change_point_list = lanes_change_point_list_temp.copy()
        else:
            for segment in self.segment_list:
                lanes_change_point_list_temp.append(max(0.0, segment.start_lr))
                lanes_change_point_list_temp.append(min(self.length, segment.end_lr))

            while lanes_change_point_list_temp:
                target_point = lanes_change_point_list_temp[0]
                remove_list = []
                for item in lanes_change_point_list_temp:
                    if target_point - og_settings.segment_resolution <= item <= target_point + og_settings.segment_resolution:
                        remove_list.append(item)
                self.lanes_change_point_list.append(target_point)
                for item in remove_list: lanes_change_point_list_temp.remove(item)
            self.lanes_change_point_list.sort()

        for i in range(len(self.lanes_change_point_list) - 1):
            self.lanes_list.append(self.lanes)
            self.lanes_change_list.append([0, 0])
            from_point = self.lanes_change_point_list[i]
            to_point = self.lanes_change_point_list[i+1]
            for segment in self.segment_list:
                length_of_overlapping = min(to_point, segment.end_lr) - max(from_point, segment.start_lr)
                if length_of_overlapping >= og_settings.segment_resolution:
                    self.lanes_list[-1] += (segment.l_lanes_added + segment.r_lanes_added)
                    self.lanes_change_list[-1][0] += segment.l_lanes_added
                    self.lanes_change_list[-1][1] += segment.r_lanes_added


class Segment:
    def __init__(self, segment_id):
        self.segment_id = segment_id
        self.link = None
        self.ref_node = None
        self.start_lr = 0.0
        self.end_lr = 0.0
        self.l_lanes_added = 0
        self.r_lanes_added = 0

        self.other_attrs = {}


class Movement:
    def __init__(self, movement_id):
        self.movement_id = movement_id
        self.node = None
        self.ib_link = None
        self.ob_link = None

        self.start_ib_lane = None
        self.end_ib_lane = None
        self.start_ob_lane = None
        self.end_ob_lane = None

        self.start_ib_lane_seq_no = None
        self.end_ib_lane_seq_no = None
        self.start_ob_lane_seq_no = None
        self.end_ob_lane_seq_no = None

        self.name = ''
        self.lanes = 0
        self.type = ''
        self.penalty = 0.0
        self.capacity = 0.0
        self.ctrl_type = ''
        self.volume = None
        self.free_speed = None
        # self.intersection_id = None
        self.mvmt_txt_id = ''
        self.allowed_uses = []

        self.geometry = None
        self.geometry_xy = None

        self.generated_by_osm2gmns = False

        self.other_attrs = {}


class POI:
    def __init__(self):
        self.poi_id = 0
        self.osm_way_id = None      # str
        self.osm_relation_id = None
        self.name = None
        self.geometry = None
        self.geometry_xy = None
        self.centroid = None
        self.centroid_xy = None
        self.nearest_node = None
        self.building = None
        self.amenity = None
        self.leisure = None
        self.way = None         # highway,railway,aeroway poi


class Network(BaseNetwork):
    def __init__(self):
        super().__init__()

        self.default_lanes = False
        self.default_speed = False
        self.default_capacity = False

        self.max_intersection_id = 0
        self.max_segment_id = 0
        self.max_poi_id = 0
        self.max_movement_id = 0

        self.user_input_movement_list = []

        self.POI_list = []

        self.movement_other_attrs = []
        self.segment_other_attrs = []

        self.mesonet = None
        self.micronet = None


    @property
    def number_of_pois(self):
        return len(self.POI_list)
    @property
    def complete_link_lane_info(self):
        complete_link_lane_info = True
        for _, link in self.link_dict.items():
            if link.lanes is None:
                complete_link_lane_info = False
                break
        return complete_link_lane_info

