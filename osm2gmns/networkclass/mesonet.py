# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2021/11/27 15:34
# @desc         [script description]

from osm2gmns.networkclass.basenet import BaseNode, BaseLink, BaseNetwork


class MesoNode(BaseNode):
    def __init__(self, node_id):
        super().__init__(node_id)
        self.macronode = None
        self.macrolink = None
    @property
    def zone_id(self):
        return self.macronode.zone_id if self.macronode is not None else None
    @property
    def macro_node_id(self):
        return self.macronode.node_id if self.macronode is not None else None
    @property
    def macro_link_id(self):
        return self.macrolink.link_id if self.macrolink is not None else None
    @property
    def activity_type(self):
        return self.macronode.activity_type if self.macronode is not None else None
    @property
    def is_boundary(self):
        if self.macronode is None:
            if self.macrolink.from_node.is_boundary is None:
                return None
            else:
                return 0
        else:
            if self.macronode.is_boundary is None:
                return None
            elif self.macronode.is_boundary != 2:
                return self.macronode.is_boundary
            else:
                return -1 if self.incoming_link_list else 1


class MesoLink(BaseLink):
    def __init__(self, link_id):
        super().__init__(link_id)
        self.macronode = None
        self.macrolink = None
        self.movement = None

        self.lanes_change = []

        self.micronode_list = []  # micronode, lane by lane;
        self.microlink_list = []  # microlink

        self.micronode_bike = []
        self.microlink_bike = []
        self.micronode_walk = []
        self.microlink_walk = []

    @property
    def upstream_normal_link_of_movement_link(self):
        return self.from_node.incoming_link_list[0]
    @property
    def macro_node_id(self):
        return self.macronode.node_id if self.macronode is not None else None
    @property
    def macro_link_id(self):
        return self.macrolink.link_id if self.macrolink is not None else None
    @property
    def movement_id(self):
        return self.movement.movement_id if self.movement is not None else None
    @property
    def mvmt_txt_id(self):
        return self.movement.mvmt_txt_id if self.movement is not None else None
    @property
    def ctrl_type(self):
        return self.macronode.ctrl_type if self.macronode is not None else None
    @property
    def link_type_name(self):
        if self.macrolink is not None:
            return self.macrolink.link_type_name
        else:
            return self.upstream_normal_link_of_movement_link.link_type_name
    @property
    def link_type(self):
        if self.macrolink is not None:
            return self.macrolink.link_type
        else:
            return self.upstream_normal_link_of_movement_link.link_type
    @property
    def free_speed(self):
        if self.macrolink is not None:
            return self.macrolink.free_speed
        else:
            return self.upstream_normal_link_of_movement_link.free_speed
    @property
    def capacity(self):
        if self.macrolink is not None:
            return self.macrolink.capacity
        else:
            return self.upstream_normal_link_of_movement_link.capacity
    @property
    def allowed_uses(self):
        if self.macrolink is not None:
            return self.macrolink.allowed_uses
        else:
            return self.upstream_normal_link_of_movement_link.allowed_uses



class MesoNetwork(BaseNetwork):
    def __init__(self):
        super().__init__()