# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2021/5/24 18:27
# @desc         [script description]

from .wayfilters import network_type_all
from .settings import default_int_buffer
import os
import sys


def _checkArgs_getNetFromFile(filename, network_type, link_type, POIs, POI_sampling_ratio,
               strict_mode, offset, min_nodes, combine, int_buffer, bbox,
               default_lanes, default_speed, default_capacity):
    # filename
    if not os.path.exists(filename):
        sys.exit(f'file {filename} does not exist')

    # network_type
    if isinstance(network_type, str):
        network_type_temp = (network_type,)
    else:
        network_type_temp = network_type

    network_type_ = []
    for net_type in network_type_temp:
        if net_type not in network_type_all:
            print(f'network type \'{net_type}\' does not belong to {network_type_all}, it will be skipped')
        else:
            network_type_.append(net_type)

    # link_type
    if link_type != 'all':
        if isinstance(network_type, str):
            link_type_ = (link_type,)
        else:
            link_type_ = link_type
    else:
        link_type_ = link_type

    # POIs
    if isinstance(POIs, bool):
        POIs_ = POIs
    else:
        print('Warning: argument POIs should be a bool. The default value False has been applied')
        POIs_ = False

    # POI_sampling_ratio
    if isinstance(POI_sampling_ratio, int) or isinstance(POI_sampling_ratio, float):
        if POI_sampling_ratio < 0.0 or POI_sampling_ratio > 1.0:
            print('Warning: argument POI_sampling_ratio should be a float between 0.0 and 1.0. The default value 1.0 has been applied')
            POI_sampling_ratio_ = 1.0
        else:
            POI_sampling_ratio_ = POI_sampling_ratio
    else:
        print('Warning: argument POI_sampling_ratio should be a float between 0.0 and 1.0. The default value 1.0 has been applied')
        POI_sampling_ratio_ = 1.0

    # strict_mode
    if isinstance(strict_mode, bool):
        strict_mode_ = strict_mode
    else:
        print('Warning: argument strict_mode should be a bool. The default value True has been applied')
        strict_mode_ = True

    # offset
    if offset in ('left', 'right', 'no'):
        offset_ = offset
    else:
        print("Warning: argument offset should be chosen from 'left', 'right', 'no'. The default value 'no' has been applied")
        offset_ = 'no'

    # min_nodes
    if isinstance(min_nodes, int):
        if min_nodes < 1:
            print('Warning: argument min_nodes should be a integer greater than or equal to 1. The default value 1 has been applied')
            min_nodes_ = 1
        else:
            min_nodes_ = min_nodes
    else:
        print('Warning: argument min_nodes should be a integer greater than or equal to 1. The default value 1 has been applied')
        min_nodes_ = 1

    # combine
    if isinstance(combine, bool):
        combine_ = combine
    else:
        print('Warning: argument combine should be a bool. The default value False has been applied')
        combine_ = False

    # int_buffer
    if isinstance(int_buffer, int) or isinstance(int_buffer, float):
        if int_buffer <= 0.0:
            print(f'Warning: argument int_buffer should be a float greater than 0.0. The default value {default_int_buffer} has been applied')
            int_buffer_ = default_int_buffer
        else:
            int_buffer_ = int_buffer
    else:
        print(f'Warning: argument int_buffer should be a float greater than 0.0. The default value {default_int_buffer} has been applied')
        int_buffer_ = default_int_buffer

    # bbox
    if bbox is None:
        bbox_ = bbox
    elif isinstance(bbox, tuple) or isinstance(bbox, list):
        if len(bbox) == 4:
            for ll in bbox:
                if not(isinstance(ll, int) or isinstance(ll, float)):
                    sys.exit('argument bbox should be a tuple with four floats: (minlat, minlon, maxlat, maxlon)')
            bbox_ = bbox
        else:
            sys.exit('argument bbox should be a tuple with four floats: (minlat, minlon, maxlat, maxlon)')
    else:
        sys.exit('argument bbox should be a tuple with four floats: (minlat, minlon, maxlat, maxlon)')

    # default_lanes
    if isinstance(default_lanes, bool) or isinstance(default_lanes, dict):
        default_lanes_ = default_lanes
    else:
        print('Warning: argument default_lanes should be a bool or a dict. The default value False has been applied')
        default_lanes_ = False

    # default_speed
    if isinstance(default_speed, bool) or isinstance(default_speed, dict):
        default_speed_ = default_speed
    else:
        print('Warning: argument default_speed should be a bool or a dict. The default value False has been applied')
        default_speed_ = False

    # default_capacity
    if isinstance(default_capacity, bool) or isinstance(default_capacity, dict):
        default_capacity_ = default_capacity
    else:
        print('Warning: argument default_capacity should be a bool or a dict. The default value False has been applied')
        default_capacity_ = False

    return network_type_, link_type_, POIs_, POI_sampling_ratio_, strict_mode_, offset_, min_nodes_, combine_,\
        int_buffer_, bbox_, default_lanes_, default_speed_, default_capacity_