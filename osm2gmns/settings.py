import logging

print_log = False
print_log_level = logging.WARNING

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
                         'residential_link': 'residential',
                         'service': 'service',
                         'services': 'service',
                         'cycleway':'cycleway',
                         'footway': 'footway',
                         'pedestrian': 'footway',
                         'steps': 'footway',
                         'track': 'track',
                         'unclassified': 'unclassified'}

link_type_no_dict = {'motorway':1, 'trunk':2, 'primary':3, 'secondary':4, 'tertiary':5, 'residential':6, 'service':7,
                     'cycleway':8, 'footway':9, 'track':10, 'unclassified':11, 'connector':20, 'railway':30, 'aeroway':31}

default_lanes_dict = {'motorway': 4, 'trunk': 3, 'primary': 3, 'secondary': 2, 'tertiary': 2, 'residential': 1, 'service': 1,
                      'cycleway':1, 'footway':1, 'track':1, 'unclassified': 1, 'connector': 2}
default_speed_dict = {'motorway': 59, 'trunk': 39, 'primary': 39, 'secondary': 39, 'tertiary': 29, 'residential': 29, 'service': 29,
                      'cycleway':9, 'footway':4, 'track':29, 'unclassified': 29, 'connector':59}


default_oneway_flag_dict = {'motorway': True,'trunk':True,'primary':True,'secondary':False,'tertiary':False,
                            'residential':False,'service':False,'cycleway':True, 'footway':True,'track': True,
                            'unclassified':False, 'connector':False, 'railway':True, 'aeroway':True}




default_int_buffer = 20.0           # meter


