import math


class CAutoConnectorIntD:
    default_right_most_lanes = 1        # do not change
    default_left_most_lanes = 1         # do not change

    ib_link = None
    ob_link_list = []
    ob_link_list_sorted = []
    connection_list = []


    @classmethod
    def getSequence(cls):       # order outbound links from left to right
        angle_list = []

        angle_ib = math.atan2(cls.ib_link.geometry_xy.coords[-1][1] - cls.ib_link.geometry_xy.coords[0][1],
                              cls.ib_link.geometry_xy.coords[-1][0] - cls.ib_link.geometry_xy.coords[0][0])
        # angle_ib = math.atan2(cls.ib_link.geometry_list[-1][1] - cls.ib_link.geometry_list[0][1], cls.ib_link.geometry_list[-1][0] - cls.ib_link.geometry_list[0][0])
        for ob_link in cls.ob_link_list:
            angle_ob = math.atan2(ob_link.geometry_xy.coords[-1][1] - ob_link.geometry_xy.coords[0][1],
                                  ob_link.geometry_xy.coords[-1][0] - ob_link.geometry_xy.coords[0][0])
            # angle_ob = math.atan2(ob_link.geometry_list[-1][1] - ob_link.geometry_list[0][1], ob_link.geometry_list[-1][0] - ob_link.geometry_list[0][0])
            angle = angle_ob-angle_ib
            if angle < -1 * math.pi:
                angle += 2 * math.pi
            if angle > math.pi:
                angle -= 2 * math.pi
            angle_list.append(angle)

        cls.ob_link_list_sorted = sorted(cls.ob_link_list, key=lambda x:angle_list[cls.ob_link_list.index(x)],reverse=True)


    @classmethod
    def getLaneConnection(cls):
        cls.connection_list = [[] for _ in range(len(cls.ob_link_list_sorted))]
        ib_lanes = cls.ib_link.lanes

        if ib_lanes == 1:
            left_ob_link = cls.ob_link_list_sorted[0]
            cls.connection_list[cls.ob_link_list.index(left_ob_link)] = [(0, 0),(0, 0)]
            for ob_link in cls.ob_link_list_sorted[1:]:
                cls.connection_list[cls.ob_link_list.index(ob_link)] = [(0, 0), (ob_link.lanes-1, ob_link.lanes-1)]
            return

        if len(cls.ob_link_list_sorted) == 1:
            # only one ob_link, full connection
            ob_link = cls.ob_link_list_sorted[0]
            connection_lanes = min(ib_lanes, ob_link.lanes)
            cls.connection_list[cls.ob_link_list.index(ob_link)] = [(0, connection_lanes - 1), (0, connection_lanes - 1)]

        elif len(cls.ob_link_list_sorted) == 2:
            # two ob_link, default right, remaining left
            left_ob_link = cls.ob_link_list_sorted[0]
            lanes_ib_link_left = ib_lanes - cls.default_left_most_lanes
            lanes_ob_has = left_ob_link.lanes
            connection_lanes = min(lanes_ib_link_left,lanes_ob_has)
            cls.connection_list[cls.ob_link_list.index(left_ob_link)] = [(0, connection_lanes - 1), (0, connection_lanes - 1)]

            right_ob_link = cls.ob_link_list_sorted[-1]
            cls.connection_list[cls.ob_link_list.index(right_ob_link)] = [
                (ib_lanes - cls.default_right_most_lanes, ib_lanes - 1),
                (right_ob_link.lanes - cls.default_right_most_lanes, right_ob_link.lanes - 1)]

        else:
            # >= 3, default left, default right, remaining mid
            left_ob_link = cls.ob_link_list_sorted[0]
            cls.connection_list[cls.ob_link_list.index(left_ob_link)] = [(0,cls.default_left_most_lanes-1), (0,cls.default_left_most_lanes-1)]

            mid_ob_link_list = cls.ob_link_list_sorted[1:-1]
            lanes_assgined_to_each_mid_ob_link = [0] * len(mid_ob_link_list)
            lanes_each_mid_ob_link_left = [link.lanes for link in mid_ob_link_list]

            if ib_lanes - cls.default_left_most_lanes - cls.default_right_most_lanes >= len(mid_ob_link_list):
                lanes_ib_link_left = ib_lanes - cls.default_left_most_lanes - cls.default_right_most_lanes
                start_lane_no = cls.default_left_most_lanes
                while (lanes_ib_link_left > 0) and (sum(lanes_each_mid_ob_link_left) > 0):
                    for ob_link_no, ob_link in enumerate(mid_ob_link_list):
                        if lanes_each_mid_ob_link_left[ob_link_no] == 0: continue
                        if lanes_ib_link_left == 0: break
                        lanes_each_mid_ob_link_left[ob_link_no] -= 1
                        lanes_assgined_to_each_mid_ob_link[ob_link_no] += 1
                        lanes_ib_link_left -= 1
                for ob_link_no, ob_link in enumerate(mid_ob_link_list):
                    cls.connection_list[cls.ob_link_list.index(ob_link)] = [
                        (start_lane_no, start_lane_no + lanes_assgined_to_each_mid_ob_link[ob_link_no] - 1),
                        (ob_link.lanes - lanes_assgined_to_each_mid_ob_link[ob_link_no], ob_link.lanes - 1)]
                    start_lane_no += lanes_assgined_to_each_mid_ob_link[ob_link_no]
            elif ib_lanes < len(mid_ob_link_list):
                lane_no, link_no = -1, -1
                for lane_no in range(ib_lanes-1):
                    link_no = lane_no
                    ob_link = mid_ob_link_list[link_no]
                    cls.connection_list[cls.ob_link_list.index(ob_link)] = [(lane_no, lane_no), (ob_link.lanes - 1, ob_link.lanes - 1)]
                lane_no += 1
                start_link_no = link_no + 1
                for link_no in range(start_link_no, len(mid_ob_link_list)):
                    ob_link = mid_ob_link_list[link_no]
                    cls.connection_list[cls.ob_link_list.index(ob_link)] = [(lane_no, lane_no), (ob_link.lanes - 1, ob_link.lanes - 1)]
            else:
                if ib_lanes - cls.default_left_most_lanes == len(mid_ob_link_list):
                    start_lane_no = cls.default_left_most_lanes
                else:
                    # ib_lanes == len(mid_ob_link_list)
                    start_lane_no = 0
                for ob_link in mid_ob_link_list:
                    cls.connection_list[cls.ob_link_list.index(ob_link)] = [(start_lane_no, start_lane_no), (ob_link.lanes - 1, ob_link.lanes - 1)]
                    start_lane_no += 1

            right_ob_link = cls.ob_link_list_sorted[-1]
            cls.connection_list[cls.ob_link_list.index(right_ob_link)] = [
                (ib_lanes - cls.default_right_most_lanes, ib_lanes - 1),
                (right_ob_link.lanes - cls.default_right_most_lanes, right_ob_link.lanes - 1)]

    @classmethod
    def buildConnector(cls):
        cls.getSequence()
        cls.getLaneConnection()
        return cls.connection_list
