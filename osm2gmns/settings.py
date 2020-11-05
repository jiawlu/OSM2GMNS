# -*- coding:utf-8 -*-
# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2020/11/3 11:30
# @desc         [script description]

osm_highway_type_dict = {'motorway': 'motorway',
                         'motorway_link': 'motorway',
                         'trunk': 'trunk',
                         'trunk_link': 'trunk',
                         'primary': 'primary',
                         'primary_link': 'primary',
                         'secondary': 'secondary',
                         'secondary_link': 'secondary',
                         'tertiary': 'tertiary',
                         'tertiary_link': 'tertiary',
                         'residential': 'residential',
                         'unclassified': 'unclassified'}

default_oneway_flag_dict = {'motorway': True,'trunk':True,'primary':True,'secondary':False,'tertiary':False,'residential':False,'unclassified':False}

default_int_buffer = 20.0
