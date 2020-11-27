from .util import *


class Segment:
    def __init__(self):
        self.segment_id = 0
        self.link = None
        self.start_lr = 0.0
        self.end_lr = 0.0
        self.l_lanes_added = 0
        self.r_lanes_added = 0


class Node:
    def __init__(self):
        self.name = None
        self.node_id = 0
        self.osm_node_id = None     # str
        self.geometry = None
        self.main_node_id = None
        self.osm_highway = ''
        self.node_type = ''
        self.ctrl_type = 0
        self.in_region = True
        self.is_crossing = False
        self.is_isolated = False
        self.valid = True
        self.activity_type = ''
        self.is_boundary = False
        self.poi_id = None
        self.incoming_link_list = []
        self.outgoing_link_list = []



class Link:
    def __init__(self):
        self.link_id = 0
        self.osm_way_id = None      # str
        self.name = ''
        self.link_type_name = ''
        self.link_type = 0
        self.from_node = None
        self.to_node = None
        self.lanes = None
        self.lanes_list = []
        self.free_speed = None
        self.length = 0.0
        self.allowed_uses = ''
        self.from_bidirectional_way = False
        self.geometry = None
        self.is_isolated = False
        self.valid = True
        self.ob_comb_link = None
        self.lanes_change_point_list = []

    def calculateLength(self):
        coord_list = self.geometry.coords[:]
        for i in range(len(coord_list)-1):
            from_coord = coord_list[i]
            to_coord = coord_list[i+1]
            self.length += getDistanceFromCoord(from_coord[0], from_coord[1], to_coord[0], to_coord[1]) * 1000


class Way:
    def __init__(self):
        self.osm_way_id = None          # string
        self.highway = ''
        self.railway = ''
        self.aeroway = ''
        self.link_type_name = ''
        self.link_type = 0
        self.name = ''
        self.lanes = None
        self.forward_lanes = None
        self.backward_lanes = None
        self.maxspeed = None
        self.oneway = None

        self.area = None
        self.motor_vehicle = None
        self.motorcar = None
        self.service = None
        self.access = None
        self.foot = None
        self.bicycle = None
        self.building = None
        self.amenity = None
        self.allowable_agent_type_list = []
        self.allowed_uses = ''

        self.is_reversed = False
        self.is_cycle = False
        self.is_pure_cycle = False          # cycle without crossing nodes
        self.ref_node_list = []
        self.number_of_segments = 0
        self.segment_node_list = []         # ref node sequence for each segment

    def getNodeListForSegments(self):
        number_of_ref_nodes = len(self.ref_node_list)
        last_idx = 0
        idx = 0

        while True:
            m_segment_node_list = [self.ref_node_list[last_idx]]
            for idx in range(last_idx+1,number_of_ref_nodes):
                ref_node = self.ref_node_list[idx]
                m_segment_node_list.append(ref_node)
                if ref_node.is_crossing:
                    last_idx = idx
                    break
            self.segment_node_list.append(m_segment_node_list)
            self.number_of_segments += 1
            if idx == number_of_ref_nodes-1: break


class Relation:
    def __init__(self):
        self.osm_relation_id = None
        self.member_list = []
        self.member_role_list = []
        self.name = ''
        self.building = None
        self.amenity = None


class POI:
    def __init__(self):
        self.poi_id = 0
        self.osm_way_id = None      # str
        self.osm_relation_id = None
        self.name = ''
        self.geometry = None
        self.nearest_node = None
        self.building = None
        self.amenity = None



class Network:
    def __init__(self):
        self.bounds = None

        self.default_lanes = False
        self.default_speed = False

        self.simplified = False
        self.complex_intersection_identified = False
        self.consolidated = False
        self.new_id = True

        self.node_coordstr_to_node_dict = {}

        self.osm_node_dict = {}
        self.osm_way_dict = {}

        self.max_node_id = 0
        self.max_link_id = 0
        self.max_segment_id = 0
        self.max_main_node_id = 0
        self.max_poi_id = 0

        self.node_dict = {}
        self.link_dict = {}
        self.segment_list = []
        self.complex_intersection_list = []
        self.POI_list = []
