# -*- coding:utf-8 -*-
# @author       Jiawei Lu (jiaweil9@asu.edu)
#               Xuesong Zhou (xzhou74@asu.edu)
# @time         2020/10/27 17:46
# @desc         [script description]

from .util import *


class Segment:
    def __init__(self):
        self.link = None
        self.start_lr = 0.0
        self.end_lr = 0.0
        self.l_lanes_added = 0
        self.r_lanes_added = 0


class Node:
    def __init__(self):
        self.node_id = 0
        self.osm_node_id = 0
        # self.node_no = 0
        self.x_coord = 0.0
        self.y_coord = 0.0
        self.node_type = ''
        self.in_region = True
        self.is_crossing = False
        self.is_isolated = False
        self.valid = True
        self.incoming_link_list = []
        self.outgoing_link_list = []



class Link:
    def __init__(self):
        self.link_id = 0
        self.osm_way_id = 0
        self.name = ''
        self.link_type = ''
        self.from_node_id = -1
        self.to_node_id = -1
        self.from_node = None
        self.to_node = None
        self.lanes = -1
        self.lanes_list = []
        self.free_speed = -1
        self.length = 0.0
        self.geometry_point_list = []
        self.geometry_str = ''
        self.is_isolated = False
        self.valid = True
        self.ob_comb_link = None
        self.lanes_change_point_list = []

    def calculateLength(self):
        for i in range(len(self.geometry_point_list)-1):
            from_point = self.geometry_point_list[i]
            to_point = self.geometry_point_list[i+1]
            self.length += getDistanceFromCoord(from_point[0], from_point[1], to_point[0], to_point[1]) * 1000

    def getGeometryStr(self):
        geometry_str = 'LINESTRING (' + f'{self.geometry_point_list[0][0]} {self.geometry_point_list[0][1]}'
        for point in self.geometry_point_list[1:]: geometry_str += f', {point[0]} {point[1]}'
        geometry_str += ')'
        self.geometry_str = geometry_str


class Way:
    def __init__(self):
        self.osm_way_id = 0
        self.highway = ''
        self.link_type = ''
        self.name = ''
        self.lanes = -1
        self.forward_lanes = -1
        self.backward_lanes = -1
        self.maxspeed = -1
        self.oneway = None
        self.is_cycle = False
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


class Network:
    def __init__(self):
        self.minlat = 0.0
        self.minlon = 0.0
        self.maxlat = 0.0
        self.maxlon = 0.0

        self.simplified = False
        self.complex_intersection_identified = False
        self.consolidated = False
        self.new_id = True

        self.node_set = set()
        self.link_set = set()
        self.segment_set = set()
        self.complex_intersection_set = set()

        self.osm_node_id_to_node_dict = {}
        self.node_id_to_node_dict = {}
