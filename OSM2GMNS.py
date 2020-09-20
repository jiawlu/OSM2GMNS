# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 12:44:27 2018

@author: Jiawei(Jay) Lu (jiaweil9@asu.edu)
@author: Xuesong(Simon) Zhou (xzhou74@asu.edu)
"""

import numpy as np
import csv
from shapely.geometry import LineString
import osmnx as ox
import copy


# city = 'Xuanwu District, Nanjing, Jiangsu, China'
bbox = [32.082663,32.000739,118.811811,118.742919]      # north, south, east, west  32.082663, 118.811811;32.000739, 118.742919
generate_demand = True
new_node_id_starting_from_one = True           # assign new ids to nodes to facilitate visualization in the NEXTA (avoid large ids)
new_link_id_starting_from_one = True           # assign new ids to links to facilitate visualization in the NEXTA (avoid large ids)

use_default_value = True
default_number_of_lanes = {'motorway':4,'trunk':3,'primary':3,'secondary':2,'tertiary':2,'residential':1,'others':1,'pedestrian':1}
default_speed_limit = {'motorway':59,'trunk':39,'primary':39,'secondary':39,'tertiary':29,'residential':29,'others':29,'pedestrian':1}
default_lane_cap = {'motorway':1799,'trunk':1799,'primary':1199,'secondary':999,'tertiary':799,'residential':699,'others':699,'pedestrian':1}

osm_link_type_dict = {'motorway':'motorway',
                      'motorway_link':'motorway',
                      'trunk':'trunk',
                      'trunk_link':'trunk',
                      'primary':'primary',
                      'primary_link':'primary',
                      'secondary':'secondary',
                      'secondary_link':'secondary',
                      'tertiary':'tertiary',
                      'tertiary_link':'tertiary',
                      'residential':'residential',
                      'pedestrian':'pedestrian'}           # link types not in this dict will be represented by 'others'


g_number_of_macro_nodes = 0
g_number_of_macro_links = 0
g_number_of_zones = 0
node_attributes_list = []
link_attributes_list = []
g_macro_node_list = []
g_macro_link_list = []
g_zone_list = []
g_demand_list = []                    # (o, d, value)
g_node_id_to_seq_no_dict = {}
g_original_node_id_to_new_node_id_dict = {}


link_type_code = 1
link_type_code_dict = {}
for link_type_name in default_number_of_lanes.keys():
    link_type_code_dict[link_type_name] = link_type_code
    link_type_code += 1


class MacroNode:
    def __init__(self):
        self.name = ''
        self.node_id = 0
        self.original_node_id = 0
        self.node_seq_no = 0
        self.zone_id = None
        self.control_type = ''
        self.x_coord = 0.0
        self.y_coord = 0.0
        self.node_type = ''
        self.geometry = ''
        self.m_outgoing_link_list = []
        self.m_incoming_link_list = []

        self.activity_type = ''
        self.adjacent_link_type_count_dict = {}
        self.is_boundary = False

        
    # def Initialization(self):
    #     global g_number_of_macro_nodes
    #     self.node_seq_no = g_number_of_macro_nodes
    #     g_internal_macro_node_seq_no_dict[self.node_id] = g_number_of_macro_nodes
    #     g_number_of_macro_nodes += 1
        

class MacroLink:
    def __init__(self):
        self.name = ''
        self.link_id = ''
        self.original_link_id = ''
        self.link_key = ''
        self.from_node_id = 0
        self.to_node_id = 0
        self.link_type = ''
        self.link_type_code = 0
        self.direction = 1
        self.length = 0.0
        # self.length = float(length)/1000 if units == 1 else float(length)/1000*0.6214

        self.number_of_lanes = None
        self.speed_limit = None

        # if maxspeed != maxspeed:
        #     if use_default_value == 1:
        #         self.speed_limit = default_speed_limit[link_type] if units == 1 else default_speed_limit[link_type]/1.61
        #
        #     else:
        #         self.speed_limit = ''
        # else:
        #     if (units == 1) and ('mph' not in maxspeed):
        #         self.speed_limit = float(maxspeed)
        #     elif (units == 1) and ('mph' in maxspeed):
        #         self.speed_limit = float(maxspeed[:-4])*1.61
        #     elif (units == 2) and ('mph' not in maxspeed):
        #         self.speed_limit = float(maxspeed)/1.61
        #     else:
        #         self.speed_limit = float(maxspeed[:-4])
            
        self.capacity = None
        self.geometry = None

        self.from_node = None
        self.to_node = None



class Demand:
    def __init__(self,o_zone_id,d_zone_id,value,demand_type):
        self.o_zone_id = o_zone_id
        self.d_zone_id = d_zone_id
        self.value = value
        self.demand_type = demand_type



def GetNetwork():
    global g_number_of_macro_nodes
    global g_number_of_macro_links

    print('downloading the target network from osm database')
    G = ox.graph_from_bbox(*bbox, network_type='all')
    # G = ox.graph_from_place(city, network_type='drive')     # G_projected = ox.project_graph(G)
    node_attributes_df = ox.graph_to_gdfs(G, edges=False)
    # node_attributes_df.to_csv('node_attributes1.csv',index=False)
    link_attributes_df = ox.graph_to_gdfs(G, nodes=False)
    # link_attributes_df.to_csv('link_attributes1.csv',index=False)
    G_proj = ox.project_graph(G)
    G2 = ox.consolidate_intersections(G_proj, rebuild_graph=True, tolerance=15, dead_ends=False)
    node_attributes_df = ox.graph_to_gdfs(G2, edges=False)
    # node_attributes_df.to_csv('node_attributes2.csv',index=False)
    link_attributes_df = ox.graph_to_gdfs(G2, nodes=False)
    # link_attributes_df.to_csv('link_attributes2.csv',index=False)




    print('generating macro nodes')
    node_attributes_df = ox.graph_to_gdfs(G, edges=False)
    node_df_index_list = node_attributes_df.index

    for node_index in node_df_index_list:
        node = MacroNode()
        node.original_node_id = node_attributes_df.loc[node_index,'osmid']
        if new_node_id_starting_from_one:
            node.node_id = g_number_of_macro_nodes + 1
            g_original_node_id_to_new_node_id_dict[node.original_node_id] = node.node_id
        else:
            node.node_id = node.original_node_id

        node.node_seq_no = g_number_of_macro_nodes
        node.x_coord = node_attributes_df.loc[node_index,'x']
        node.y_coord = node_attributes_df.loc[node_index,'y']

        node_type = node_attributes_df.loc[node_index,'highway']
        node.node_type = node_type if isinstance(node_type, str) else ''
        node.geometry = node_attributes_df.loc[node_index,'geometry']

        g_macro_node_list.append(node)
        g_node_id_to_seq_no_dict[node.node_id] = node.node_seq_no
        g_number_of_macro_nodes += 1


    print('generating macro links')
    link_attributes_df = ox.graph_to_gdfs(G, nodes=False)
    link_attributes_df['name'] = link_attributes_df.apply(lambda x: x['name'][0] if isinstance(x['name'], list) else x['name'], axis=1)
    link_attributes_df['highway'] = link_attributes_df.apply(lambda x: x['highway'][0] if isinstance(x['highway'],list) else x['highway'],axis=1)
    link_attributes_df['osmid'] = link_attributes_df.apply(lambda x: x['osmid'][0] if isinstance(x['osmid'],list) else x['osmid'],axis=1)
    link_attributes_df['lanes'] = link_attributes_df.apply(lambda x: x['lanes'][0] if isinstance(x['lanes'],list) else x['lanes'],axis=1)
    if 'maxspeed' not in link_attributes_df.columns:
        link_attributes_df['maxspeed'] = np.nan
    link_attributes_df['maxspeed'] = link_attributes_df.apply(lambda x: x['maxspeed'][0] if isinstance(x['maxspeed'],list) else x['maxspeed'],axis=1)
    link_df_index_list = link_attributes_df.index

    others_link_type_set = set()

    for link_index in link_df_index_list:
        link = MacroLink()
        link.original_link_id = str(link_attributes_df.loc[link_index, 'osmid'])
        if new_link_id_starting_from_one:
            link.link_id = str(g_number_of_macro_links+1)
        else:
            link.link_id = link.original_link_id

        link.name = link_attributes_df.loc[link_index,'name']

        link_type_osm = link_attributes_df.loc[link_index,'highway']
        if link_type_osm not in osm_link_type_dict.keys():
            link_type = 'others'
            if link_type_osm not in others_link_type_set: others_link_type_set.add(link_type_osm)
        else:
            link_type = osm_link_type_dict[link_type_osm]
        link.link_type = link_type
        link.link_type_code = link_type_code_dict[link_type]

        number_of_lanes = link_attributes_df.loc[link_index,'lanes']
        oneway = link_attributes_df.loc[link_index,'oneway']

        if number_of_lanes == number_of_lanes:
            link.number_of_lanes = int(number_of_lanes) if oneway else np.ceil(int(number_of_lanes) / 2)
        else:
            if use_default_value:
                link.number_of_lanes = default_number_of_lanes[link.link_type]

        max_speed = link_attributes_df.loc[link_index,'maxspeed']
        if max_speed == max_speed:
            link.speed_limit = float(max_speed[:-4]) if 'mph' in max_speed else float(max_speed)
        else:
            if use_default_value:
                link.speed_limit = default_speed_limit[link.link_type]

        if use_default_value:
            link.capacity = default_lane_cap[link.link_type] * link.number_of_lanes

        original_from_node_id = link_attributes_df.loc[link_index,'u']
        original_to_node_id = link_attributes_df.loc[link_index, 'v']
        if new_node_id_starting_from_one:
            link.from_node_id = g_original_node_id_to_new_node_id_dict[original_from_node_id]
            link.to_node_id = g_original_node_id_to_new_node_id_dict[original_to_node_id]
        else:
            link.from_node_id = original_from_node_id
            link.to_node_id = original_to_node_id

        link.length = link_attributes_df.loc[link_index,'length'] / 1000*0.6214
        link.geometry = link_attributes_df.loc[link_index,'geometry']

        if oneway:
            g_macro_link_list.append(link)
            g_number_of_macro_links += 1
        else:
            link_r = copy.deepcopy(link)
            link.link_id = f'{link.link_id}a'
            link_r.link_id = f'{link_r.link_id}b'
            link_r.from_node_id, link_r.to_node_id = link.to_node_id, link.from_node_id
            link_r.geometry = LineString(list(reversed(list(link.geometry.coords))))
            g_macro_link_list.append(link)
            g_macro_link_list.append(link_r)
            g_number_of_macro_links += 2

    print(f'  following osm link types are represented by \'others\': {others_link_type_set}')


# def LonLat2Mile(lon1,lat1,lon2,lat2):
#     lonrad1 = lon1 * np.pi / 180
#     latrad1 = lat1 * np.pi / 180
#     lonrad2 = lon2 * np.pi / 180
#     latrad2 = lat2 * np.pi / 180
#
#     a = latrad1 - latrad2
#     b = lonrad1 - lonrad2
#     cal = 2 * np.arcsin(np.sqrt((np.sin(a / 2))**2 + np.cos(latrad1) * np.cos(latrad2) * ((np.sin(b / 2)) ** 2))) * 6378.137
#     return cal
#
#
# def DemandGeneration():
#     if not generate_demand: return
#
#     global demand_list
#     coordinate_list = []
#     number_of_outgoging_lanes_list = []
#     number_of_incoming_lanes_list = []
#     for i in range(g_number_of_macro_nodes):
#         p_node = g_macro_node_list[i]
#         if len(p_node.m_incoming_link_list) < 2 and len(p_node.m_outgoing_link_list) < 2:
#             p_node.zone_id = g_number_of_zones
#             coordinate_list.append([p_node.x,p_node.y])
#             g_zone_list.append(Zone(p_node))
#             number_of_outgoging_lanes_list.append(g_zone_list[-1].number_of_outgoing_lanes)
#             number_of_incoming_lanes_list.append(g_zone_list[-1].number_of_incoming_lanes)
#
#     coordinate_array = np.array(coordinate_list)
#     number_of_outgoging_lanes_array = np.array(number_of_outgoging_lanes_list)
#     number_of_incoming_lanes_array = np.array(number_of_incoming_lanes_list)
#
#     demand_list = [['from_zone_id','to_zone_id','number_of_trips_demand_type1']]
#     for i in range(g_number_of_zones):
#         zone_distance = LonLat2Mile(coordinate_array[i,0],coordinate_array[i,1],coordinate_array[:,0],coordinate_array[:,1])
#         demand = zone_distance * number_of_outgoging_lanes_array[i] * number_of_incoming_lanes_array
#         for j in range(g_number_of_zones):
#             if demand[j] > 0: demand_list.append([i,j,int(np.ceil(demand[j]))])


def generateDemands():
    if not generate_demand: return

    print('generating demand')
    global g_number_of_zones

    for link in g_macro_link_list:
        from_node = g_macro_node_list[g_node_id_to_seq_no_dict[link.from_node_id]]
        link.from_node = from_node
        from_node.m_outgoing_link_list.append(link)
        if link.link_type in from_node.adjacent_link_type_count_dict.keys():
            from_node.adjacent_link_type_count_dict[link.link_type] += 1
        else:
            from_node.adjacent_link_type_count_dict[link.link_type] = 1

        to_node = g_macro_node_list[g_node_id_to_seq_no_dict[link.to_node_id]]
        link.to_node = to_node
        to_node.m_incoming_link_list.append(link)
        if link.link_type in to_node.adjacent_link_type_count_dict.keys():
            to_node.adjacent_link_type_count_dict[link.link_type] += 1
        else:
            to_node.adjacent_link_type_count_dict[link.link_type] = 1

    for node in g_macro_node_list:
        if 'residential' in node.adjacent_link_type_count_dict.keys():
            node.activity_type = 'residential'
        else:
            max_count_type = ''
            max_count = 0
            for link_type, count in node.adjacent_link_type_count_dict.items():
                if count > max_count:
                    max_count = count
                    max_count_type = link_type
            node.activity_type = max_count_type

    for node in g_macro_node_list:
        if (len(node.m_incoming_link_list) == 0) or (len(node.m_outgoing_link_list) == 0):
            node.is_boundary = True
            continue

        if (len(node.m_incoming_link_list) == 1) and (len(node.m_outgoing_link_list) == 1):
            ib_link = node.m_incoming_link_list[0]
            ob_link = node.m_outgoing_link_list[0]
            if ib_link.from_node_id == ob_link.to_node_id:
                node.is_boundary = True

    for node in g_macro_node_list:
        if (node.activity_type == 'residential') or node.is_boundary:
            node.zone_id = g_number_of_zones + 1
            g_number_of_zones += 1


    # build accessable set
    print('  generating accessable node set (to ensure d_zone is reachable from o_zone)')
    accessable_set_dict = {}
    for node in g_macro_node_list:
        accessable_set_dict[node.node_id] = {node.node_id}

    cont_flag = True
    while cont_flag:
        cont_flag = False
        for link in g_macro_link_list:
            from_node_id = link.from_node_id
            to_node_id = link.to_node_id
            from_node_accessable_set = accessable_set_dict[from_node_id]
            to_node_accessable_set = accessable_set_dict[to_node_id]
            new_from_node_accessable_set = from_node_accessable_set.union(to_node_accessable_set)
            if len(from_node_accessable_set) != len(new_from_node_accessable_set):
                accessable_set_dict[from_node_id] = new_from_node_accessable_set
                cont_flag = True

    # generate od
    print('  generating od flow between valid od pairs')
    for node_o in g_macro_node_list:
        for node_d in g_macro_node_list:
            if node_o is node_d: continue

            if node_o.is_boundary and node_d.is_boundary:
                demand_type = 'external-external'
            elif node_o.is_boundary and node_d.activity_type == 'residential':
                demand_type = 'external-residential'
            elif node_o.activity_type == 'residential' and node_d.is_boundary:
                demand_type = 'residential-external'
            elif node_o.activity_type == 'residential' and node_d.activity_type == 'residential':
                demand_type = 'residential-residential'
            else:
                continue

            if node_d.node_id in accessable_set_dict[node_o.node_id]:
                g_demand_list.append(Demand(node_o.zone_id, node_d.zone_id, 1, demand_type))



def OutputResults():
    print('outputting network files')
    with open('node.csv', 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['name','node_id','zone_id','ctrl_type','node_type','activity_type','is_boundary','x_coord','y_coord','geometry'])
        for i in range(g_number_of_macro_nodes):
            p_node = g_macro_node_list[i]
            is_boundary = 1 if p_node.is_boundary else 0
            line = [p_node.name,p_node.node_id,p_node.zone_id,p_node.control_type, p_node.node_type,p_node.activity_type,
                    is_boundary,p_node.x_coord,p_node.y_coord,p_node.geometry]
            writer.writerow(line)

    with open('link.csv', 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['name','link_id','from_node_id','to_node_id','dir_flag','length','lanes','free_speed',
                         'capacity','link_type_name','link_type','geometry'])

        for i in range(g_number_of_macro_links):
            p_link = g_macro_link_list[i]
            line = [p_link.name,p_link.link_id,p_link.from_node_id, p_link.to_node_id,p_link.direction,p_link.length,
                    p_link.number_of_lanes,p_link.speed_limit,p_link.capacity,p_link.link_type,p_link.link_type_code,p_link.geometry]
            writer.writerow(line)

    with open('link_type.csv', 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['link_type','link_type_name'])
        for linktype_name, linktype_code in link_type_code_dict.items():
            writer.writerow([linktype_code,linktype_name])

    if not generate_demand: return
    with open('demand.csv', 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['o_zone_id', 'd_zone_id', 'value', 'demand_type'])
        number_of_demand_records = len(g_demand_list)
        for i in range(number_of_demand_records):
            p_demand = g_demand_list[i]
            writer.writerow([p_demand.o_zone_id,p_demand.d_zone_id,p_demand.value,None])
            
    
if __name__ == '__main__':
    GetNetwork()                # get openstreetmap network
    generateDemands()
    OutputResults()
