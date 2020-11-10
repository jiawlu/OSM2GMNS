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

link_type_no_dict = {'motorway':1, 'trunk':2, 'primary':3, 'secondary':4, 'tertiary':5, 'residential':6, 'unclassified':7}

default_lanes_dict = {'motorway': 4, 'trunk': 3, 'primary': 3, 'secondary': 2, 'tertiary': 2, 'residential': 1, 'unclassified': 1}
default_speed_dict = {'motorway': 59, 'trunk': 39, 'primary': 39, 'secondary': 39, 'tertiary': 29, 'residential': 29, 'unclassified': 29}


default_oneway_flag_dict = {'motorway': True,'trunk':True,'primary':True,'secondary':False,'tertiary':False,'residential':False,'unclassified':False}


default_int_buffer = 20.0


