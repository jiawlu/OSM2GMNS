import logging


log = False
log_level = logging.WARNING
log_name = 'osm2gmns'

verbose = True

lonlat_coord_precision = 7
local_coord_precision = 2


default_int_buffer = 20.0           # meter

osm_highway_type_dict = {'motorway': ('motorway', False),
                         'motorway_link': ('motorway', True),
                         'trunk': ('trunk', False),
                         'trunk_link': ('trunk', True),
                         'primary': ('primary', False),
                         'primary_link': ('primary', True),
                         'secondary': ('secondary', False),
                         'secondary_link': ('secondary', True),
                         'tertiary': ('tertiary', False),
                         'tertiary_link': ('tertiary', True),
                         'residential': ('residential', False),
                         'residential_link': ('residential', True),
                         'service': ('service', False),
                         'services': ('service', False),
                         'cycleway': ('cycleway', False),
                         'footway': ('footway', False),
                         'pedestrian': ('footway', False),
                         'steps': ('footway', False),
                         'track': ('track', False),
                         'unclassified': ('unclassified', False)}

link_type_no_dict = {'motorway':1, 'trunk':2, 'primary':3, 'secondary':4, 'tertiary':5, 'residential':6, 'service':7,
                     'cycleway':8, 'footway':9, 'track':10, 'unclassified':11, 'connector':20, 'railway':30, 'aeroway':31}

default_lanes_dict = {'motorway': 4, 'trunk': 3, 'primary': 3, 'secondary': 2, 'tertiary': 2, 'residential': 1, 'service': 1,
                      'cycleway':1, 'footway':1, 'track':1, 'unclassified': 1, 'connector': 2}
default_speed_dict = {'motorway': 120, 'trunk': 100, 'primary': 80, 'secondary': 60, 'tertiary': 40, 'residential': 30, 'service': 30,
                      'cycleway':5, 'footway':5, 'track':30, 'unclassified': 30, 'connector':120}
default_capacity_dict = {'motorway': 2300, 'trunk': 2200, 'primary': 1800, 'secondary': 1600, 'tertiary': 1200, 'residential': 1000, 'service': 800,
                         'cycleway':800, 'footway':800, 'track':800, 'unclassified': 800, 'connector':9999}


default_oneway_flag_dict = {'motorway': False,'trunk':False,'primary':False,'secondary':False,'tertiary':False,
                            'residential':False,'service':False,'cycleway':True, 'footway':True,'track': True,
                            'unclassified':False, 'connector':False, 'railway':True, 'aeroway':True}


default_bounds = {'minlat':-90.0, 'minlon':-180.0, 'maxlat':90.0, 'maxlon':180.0}

