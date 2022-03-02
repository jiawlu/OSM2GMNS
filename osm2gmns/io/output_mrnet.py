from osm2gmns.io.util_io import getFileHandle
import osm2gmns.settings as og_settings
from shapely import wkt
import os
import csv


def _outputMesoNodes(mesonet, mesonode_filepath, projection, encoding):
    outfile = getFileHandle(mesonode_filepath, encoding)
    writer = csv.writer(outfile)

    writer.writerow(['node_id', 'zone_id', 'x_coord', 'y_coord', 'macro_node_id', 'macro_link_id', 'activity_type', 'is_boundary'])
    for mesonode_id, mesonode in mesonet.node_dict.items():
        if projection:
            x_coord = round(mesonode.geometry_xy.x, og_settings.local_coord_precision)
            y_coord = round(mesonode.geometry_xy.y, og_settings.local_coord_precision)
        else:
            x_coord = round(mesonode.geometry.x, og_settings.lonlat_coord_precision)
            y_coord = round(mesonode.geometry.y, og_settings.lonlat_coord_precision)

        line = [mesonode.node_id, mesonode.zone_id, x_coord, y_coord, mesonode.macro_node_id, mesonode.macro_link_id,
                mesonode.activity_type, mesonode.is_boundary]
        writer.writerow(line)

    outfile.close()


def _outputMesoLinks(mesonet, mesolink_filepath, projection, encoding):
    outfile = getFileHandle(mesolink_filepath, encoding)
    writer = csv.writer(outfile)

    writer.writerow(['link_id', 'from_node_id', 'to_node_id', 'dir_flag', 'length', 'lanes', 'capacity',
                     'free_speed', 'link_type_name', 'link_type', 'geometry', 'macro_node_id', 'macro_link_id',
                     'mvmt_txt_id', 'allowed_uses'])
    for mesolink_id, mesolink in mesonet.link_dict.items():
        if projection:
            geometry_ = wkt.dumps(mesolink.geometry_xy, rounding_precision=og_settings.local_coord_precision)
        else:
            geometry_ = wkt.dumps(mesolink.geometry, rounding_precision=og_settings.lonlat_coord_precision)

        line = [mesolink.link_id, mesolink.from_node.node_id, mesolink.to_node.node_id, mesolink.dir_flag, mesolink.length,
                mesolink.lanes, mesolink.capacity, mesolink.free_speed, mesolink.link_type_name,mesolink.link_type,
                geometry_, mesolink.macro_node_id, mesolink.macro_link_id, mesolink.mvmt_txt_id, ';'.join(mesolink.allowed_uses)]
        writer.writerow(line)

    outfile.close()


def _outputMicroNodes(micronet, micronode_filepath, projection, encoding):
    outfile = getFileHandle(micronode_filepath, encoding)
    writer = csv.writer(outfile)

    writer.writerow(['node_id', 'zone_id', 'x_coord', 'y_coord', 'meso_link_id', 'lane_no', 'is_boundary'])
    for micronode_id, micronode in micronet.node_dict.items():
        if projection:
            x_coord = round(micronode.geometry_xy.x, og_settings.local_coord_precision)
            y_coord = round(micronode.geometry_xy.y, og_settings.local_coord_precision)
        else:
            x_coord = round(micronode.geometry.x, og_settings.lonlat_coord_precision)
            y_coord = round(micronode.geometry.y, og_settings.lonlat_coord_precision)

        line = [micronode.node_id, micronode.zone_id, x_coord, y_coord, micronode.mesolink.link_id, micronode.lane_no, micronode.is_boundary]
        writer.writerow(line)

    outfile.close()


def _outputMicroLinks(micronet, microlink_filepath, projection, encoding):
    outfile = getFileHandle(microlink_filepath, encoding)
    writer = csv.writer(outfile)

    writer.writerow(['link_id', 'from_node_id', 'to_node_id', 'dir_flag', 'length', 'lanes', 'capacity',
                     'free_speed', 'link_type_name', 'link_type', 'geometry', 'macro_node_id', 'macro_link_id',
                     'meso_link_id', 'cell_type', 'additional_cost', 'lane_no', 'mvmt_txt_id', 'allowed_uses'])
    for microlink_id, microlink in micronet.link_dict.items():
        if projection:
            geometry_ = wkt.dumps(microlink.geometry_xy, rounding_precision=og_settings.local_coord_precision)
        else:
            geometry_ = wkt.dumps(microlink.geometry, rounding_precision=og_settings.lonlat_coord_precision)

        line = [microlink.link_id, microlink.from_node.node_id, microlink.to_node.node_id, microlink.dir_flag,
                microlink.length, 1, microlink.mesolink.capacity, microlink.mesolink.free_speed,
                microlink.mesolink.link_type_name, microlink.mesolink.link_type, geometry_,
                microlink.mesolink.macro_node_id, microlink.mesolink.macro_link_id, microlink.mesolink.link_id,
                microlink.cell_type, 0, microlink.lane_no, microlink.mvmt_txt_id, ';'.join(microlink.allowed_uses)]
        writer.writerow(line)

    outfile.close()



def outputMesoNet(mesonet, output_folder, prefix, projection, encoding):
    mesonet_folder = os.path.join(output_folder, 'mesonet')
    if not os.path.isdir(mesonet_folder): os.mkdir(mesonet_folder)

    mesonode_filepath = os.path.join(mesonet_folder, f'{prefix}node.csv')
    _outputMesoNodes(mesonet, mesonode_filepath, projection, encoding)

    mesolink_filepath = os.path.join(mesonet_folder, f'{prefix}link.csv')
    _outputMesoLinks(mesonet, mesolink_filepath, projection, encoding)


def outputMicroNet(micronet, output_folder, prefix, projection, encoding):
    micronet_folder = os.path.join(output_folder, 'micronet')
    if not os.path.isdir(micronet_folder): os.mkdir(micronet_folder)

    micronode_filepath = os.path.join(micronet_folder, f'{prefix}node.csv')
    _outputMicroNodes(micronet, micronode_filepath, projection, encoding)

    microlink_filepath = os.path.join(micronet_folder, f'{prefix}link.csv')
    _outputMicroLinks(micronet, microlink_filepath, projection, encoding)
