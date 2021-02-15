import csv
import os
from shapely import geometry


def outputNetToCSV(network, output_folder='', projection=False, enconding=None):
    if output_folder:
        if not os.path.exists(output_folder): os.mkdir(output_folder)
        node_filepath = os.path.join(output_folder,'node.csv')
        link_filepath = os.path.join(output_folder,'link.csv')
        segment_filepath = os.path.join(output_folder,'segment.csv')
        movement_filepath = os.path.join(output_folder, 'movement.csv')
        structure_filpath = os.path.join(output_folder,'poi.csv')
    else:
        node_filepath = 'node.csv'
        link_filepath = 'link.csv'
        segment_filepath = 'segment.csv'
        movement_filepath = 'movement.csv'
        structure_filpath = 'poi.csv'

    # we use errors='ignore' to make our program compatible with some characters that cannot be encoded by the local encoding,
    # these characters will be discarded

    while True:
        try:
            if enconding is None:
                outfile = open(node_filepath, 'w', newline='',errors='ignore')
            else:
                outfile = open(node_filepath, 'w', newline='', errors='ignore', encoding=enconding)
            break
        except PermissionError:
            print('node.csv may be locked by other programs. please release it then press Enter to try again')
            input()
    writer = csv.writer(outfile)
    writer.writerow(['name', 'node_id', 'osm_node_id', 'osm_highway', 'zone_id', 'ctrl_type', 'node_type', 'activity_type',
                     'is_boundary', 'x_coord', 'y_coord', 'main_node_id','poi_id','notes'])
    for node_id,node in network.node_dict.items():
        if node.is_boundary is None:
            is_boundary = ''
        else:
            is_boundary = 1 if node.is_boundary else 0
        x_coord = node.geometry_xy.x if projection else node.geometry.x
        y_coord = node.geometry_xy.y if projection else node.geometry.y
        line = [node.name, node.node_id, node.osm_node_id, node.osm_highway, '', node.ctrl_type, '', node.activity_type,
                is_boundary, x_coord, y_coord,node.main_node_id,node.poi_id,node.notes]
        writer.writerow(line)
    outfile.close()

    while True:
        try:
            if enconding is None:
                outfile = open(link_filepath, 'w', newline='',errors='ignore')
            else:
                outfile = open(link_filepath, 'w', newline='', errors='ignore', encoding=enconding)
            break
        except PermissionError:
            print('link.csv may be locked by other programs. please release it then press Enter to try again')
            input()
    writer = csv.writer(outfile)
    writer.writerow(['name', 'link_id', 'osm_way_id', 'from_node_id', 'to_node_id', 'dir_flag', 'length', 'lanes',
                     'free_speed', 'capacity', 'link_type_name', 'link_type', 'geometry','allowed_uses','from_biway'])
    for link_id, link in network.link_dict.items():
        from_biway = 1 if link.from_bidirectional_way else 0
        geometry_ = link.geometry_xy if projection else link.geometry
        line = [link.name, link.link_id, link.osm_way_id, link.from_node.node_id, link.to_node.node_id, 1, link.length,
                link.lanes, link.free_speed, '', link.link_type_name, link.link_type, geometry_, link.allowed_uses,from_biway]
        writer.writerow(line)
    outfile.close()

    if network.link_combined:
        while True:
            try:
                if enconding is None:
                    outfile = open(segment_filepath, 'w', newline='',errors='ignore')
                else:
                    outfile = open(segment_filepath, 'w', newline='', errors='ignore', encoding=enconding)
                break
            except PermissionError:
                print('segment.csv may be locked by other programs. please release it then press Enter to try again')
                input()
        writer = csv.writer(outfile)
        writer.writerow(['segment_id','link_id','ref_node_id','start_lr','end_lr','capacity','free_speed','bike_facility',
                         'ped_facility','parking','allowed_uses','l_lanes_added','r_lanes_added'])
        for segment in network.segment_list:
            line = [segment.segment_id, segment.link.link_id,segment.link.from_node.node_id,segment.start_lr,segment.end_lr,'',
                    '','','','','',segment.l_lanes_added,segment.r_lanes_added]
            writer.writerow(line)
        outfile.close()

    if network.movement_list:
        while True:
            try:
                if enconding is None:
                    outfile = open(movement_filepath, 'w', newline='',errors='ignore')     # ,errors='ignore'
                else:
                    outfile = open(movement_filepath, 'w', newline='', errors='ignore', encoding=enconding)  # ,errors='ignore'
                break
            except PermissionError:
                print('movement.csv may be locked by other programs. please release it then press Enter to try again')
                input()
        writer = csv.writer(outfile)
        writer.writerow(['mvmt_id', 'node_id', 'osm_node_id', 'name', 'ib_link_id','ib_lane','ob_link_id','ob_lane',
                         'lanes','ib_osm_node_id','ob_osm_node_id','type','penalty','capacity','ctrl_type','movement_str',
                         'geometry','volume','free_speed'])
        for mvmt in network.movement_list:
            node = mvmt.node
            from_node = mvmt.ib_link.from_node
            to_node = mvmt.ob_link.to_node
            if projection:
                geometry_ = geometry.LineString([from_node.geometry_xy, node.geometry_xy, to_node.geometry_xy])
            else:
                geometry_ = geometry.LineString([from_node.geometry, node.geometry, to_node.geometry])
            line = [mvmt.movement_id, node.node_id, node.osm_node_id, '', mvmt.ib_link.link_id, mvmt.ib_lane,
                    mvmt.ob_link.link_id, mvmt.ob_lane, mvmt.lanes, from_node.osm_node_id, to_node.osm_node_id,
                    '', '', '', '', mvmt.movement_str,geometry_]
            writer.writerow(line)

    if network.POI_list:
        while True:
            try:
                if enconding is None:
                    outfile = open(structure_filpath, 'w', newline='',errors='ignore')     # ,errors='ignore'
                else:
                    outfile = open(structure_filpath, 'w', newline='', errors='ignore', encoding=enconding)  # ,errors='ignore'
                break
            except PermissionError:
                print('POI.csv may be locked by other programs. please release it then press Enter to try again')
                input()
        writer = csv.writer(outfile)
        writer.writerow(['name', 'poi_id', 'osm_way_id', 'osm_relation_id','building','amenity','way','geometry','centroid',
                         'area', 'area_ft2'])
        for poi in network.POI_list:
            geometry_ = poi.geometry_xy if projection else poi.geometry
            centroid = poi.centroid_xy if projection else poi.centroid
            area = poi.geometry_xy.area
            area_ft2 = area * 10.7639
            line = [poi.name, poi.poi_id, poi.osm_way_id, poi.osm_relation_id, poi.building, poi.amenity, poi.way, geometry_,
                    centroid, round(area,1), round(area_ft2,1)]
            writer.writerow(line)