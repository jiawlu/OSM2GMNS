# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2021/11/27 15:34
# @desc         [script description]

import osm2gmns.settings as og_settings


class BaseNode:
    def __init__(self, node_id):
        self.name = None
        self.node_id = node_id
        self.geometry = None
        self.geometry_xy = None

        self.other_attrs = {}

        self.incoming_link_list = []
        self.outgoing_link_list = []



class BaseLink:
    def __init__(self, link_id):
        self.name = None
        self.link_id = link_id
        self.from_node = None
        self.to_node = None
        self.dir_flag = 1
        self.allowed_uses = ''
        self.geometry = None
        self.geometry_xy = None

        self.other_attrs = {}

    @property
    def length(self):
        return round(self.geometry_xy.length, og_settings.local_coord_precision)



class BaseNetwork:
    def __init__(self):
        self.node_dict = {}
        self.link_dict = {}

        self.max_node_id = 0
        self.max_link_id = 0

        self.original_coordinate_type = 'lonlat'
        self.GT = None
        self.bounds = None

        self.node_other_attrs = []
        self.link_other_attrs = []

    @property
    def number_of_nodes(self):
        return len(self.node_dict)

    @property
    def number_of_links(self):
        return len(self.link_dict)

