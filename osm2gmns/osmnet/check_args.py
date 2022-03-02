from osm2gmns.osmnet.wayfilters import network_types_all
import os
import sys


def checkArgs_getNetFromFile(filename, network_types, link_types, POI, POI_sampling_ratio,
               strict_mode, offset, min_nodes, combine, bbox,
               default_lanes, default_speed, default_capacity):
    # filename
    file_extension = os.path.splitext(filename)[-1]
    if not file_extension:
        sys.exit(f'ERROR: cannot detect the format of file {filename}. If it is a xml-based text file, please add extension .xml or .osm after the filename')
    if not os.path.exists(filename):
        sys.exit(f'ERROR: file {filename} does not exist')

    # network_types
    if isinstance(network_types, str):
        network_types_temp = [network_types,]
    elif isinstance(network_types, list) or isinstance(network_types, set) or isinstance(network_types, tuple):
        network_types_temp = network_types
    else:
        sys.exit(f'ERROR: network_types must be a string, list, set, or tuple')

    network_types_ = []
    for net_type in network_types_temp:
        if net_type not in network_types_all:
            print(f'WARNING: network_type \'{net_type}\' does not belong to {network_types_all}, it will be skipped')
        else:
            network_types_.append(net_type)

    # link_types
    if link_types != 'all':
        if isinstance(link_types, str):
            link_types_ = (link_types,)
        elif isinstance(link_types, list) or isinstance(link_types, set) or isinstance(link_types, tuple):
            link_types_ = link_types
        else:
            sys.exit(f'ERROR: argument link_types must be a string, list, set, or tuple')
    else:
        link_types_ = link_types

    # POIs
    if isinstance(POI, bool):
        POI_ = POI
    else:
        print('WARNING: argument POI should be a bool. The default value False has been applied')
        POI_ = False

    # POI_sampling_ratio
    if isinstance(POI_sampling_ratio, int) or isinstance(POI_sampling_ratio, float):
        if POI_sampling_ratio < 0.0 or POI_sampling_ratio > 1.0:
            print('WARNING: argument POI_sampling_ratio should be a float between 0.0 and 1.0. The default value 1.0 has been applied')
            POI_sampling_ratio_ = 1.0
        else:
            POI_sampling_ratio_ = POI_sampling_ratio
    else:
        print('WARNING: argument POI_sampling_ratio should be a float between 0.0 and 1.0. The default value 1.0 has been applied')
        POI_sampling_ratio_ = 1.0

    # strict_mode
    if isinstance(strict_mode, bool):
        strict_mode_ = strict_mode
    else:
        print('WARNING: argument strict_mode should be a bool. The default value True has been applied')
        strict_mode_ = True

    # offset
    if offset in ('left', 'right', 'no'):
        offset_ = offset
    else:
        print("WARNING: argument offset should be chosen from 'left', 'right', 'no'. The default value 'no' has been applied")
        offset_ = 'no'

    # min_nodes
    if isinstance(min_nodes, int):
        if min_nodes < 1:
            print('WARNING: argument min_nodes should be a integer greater than or equal to 1. The default value 1 has been applied')
            min_nodes_ = 1
        else:
            min_nodes_ = min_nodes
    else:
        print('WARNING: argument min_nodes should be an integer greater than or equal to 1. The default value 1 has been applied')
        min_nodes_ = 1

    # combine
    if isinstance(combine, bool):
        combine_ = combine
    else:
        print('WARNING: argument combine should be a bool. The default value False has been applied')
        combine_ = False

    # bbox
    if bbox is None:
        bbox_ = bbox
    elif isinstance(bbox, tuple) or isinstance(bbox, list):
        if len(bbox) == 4:
            for ll in bbox:
                if not(isinstance(ll, int) or isinstance(ll, float)):
                    sys.exit('ERROR: argument bbox should be a tuple with four floats: (minlat, minlon, maxlat, maxlon)')
            bbox_ = bbox
        else:
            sys.exit('ERROR: argument bbox should be a tuple with four floats: (minlat, minlon, maxlat, maxlon)')
    else:
        sys.exit('ERROR: argument bbox should be a tuple with four floats: (minlat, minlon, maxlat, maxlon)')

    # default_lanes
    if isinstance(default_lanes, bool) or isinstance(default_lanes, dict):
        default_lanes_ = default_lanes
    else:
        print('WARNING: argument default_lanes should be a bool or a dict. The default value False has been applied')
        default_lanes_ = False

    # default_speed
    if isinstance(default_speed, bool) or isinstance(default_speed, dict):
        default_speed_ = default_speed
    else:
        print('WARNING: argument default_speed should be a bool or a dict. The default value False has been applied')
        default_speed_ = False

    # default_capacity
    if isinstance(default_capacity, bool) or isinstance(default_capacity, dict):
        default_capacity_ = default_capacity
    else:
        print('WARNING: argument default_capacity should be a bool or a dict. The default value False has been applied')
        default_capacity_ = False

    return network_types_, link_types_, POI_, POI_sampling_ratio_, strict_mode_, offset_, min_nodes_, combine_,\
        bbox_, default_lanes_, default_speed_, default_capacity_