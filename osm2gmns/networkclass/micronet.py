# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2021/11/27 15:34
# @desc         [script description]

from osm2gmns.networkclass.basenet import BaseNode, BaseLink, BaseNetwork

class MicroNode(BaseNode):
    def __init__(self, node_id):
        super().__init__(node_id)
        self.mesolink = None
        self.lane_no = 0
        self.is_link_upstream_end_node = False        # nodes on the two ends of macro links
        self.is_link_downstream_end_node = False

    @property
    def zone_id(self):
        if self.is_link_upstream_end_node:
            return self.mesolink.macrolink.from_node.zone_id
        elif self.is_link_downstream_end_node:
            return self.mesolink.macrolink.to_node.zone_id
        else:
            return None

    @property
    def is_boundary(self):
        if self.mesolink.from_node.is_boundary is None:
            return None
        else:
            if self.is_link_upstream_end_node:
                return self.mesolink.from_node.is_boundary
            elif self.is_link_downstream_end_node:
                return self.mesolink.to_node.is_boundary
            else:
                return 0


class MicroLink(BaseLink):
    def __init__(self, link_id):
        super().__init__(link_id)
        self.mesolink = None
        self.cell_type = 1	            # //1:traveling; 2:changing
        self.allowed_uses = []
        self.is_first_movement_cell = False

    @property
    def mvmt_txt_id(self):
        if self.is_first_movement_cell and self.mesolink.mvmt_txt_id is not None:
            return self.mesolink.mvmt_txt_id
    @property
    def lane_no(self):
        return self.from_node.lane_no



class MicroNetwork(BaseNetwork):
    def __init__(self):
        super().__init__()