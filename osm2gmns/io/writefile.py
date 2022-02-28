from osm2gmns.io.output_mrnet import outputMesoNet, outputMicroNet
import osm2gmns.settings as og_settings
from shapely import wkt
import csv
import os


# we use errors='ignore' to make our program compatible with some characters that cannot be encoded by the local encoding,
# these characters will be discarded

def _outputNode(network, output_folder, node_filename, projection, encoding):
    node_filepath = os.path.join(output_folder, node_filename)
    while True:
        try:
            if encoding is None:
                outfile = open(node_filepath, 'w', newline='',errors='ignore')
            else:
                outfile = open(node_filepath, 'w', newline='', errors='ignore', encoding=encoding)
            break
        except PermissionError:
            print(f'{node_filename} may be locked by other programs. please release it then press Enter to try again')
            input()
    writer = csv.writer(outfile)
    writer.writerow(['name', 'node_id', 'osm_node_id', 'osm_highway', 'zone_id', 'ctrl_type', 'node_type', 'activity_type',
                     'is_boundary', 'x_coord', 'y_coord', 'intersection_id','poi_id','notes'])
    for node_id,node in network.node_dict.items():
        if projection:
            x_coord = round(node.geometry_xy.x, og_settings.local_coord_precision)
            y_coord = round(node.geometry_xy.y, og_settings.local_coord_precision)
        else:
            x_coord = round(node.geometry.x, og_settings.lonlat_coord_precision)
            y_coord = round(node.geometry.y, og_settings.lonlat_coord_precision)
        line = [node.name, node.node_id, node.osm_node_id, node.osm_highway, node.zone_id, node.ctrl_type, '', node.activity_type,
                node.is_boundary, x_coord, y_coord,node.intersection_id,node.poi_id,node.notes]
        writer.writerow(line)
    outfile.close()


def _outputLink(network, output_folder, link_filename, projection, encoding):
    link_filepath = os.path.join(output_folder, link_filename)
    while True:
        try:
            if encoding is None:
                outfile = open(link_filepath, 'w', newline='',errors='ignore')
            else:
                outfile = open(link_filepath, 'w', newline='', errors='ignore', encoding=encoding)
            break
        except PermissionError:
            print(f'{link_filename} may be locked by other programs. please release it then press Enter to try again')
            input()
    writer = csv.writer(outfile)
    writer.writerow(['name', 'link_id', 'osm_way_id', 'from_node_id', 'to_node_id', 'dir_flag', 'length', 'lanes',
                     'free_speed', 'capacity', 'link_type_name', 'link_type', 'geometry','allowed_uses','from_biway',
                     'is_link', 'VDF_fftt1', 'VDF_cap1'])
    for link_id, link in network.link_dict.items():
        from_biway = 1 if link.from_bidirectional_way else 0
        is_link = 1 if link.is_link else 0
        if projection:
            geometry_ = wkt.dumps(link.geometry_xy, rounding_precision=og_settings.local_coord_precision)
        else:
            geometry_ = wkt.dumps(link.geometry, rounding_precision=og_settings.lonlat_coord_precision)
        line = [link.name, link.link_id, link.osm_way_id, link.from_node.node_id, link.to_node.node_id, link.dir_flag, link.length,
                link.lanes, link.free_speed, link.capacity, link.link_type_name, link.link_type, geometry_, ';'.join(link.allowed_uses),
                from_biway, is_link, link.VDF_fftt1, link.VDF_cap1]
        writer.writerow(line)
    outfile.close()


def _outputMovement(network, output_folder, movement_filename, projection, encoding):
    movement_filepath = os.path.join(output_folder, movement_filename)
    if network.max_movement_id > 0:
        while True:
            try:
                if encoding is None:
                    outfile = open(movement_filepath, 'w', newline='', errors='ignore')  # ,errors='ignore'
                else:
                    outfile = open(movement_filepath, 'w', newline='', errors='ignore',
                                   encoding=encoding)  # ,errors='ignore'
                break
            except PermissionError:
                print(
                    f'{movement_filename} may be locked by other programs. please release it then press Enter to try again')
                input()
        writer = csv.writer(outfile)
        writer.writerow(['mvmt_id', 'node_id', 'osm_node_id', 'name', 'ib_link_id', 'start_ib_lane', 'end_ib_lane',
                         'ob_link_id', 'start_ob_lane', 'end_ob_lane', 'lanes', 'ib_osm_node_id', 'ob_osm_node_id',
                         'type', 'penalty', 'capacity', 'ctrl_type', 'mvmt_txt_id', 'geometry', 'volume', 'free_speed',
                         'allowed_uses', 'generated_by_osm2gmns'])

        for node_id, node in network.node_dict.items():
            for mvmt in node.movement_list:
                from_node = mvmt.ib_link.from_node
                to_node = mvmt.ob_link.to_node
                if projection:
                    geometry_ = wkt.dumps(mvmt.geometry_xy, rounding_precision=og_settings.local_coord_precision)
                else:
                    geometry_ = wkt.dumps(mvmt.geometry, rounding_precision=og_settings.lonlat_coord_precision)

                generated_by_osm2gmns = 1 if mvmt.generated_by_osm2gmns else 0

                line = [mvmt.movement_id, node.node_id, node.osm_node_id, '', mvmt.ib_link.link_id, mvmt.start_ib_lane,
                        mvmt.end_ib_lane, mvmt.ob_link.link_id, mvmt.start_ob_lane, mvmt.end_ob_lane, mvmt.lanes,
                        from_node.osm_node_id, to_node.osm_node_id, mvmt.type, '', '', mvmt.ctrl_type, mvmt.mvmt_txt_id,
                        geometry_, '', '', ';'.join(mvmt.allowed_uses), generated_by_osm2gmns]
                writer.writerow(line)
        outfile.close()


def _outputPOI(network, output_folder, poi_filename, projection, encoding):
    poi_filepath = os.path.join(output_folder, poi_filename)
    if network.POI_list:
        while True:
            try:
                if encoding is None:
                    outfile = open(poi_filepath, 'w', newline='',errors='ignore')     # ,errors='ignore'
                else:
                    outfile = open(poi_filepath, 'w', newline='', errors='ignore', encoding=encoding)  # ,errors='ignore'
                break
            except PermissionError:
                print(f'{poi_filename} may be locked by other programs. please release it then press Enter to try again')
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



def outputNetToCSV(network, output_folder='', prefix='', projection=False, encoding=None):
    if og_settings.verbose:
        print('Outputting Network Files')

    if output_folder:
        if not os.path.isdir(output_folder): os.mkdir(output_folder)

    node_filename = f'{prefix}node.csv'
    _outputNode(network, output_folder, node_filename, projection, encoding)

    link_filename = f'{prefix}link.csv'
    _outputLink(network, output_folder, link_filename, projection, encoding)

    movement_filename = f'{prefix}movement.csv'
    _outputMovement(network, output_folder, movement_filename, projection, encoding)

    poi_filename = f'{prefix}poi.csv'
    _outputPOI(network, output_folder, poi_filename, projection, encoding)

    if network.mesonet is not None:
        outputMesoNet(network.mesonet, output_folder, prefix, projection, encoding)
    if network.micronet is not None:
        outputMicroNet(network.micronet, output_folder, prefix, projection, encoding)
