from osm2gmns.networkclass.mesonet import MesoNode, MesoLink, MesoNetwork
from osm2gmns.networkclass.micronet import MicroNode, MicroLink, MicroNetwork
import osm2gmns.settings as og_settings
from shapely import geometry
import sys



class NetGenerator:
    def __init__(self, macronet, length_of_cell, width_of_lane):
        self.macronet = macronet
        self.length_of_cell = length_of_cell
        self.width_of_lane = width_of_lane

        self.mesonet = MesoNetwork()
        self.micronet = MicroNetwork()

        # self.number_of_micro_nodes = 0
        # self.number_of_micro_links = 0
        # self.number_of_meso_nodes = 0
        # self.number_of_meso_links = 0
        #
        # self.micro_node_list = []
        # self.micro_link_list = []
        # self.meso_node_list = []
        # self.meso_link_list = []
        #
        # self.meso_node_id_to_seq_no_dict = {}
        # self.micro_node_id_to_seq_no_dict = {}
        # self.meso_link_id_to_seq_no_dict = {}
        # self.micro_link_id_to_seq_no_dict = {}
        #
        # self.meso_link_key_to_seq_no_dict = {}
        # self.processed_node_id_set = set()

        self.number_of_expanded_mesonode = {}       # macronode: number_of_expanded_mesonode


    def createMicroNetForNormalLink(self, link):
        max_micronode_id = self.micronet.max_node_id
        max_microlink_id = self.micronet.max_link_id

        # create micronodes on each mesolink
        for mesolink in link.mesolink_list:
            original_number_of_lanes = mesolink.macrolink.lanes
            lane_changes_left = mesolink.lanes_change[0]
            num_of_lane_offset_between_left_most_and_central = -1 * (original_number_of_lanes / 2 - 0.5 + lane_changes_left)

            lane_geometry_xy_list = []
            for i in range(mesolink.lanes):
                lane_offset = (num_of_lane_offset_between_left_most_and_central + i) * self.width_of_lane
                if lane_offset < -1e-3 or lane_offset > 1e-3:
                    lane_geometry_xy = mesolink.geometry_xy.parallel_offset(distance=lane_offset, side='right', join_style=2)

                    if isinstance(lane_geometry_xy, geometry.MultiLineString):
                        coords = []
                        for line in lane_geometry_xy: coords += line.coords
                        lane_geometry_xy = geometry.LineString(coords)

                    if lane_offset > 1e-3:
                        lane_geometry_xy = geometry.LineString(list(lane_geometry_xy.coords)[::-1])
                else:
                    lane_geometry_xy = mesolink.geometry_xy
                lane_geometry_xy_list.append(lane_geometry_xy)

            number_of_cells = max(1, round(mesolink.length / self.length_of_cell))
            micronode_geometry_xy_list = [[lane_geometry_xy.interpolate(i/number_of_cells, normalized=True) for i in range(number_of_cells+1)] for lane_geometry_xy in lane_geometry_xy_list]

            for i in range(mesolink.lanes):
                micronode_list_lane = []
                for micronode_geometry_xy in micronode_geometry_xy_list[i]:
                    micronode = MicroNode(max_micronode_id)
                    micronode.geometry_xy = micronode_geometry_xy
                    micronode.geometry = self.macronet.GT.geo_to_latlon(micronode_geometry_xy)
                    micronode.mesolink = mesolink
                    micronode.lane_no = i + 1
                    micronode_list_lane.append(micronode)
                    self.micronet.node_dict[micronode.node_id] = micronode
                    max_micronode_id += 1
                mesolink.micronode_list.append(micronode_list_lane)

        # micronodes on two ends
        first_mesolink = link.mesolink_list[0]
        for micronode_list_lane in first_mesolink.micronode_list:
            micronode_list_lane[0].is_link_upstream_end_node = True
        last_mesolink = link.mesolink_list[-1]
        for micronode_list_lane in last_mesolink.micronode_list:
            micronode_list_lane[-1].is_link_downstream_end_node = True

        # micronodes between two adjacent mesolinks
        for i in range(len(link.mesolink_list)-1):
            upstream_mesolink = link.mesolink_list[i]
            downstream_mesolink = link.mesolink_list[i+1]

            up_index_of_left_most_lane_of_original_link = upstream_mesolink.lanes_change[0]
            down_index_of_left_most_lane_of_original_link = downstream_mesolink.lanes_change[0]
            min_left_most_lane_index = min(up_index_of_left_most_lane_of_original_link, down_index_of_left_most_lane_of_original_link)
            up_lane_index_start = up_index_of_left_most_lane_of_original_link - min_left_most_lane_index
            down_lane_index_start = down_index_of_left_most_lane_of_original_link - min_left_most_lane_index

            number_of_connecting_lanes = min(upstream_mesolink.lanes-up_lane_index_start,
                                             downstream_mesolink.lanes-down_lane_index_start)

            for j in range(number_of_connecting_lanes):
                up_lane_index = up_lane_index_start + j
                down_lane_index = down_lane_index_start + j
                up_micronode = upstream_mesolink.micronode_list[up_lane_index][-1]
                down_micronode = downstream_mesolink.micronode_list[down_lane_index][0]
                upstream_mesolink.micronode_list[up_lane_index][-1] = down_micronode
                del self.micronet.node_dict[up_micronode.node_id]


        # create cell
        for mesolink in link.mesolink_list:
            for i in range(mesolink.lanes):
                # travelling
                for j in range(len(mesolink.micronode_list[i])-1):
                    microlink = MicroLink(max_microlink_id)
                    microlink.from_node = mesolink.micronode_list[i][j]
                    microlink.to_node = mesolink.micronode_list[i][j+1]
                    microlink.geometry = geometry.LineString([microlink.from_node.geometry, microlink.to_node.geometry])
                    microlink.geometry_xy = geometry.LineString([microlink.from_node.geometry_xy, microlink.to_node.geometry_xy])
                    microlink.mesolink = mesolink
                    microlink.cell_type = 1	            # //1:traveling; 2:changing
                    self.micronet.link_dict[microlink.link_id] = microlink
                    max_microlink_id += 1
                    microlink.from_node.outgoing_link_list.append(microlink)
                    microlink.to_node.incoming_link_list.append(microlink)

                # changing
                if i <= mesolink.lanes - 2:
                    # to left
                    for j in range(len(mesolink.micronode_list[i])-1):
                        microlink = MicroLink(max_microlink_id)
                        microlink.from_node = mesolink.micronode_list[i][j]
                        microlink.to_node = mesolink.micronode_list[i+1][j+1]
                        microlink.geometry = geometry.LineString([microlink.from_node.geometry, microlink.to_node.geometry])
                        microlink.geometry_xy = geometry.LineString([microlink.from_node.geometry_xy, microlink.to_node.geometry_xy])
                        microlink.mesolink = mesolink
                        microlink.cell_type = 2	            # //1:traveling; 2:changing
                        self.micronet.link_dict[microlink.link_id] = microlink
                        max_microlink_id += 1
                        microlink.from_node.outgoing_link_list.append(microlink)
                        microlink.to_node.incoming_link_list.append(microlink)

                if i >= 1:
                    # to right
                    for j in range(len(mesolink.micronode_list[i])-1):
                        microlink = MicroLink(max_microlink_id)
                        microlink.from_node = mesolink.micronode_list[i][j]
                        microlink.to_node = mesolink.micronode_list[i-1][j+1]
                        microlink.geometry = geometry.LineString([microlink.from_node.geometry, microlink.to_node.geometry])
                        microlink.geometry_xy = geometry.LineString([microlink.from_node.geometry_xy, microlink.to_node.geometry_xy])
                        microlink.mesolink = mesolink
                        microlink.cell_type = 2	            # //1:traveling; 2:changing
                        self.micronet.link_dict[microlink.link_id] = microlink
                        max_microlink_id += 1
                        microlink.from_node.outgoing_link_list.append(microlink)
                        microlink.to_node.incoming_link_list.append(microlink)

        self.micronet.max_node_id = max_micronode_id
        self.micronet.max_link_id = max_microlink_id


    def createMicroNetForConnector(self, mesolink, ib_mesolink, ib_lane_index_start, ob_mesolink, ob_lane_index_start):
        max_micronode_id = self.micronet.max_node_id
        max_microlink_id = self.micronet.max_link_id

        for i in range(mesolink.lanes):
            start_micronode = ib_mesolink.micronode_list[ib_lane_index_start+i][-1]
            end_micronode = ob_mesolink.micronode_list[ob_lane_index_start+i][0]
            lane_geometry_xy = geometry.LineString([start_micronode.geometry_xy, end_micronode.geometry_xy])

            number_of_cells = max(1, round(lane_geometry_xy.length / self.length_of_cell))
            micronode_geometry_xy_list = [lane_geometry_xy.interpolate(i/number_of_cells, normalized=True) for i in range(1,number_of_cells)]

            mesolink.micronode_list.append([])
            mesolink.microlink_list.append([])
            last_micronode = start_micronode

            first_movement_cell = True

            for micronode_geometry_xy in micronode_geometry_xy_list:
                micronode = MicroNode(max_micronode_id)
                micronode.geometry_xy = micronode_geometry_xy
                micronode.geometry = self.macronet.GT.geo_to_latlon(micronode_geometry_xy)
                micronode.mesolink = mesolink
                micronode.lane_no = i + 1
                mesolink.micronode_list[-1].append(micronode)
                self.micronet.node_dict[micronode.node_id] = micronode
                max_micronode_id += 1

                microlink = MicroLink(max_microlink_id)
                microlink.from_node = last_micronode
                microlink.to_node = micronode
                microlink.geometry = geometry.LineString([microlink.from_node.geometry, microlink.to_node.geometry])
                microlink.geometry_xy = geometry.LineString([microlink.from_node.geometry_xy, microlink.to_node.geometry_xy])
                microlink.mesolink = mesolink
                microlink.cell_type = 1	            # //1:traveling; 2:changing

                if first_movement_cell:
                    microlink.is_first_movement_cell = True
                    first_movement_cell = False

                mesolink.microlink_list[-1].append(microlink)
                self.micronet.link_dict[microlink.link_id] = microlink
                max_microlink_id += 1
                microlink.from_node.outgoing_link_list.append(microlink)
                microlink.to_node.incoming_link_list.append(microlink)

                last_micronode = micronode

            microlink = MicroLink(max_microlink_id)
            microlink.from_node = last_micronode
            microlink.to_node = end_micronode
            microlink.geometry = geometry.LineString([microlink.from_node.geometry, microlink.to_node.geometry])
            microlink.geometry_xy = geometry.LineString([microlink.from_node.geometry_xy, microlink.to_node.geometry_xy])
            microlink.mesolink = mesolink
            microlink.cell_type = 1	            # //1:traveling; 2:changing

            if first_movement_cell:
                microlink.is_first_movement_cell = True

            mesolink.microlink_list[-1].append(microlink)
            self.micronet.link_dict[microlink.link_id] = microlink
            max_microlink_id += 1
            microlink.from_node.outgoing_link_list.append(microlink)
            microlink.to_node.incoming_link_list.append(microlink)

        self.micronet.max_node_id = max_micronode_id
        self.micronet.max_link_id = max_microlink_id


    def createMesoNodeForCentriod(self):
        # create new meso nodes for centroids
        for node_id, node in self.macronet.node_dict.items():
            if node.is_centroid:

                if node not in self.number_of_expanded_mesonode.keys():
                    self.number_of_expanded_mesonode[node] = 0
                number_of_expanded_mesonode = self.number_of_expanded_mesonode[node]
                self.number_of_expanded_mesonode[node] += 1

                mesonode = MesoNode(node.node_id * 100 + number_of_expanded_mesonode)
                mesonode.geometry = node.geometry
                mesonode.geometry_xy = node.geometry_xy
                mesonode.macronode = node
                node.centroid_mesonode = mesonode
                self.mesonet.node_dict[mesonode.node_id] = mesonode


    def createNormalLinks(self):
        if og_settings.verbose:
            print('  generating normal meso links...')

        max_mesolink_id = self.mesonet.max_link_id

        for link_id, link in self.macronet.link_dict.items():
            macro_from_node = link.from_node
            if macro_from_node.is_centroid:
                upstream_node = macro_from_node.centroid_meso_node
            else:
                if macro_from_node not in self.number_of_expanded_mesonode.keys():
                    self.number_of_expanded_mesonode[macro_from_node] = 0
                number_of_expanded_mesonode = self.number_of_expanded_mesonode[macro_from_node]
                self.number_of_expanded_mesonode[macro_from_node] += 1

                upstream_node = MesoNode(macro_from_node.node_id * 100 + number_of_expanded_mesonode)
                upstream_node.geometry = geometry.Point(link.cutted_geometry_list[0].coords[0])
                upstream_node.geometry_xy = geometry.Point(link.cutted_geometry_xy_list[0].coords[0])
                upstream_node.macronode = macro_from_node

                self.mesonet.node_dict[upstream_node.node_id] = upstream_node

            cutted_number_of_segments = len(link.cutted_lanes_list)
            macro_to_node = link.to_node
            for section_no in range(cutted_number_of_segments):
                if macro_to_node.is_centroid and section_no == cutted_number_of_segments - 1:
                    downstream_node = macro_to_node.centroid_meso_node
                else:
                    if macro_to_node not in self.number_of_expanded_mesonode.keys():
                        self.number_of_expanded_mesonode[macro_to_node] = 0
                    number_of_expanded_mesonode = self.number_of_expanded_mesonode[macro_to_node]
                    self.number_of_expanded_mesonode[macro_to_node] += 1

                    downstream_node = MesoNode(macro_to_node.node_id * 100 + number_of_expanded_mesonode)
                    downstream_node.geometry = geometry.Point(link.cutted_geometry_list[section_no].coords[-1])
                    downstream_node.geometry_xy = geometry.Point(link.cutted_geometry_xy_list[section_no].coords[-1])
                    if section_no == cutted_number_of_segments - 1:
                        downstream_node.macronode = macro_to_node
                    else:
                        downstream_node.macrolink = link

                    self.mesonet.node_dict[downstream_node.node_id] = downstream_node

                mesolink = MesoLink(max_mesolink_id)
                mesolink.from_node = upstream_node
                mesolink.to_node = downstream_node
                mesolink.lanes = link.cutted_lanes_list[section_no]
                mesolink.lanes_change = link.cutted_lanes_change_list[section_no]
                mesolink.geometry = link.cutted_geometry_list[section_no]
                mesolink.geometry_xy = link.cutted_geometry_xy_list[section_no]
                mesolink.macrolink = link

                link.mesolink_list.append(mesolink)
                upstream_node.outgoing_link_list.append(mesolink)
                downstream_node.incoming_link_list.append(mesolink)

                self.mesonet.link_dict[mesolink.link_id] = mesolink
                max_mesolink_id += 1
                upstream_node = downstream_node

            self.createMicroNetForNormalLink(link)

        self.mesonet.max_link_id = max_mesolink_id


    def connectMesoLinksMVMT(self):
        if og_settings.verbose:
            print('  generating movement meso links...')

        max_mesolink_id = self.mesonet.max_link_id

        for macronode_id, macronode in self.macronet.node_dict.items():
            for mvmt in macronode.movement_list:
                ib_link, ob_link = mvmt.ib_link, mvmt.ob_link
                ib_lane_list = [lane_no for lane_no in range(int(mvmt.start_ib_lane), int(mvmt.end_ib_lane + 1))]
                ob_lane_list = [lane_no for lane_no in range(int(mvmt.start_ob_lane), int(mvmt.end_ob_lane + 1))]

                ib_mesolink = ib_link.mesolink_list[-1]
                ob_mesolink = ob_link.mesolink_list[0]

                if len(ib_lane_list) != len(ob_lane_list):
                    print('  warning: number of inbound lanes and outbound lanes at movement {} is not consistent, movement info will be discarded'.format(mvmt.movement_id))
                    continue
                if (0 in ib_lane_list) or (0 in ob_lane_list):
                    print('  warning: lane number 0 detected at movement {}, movement info will be discarded'.format(mvmt.movement_id))
                    continue
                number_of_lanes = len(ib_lane_list)

                # lane index starts from 0
                ib_lane_index_start = ib_mesolink.lanes_change[0] + ib_lane_list[0] if ib_lane_list[0] < 0 else ib_mesolink.lanes_change[0] + ib_lane_list[0] - 1
                ib_lane_index_end = ib_mesolink.lanes_change[0] + ib_lane_list[-1] if ib_lane_list[-1] < 0 else ib_mesolink.lanes_change[0] + ib_lane_list[-1] - 1
                ob_lane_index_start = ob_mesolink.lanes_change[0] + ob_lane_list[0] if ob_lane_list[0] < 0 else ob_mesolink.lanes_change[0] + ob_lane_list[0] - 1
                ob_lane_index_end = ob_mesolink.lanes_change[0] + ob_lane_list[-1] if ob_lane_list[-1] < 0 else ob_mesolink.lanes_change[0] + ob_lane_list[-1] - 1

                if (ib_lane_index_start < 0) or (ob_lane_index_start < 0) or (ib_lane_index_end > ib_mesolink.lanes - 1) or (ob_lane_index_end > ob_mesolink.lanes - 1):
                    print('  warning: inbound or outbound lane info of movement {} is not consistent with what inbound or outbound link has,'
                        ' movement info will be discarded'.format(mvmt.movement_id))
                    continue

                if macronode.movement_link_needed:
                    mesolink = MesoLink(max_mesolink_id)
                    mesolink.from_node = ib_mesolink.to_node
                    mesolink.to_node = ob_mesolink.from_node
                    mesolink.lanes = number_of_lanes
                    mesolink.isconnector = True
                    mesolink.movement = mvmt
                    mesolink.macronode = macronode

                    mesolink.geometry = geometry.LineString([ib_mesolink.geometry.coords[-1], ob_mesolink.geometry.coords[0]])
                    mesolink.geometry_xy = geometry.LineString([ib_mesolink.geometry_xy.coords[-1], ob_mesolink.geometry_xy.coords[0]])

                    self.mesonet.link_dict[mesolink.link_id] = mesolink
                    max_mesolink_id += 1

                    mesolink.from_node.outgoing_link_list.append(mesolink)
                    mesolink.to_node.incoming_link_list.append(mesolink)

                    self.createMicroNetForConnector(mesolink, ib_mesolink, ib_lane_index_start, ob_mesolink, ob_lane_index_start)
                else:
                    if ib_link.downstream_is_target and not ob_link.upstream_is_target:
                        # remove incoming micro nodes and links of ob_mesolink, then connect to ib_mesolink
                        ib_mesolink_to_node = ib_mesolink.to_node
                        ob_mesolink_from_node = ob_mesolink.from_node
                        ob_mesolink.from_node = ib_mesolink_to_node
                        ob_mesolink.geometry = geometry.LineString([ib_mesolink.geometry.coords[-1]] + ob_mesolink.geometry.coords[1:])
                        ob_mesolink.geometry_xy = geometry.LineString([ib_mesolink.geometry_xy.coords[-1]] + ob_mesolink.geometry_xy.coords[1:])
                        del self.mesonet.node_dict[ob_mesolink_from_node.node_id]

                        for i in range(number_of_lanes):
                            ib_lane_index = ib_lane_index_start + i
                            ob_lane_index = ob_lane_index_start + i
                            ib_mesolink_outgoing_micro_node = ib_mesolink.micronode_list[ib_lane_index][-1]
                            ob_mesolink_incoming_micro_node = ob_mesolink.micronode_list[ob_lane_index][0]
                            for microlink in ob_mesolink_incoming_micro_node.outgoing_link_list:
                                microlink.from_node = ib_mesolink_outgoing_micro_node
                            del self.micronet.node_dict[ob_mesolink_incoming_micro_node.node_id]
                    elif not ib_link.downstream_is_target and ob_link.upstream_is_target:
                        # remove outgoing micro nodes and links of ib_mesolink, then connect to ob_mesolink
                        ib_mesolink_to_node = ib_mesolink.to_node
                        ob_mesolink_from_node = ob_mesolink.from_node
                        ib_mesolink.to_node = ob_mesolink_from_node
                        ib_mesolink.geometry = geometry.LineString(ib_mesolink.geometry.coords[:-1] + [ob_mesolink.geometry.coords[0]])
                        ib_mesolink.geometry_xy = geometry.LineString(ib_mesolink.geometry_xy.coords[:-1] + [ob_mesolink.geometry_xy.coords[0]])
                        del self.mesonet.node_dict[ib_mesolink_to_node.node_id]

                        for i in range(number_of_lanes):
                            ib_lane_index = ib_lane_index_start + i
                            ob_lane_index = ob_lane_index_start + i
                            ib_mesolink_outgoing_micro_node = ib_mesolink.micronode_list[ib_lane_index][-1]
                            ob_mesolink_incoming_micro_node = ob_mesolink.micronode_list[ob_lane_index][0]
                            for microlink in ib_mesolink_outgoing_micro_node.incoming_link_list:
                                microlink.to_node = ob_mesolink_incoming_micro_node
                            del self.micronet.node_dict[ib_mesolink_outgoing_micro_node.node_id]
                    else:
                        sys.exit('Target link defintion error')

        self.mesonet.max_link_id = max_mesolink_id





    def generateNet(self):
        self.createMesoNodeForCentriod()
        self.createNormalLinks()
        self.connectMesoLinksMVMT()

