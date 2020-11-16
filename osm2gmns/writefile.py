import csv
import os


def outputNetToCSV(network, output_folder=''):
    if output_folder:
        if not os.path.exists(output_folder): os.mkdir(output_folder)
        node_filepath = os.path.join(output_folder,'node.csv')
        link_filepath = os.path.join(output_folder,'link.csv')
        segment_filepath = os.path.join(output_folder,'segment.csv')
    else:
        node_filepath = 'node.csv'
        link_filepath = 'link.csv'
        segment_filepath = 'segment.csv'

    # we use errors='ignore' to make our program compatible with some characters that cannot be encoded by the local encoding,
    # these characters will be discarded

    while True:
        try:
            outfile = open(node_filepath, 'w', newline='',errors='ignore')
            break
        except PermissionError:
            print('node.csv may be locked by other programs. please release it then press Enter to try again')
            input()
    writer = csv.writer(outfile)
    writer.writerow(['name', 'node_id', 'osm_node_id', 'osm_highway', 'zone_id', 'ctrl_type', 'node_type', 'activity_type',
                     'is_boundary', 'x_coord', 'y_coord', 'geometry','main_node_id'])
    node_list = sorted(network.node_set, key=lambda x: x.node_id)
    for node in node_list:
        is_boundary = 1 if node.is_boundary else 0
        line = [node.name, node.node_id, node.osm_node_id, node.osm_highway, '', node.ctrl_type, '', node.activity_type,
                is_boundary, node.x_coord, node.y_coord,'',node.main_node_id]
        writer.writerow(line)
    outfile.close()

    while True:
        try:
            outfile = open(link_filepath, 'w', newline='',errors='ignore')
            break
        except PermissionError:
            print('link.csv may be locked by other programs. please release it then press Enter to try again')
            input()
    writer = csv.writer(outfile)
    writer.writerow(['name', 'link_id', 'osm_way_id', 'from_node_id', 'to_node_id', 'dir_flag', 'length', 'lanes',
                     'free_speed', 'capacity', 'link_type_name', 'link_type', 'geometry','allowed_uses'])
    link_list = sorted(network.link_set, key=lambda x: x.link_id)
    for link in link_list:
        line = [link.name, link.link_id, link.osm_way_id, link.from_node.node_id, link.to_node.node_id, '',link.length,
                link.lanes, link.free_speed, '', link.link_type_name, link.link_type, link.geometry_str, link.allowed_uses]
        writer.writerow(line)
    outfile.close()

    if network.simplified:
        while True:
            try:
                outfile = open(segment_filepath, 'w', newline='',errors='ignore')
                break
            except PermissionError:
                print('segment.csv may be locked by other programs. please release it then press Enter to try again')
                input()
        writer = csv.writer(outfile)
        writer.writerow(['segment_id','link_id','ref_node_id','start_lr','end_lr','capacity','free_speed','bike_facility',
                         'ped_facility','parking','allowed_uses','l_lanes_added','r_lanes_added'])
        segment_list = sorted(network.segment_set, key=lambda x: x.link.link_id)
        for segment_no, segment in enumerate(segment_list):
            line = [segment_no, segment.link.link_id,segment.link.from_node.node_id,segment.start_lr,segment.end_lr,'',
                    '','','','','',segment.l_lanes_added,segment.r_lanes_added]
            writer.writerow(line)
        outfile.close()