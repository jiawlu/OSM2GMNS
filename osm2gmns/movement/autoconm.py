from osm2gmns.utils.util_geo import getLineAngle

class CAutoConnectorM:
    default_right_most_lanes = 1        # do not change
    default_left_most_lanes = 1         # do not change

    ib_link_list = []
    ob_link = None
    ib_link_list_sorted = []
    connection_list = []


    @classmethod
    def getSequence(cls):       # order inbound links from left to right
        angle_list = []

        for ib_link in cls.ib_link_list:
            angle = getLineAngle(ib_link.geometry_xy, cls.ob_link.geometry_xy)
            angle_list.append(angle)

        cls.ib_link_list_sorted = sorted(cls.ib_link_list, key=lambda x:angle_list[cls.ib_link_list.index(x)],reverse=True)


    @classmethod
    def getLaneConnection(cls):
        cls.connection_list = [[] for _ in range(len(cls.ib_link_list_sorted))]
        ob_lanes = cls.ob_link.lanes


        left_ib_link = cls.ib_link_list_sorted[0]
        connection_lanes = min(ob_lanes, left_ib_link.outgoing_lanes)
        cls.connection_list[cls.ib_link_list.index(left_ib_link)] = [(left_ib_link.outgoing_lanes-connection_lanes, left_ib_link.outgoing_lanes-1),
                                                                     (0, connection_lanes-1)]        # in, out

        for ib_link in cls.ib_link_list_sorted[1:]:
            connection_lanes = min(ob_lanes, ib_link.outgoing_lanes)
            cls.connection_list[cls.ib_link_list.index(ib_link)] = [(0, connection_lanes - 1), (ob_lanes-connection_lanes, ob_lanes-1)]  # in, out


    @classmethod
    def buildConnector(cls):
        cls.getSequence()
        cls.getLaneConnection()
        return cls.connection_list
