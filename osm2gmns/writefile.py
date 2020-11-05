# -*- coding:utf-8 -*-
# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2020/11/3 0:01
# @desc         [script description]


import csv
import os


def outputNetToCSV(network, output_folder=''):
    if output_folder:
        if not os.path.exists(output_folder): os.mkdir(output_folder)
        node_filepath = os.path.join(output_folder,'node.csv')
        link_filepath = os.path.join(output_folder,'link.csv')
        segment_filepath = os.path.join(output_folder,'segment.csv')
        intersection_filepath = os.path.join(output_folder,'complex_intersection.csv')
    else:
        node_filepath = 'node.csv'
        link_filepath = 'link.csv'
        segment_filepath = 'segment.csv'
        intersection_filepath = 'complex_intersection.csv'

    with open(node_filepath, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['name', 'node_id', 'osm_node_id', 'zone_id', 'ctrl_type', 'node_type', 'activity_type',
                         'is_boundary', 'x_coord', 'y_coord', 'geometry'])
        for node in network.node_set:
            line = ['', node.node_id, node.osm_node_id, '', '', node.node_type, '', '', node.x_coord, node.y_coord, '']
            writer.writerow(line)

    with open(link_filepath, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(
            ['name', 'link_id', 'osm_way_id', 'from_node_id', 'to_node_id', 'dir_flag', 'length', 'lanes', 'free_speed',
             'capacity', 'link_type_name', 'link_type', 'geometry'])
        for link in network.link_set:
            line = [link.name, link.link_id, link.osm_way_id, link.from_node.node_id, link.to_node.node_id, '',
                    link.length, link.lanes, link.free_speed, '', link.link_type, '', link.geometry_str]
            writer.writerow(line)

    if network.simplified:
        with open(segment_filepath, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['segment_id','link_id','ref_node_id','start_lr','end_lr','capacity','free_speed',
                             'bike_facility','ped_facility','parking','allowed_uses','l_lanes_added','r_lanes_added'])
            for segment_no, segment in enumerate(network.segment_set):
                line = [segment_no, segment.link.link_id,'',segment.start_lr,segment.end_lr,'','','','','','',segment.l_lanes_added,'']
                writer.writerow(line)

    if not network.consolidated:
        with open(intersection_filepath, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['group_id','node_id'])
            for group_no, group in enumerate(network.complex_intersection_set):
                node_id_str = ''
                for node in group: node_id_str += f'{node.node_id};'
                line = [group_no, node_id_str[:-1]]
                writer.writerow(line)
