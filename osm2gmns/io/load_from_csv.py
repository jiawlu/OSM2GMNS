from osm2gmns.networkclass.macronet import Node, Link, Movement, Segment, POI, Network
from osm2gmns.movement.util_mvmt import getMovementDescription, getMovementGeometry
from osm2gmns.utils.util_coord import from_latlon
from osm2gmns.utils.util_geo import GeoTransformer
import osm2gmns.settings as og_settings
import os
import csv
import sys
import numpy as np
from shapely import wkt, geometry


_node_required_fields = {'node_id', 'x_coord', 'y_coord'}
_node_optional_fields = {'name', 'osm_node_id', 'osm_highway', 'zone_id', 'ctrl_type', 'node_type', 'activity_type', 'is_boundary', 'intersection_id', 'poi_id', 'notes'}
_link_required_fields = {'link_id', 'from_node_id', 'to_node_id', 'lanes'}
_link_optional_fields = {'name', 'osm_way_id', 'dir_flag', 'length', 'free_speed', 'capacity', 'link_type_name', 'link_type', 'geometry', 'allowed_uses', 'from_biway', 'is_link', 'VDF_fftt1', 'VDF_cap1'}
_mvmt_required_fields = {'mvmt_id', 'node_id', 'ib_link_id', 'start_ib_lane', 'end_ib_lane', 'ob_link_id', 'start_ob_lane', 'end_ob_lane'}
_mvmt_optional_fields = {'osm_node_id', 'name', 'lanes', 'ib_osm_node_id', 'ob_osm_node_id', 'type', 'penalty', 'capacity', 'ctrl_type', 'mvmt_txt_id', 'geometry', 'volume', 'free_speed', 'allowed_uses','generated_by_osm2gmns'}
_segment_required_fields = {'segment_id', 'link_id', 'ref_node_id', 'start_lr', 'end_lr', 'l_lanes_added', 'r_lanes_added'}
_segment_optional_fields = {'grade', 'capacity', 'free_speed', 'lanes', 'bike_facility', 'ped_facility', 'parking', 'allowed_uses', 'toll', 'jurisdiction', 'row_width', 'opt_comment'}


def _loadNodes(network, node_filepath, coordinate_type, encoding):
    if encoding is None:
        fin = open(node_filepath, 'r')
    else:
        fin = open(node_filepath, 'r', encoding=encoding)
    reader = csv.DictReader(fin)

    fieldnames = reader.fieldnames.copy()
    if '' in fieldnames:
        print('WARNING: columns with an empty header are detected in the node file. these columns will be skipped')
        fieldnames = [fieldname for fieldname in fieldnames if fieldname]
    
    fieldnames_set = set(fieldnames)
    if len(fieldnames) > len(fieldnames_set):
        print('WARNING: columns with duplicate header names are detected in the node file. please check')

    for field in _node_required_fields:
        if field not in fieldnames_set:
            sys.exit(f'ERROR: required field ({field}) does not exist in the node file')
    other_fields = list(fieldnames_set.difference(_node_required_fields.union(_node_optional_fields)))

    max_node_id = network.max_node_id
    max_intersection_id = network.max_intersection_id
    node_id_list = []
    node_coord_list = []
    node_dict = {}
    for node_info in reader:
        # required
        node = Node(int(node_info['node_id']))
        if node.node_id > max_node_id: max_node_id = node.node_id

        x_coord, y_coord = float(node_info['x_coord']), float(node_info['y_coord'])
        if coordinate_type == 'lonlat':
            node.geometry = geometry.Point(round(x_coord, og_settings.lonlat_coord_precision), round(y_coord, og_settings.lonlat_coord_precision))
            node_id_list.append(node.node_id)
            node_coord_list.append((x_coord, y_coord))
        elif coordinate_type == 'meter':
            node.geometry_xy = geometry.Point(round(x_coord, og_settings.local_coord_precision), round(y_coord, og_settings.local_coord_precision))
        elif coordinate_type == 'feet':
            node.geometry_xy = geometry.Point(round(x_coord*0.3048, og_settings.local_coord_precision), round(y_coord*0.3048, og_settings.local_coord_precision))

        # optional
        name = node_info['name'] if 'name' in reader.fieldnames else None
        if name: node.name = name
        osm_node_id = node_info['osm_node_id'] if 'osm_node_id' in reader.fieldnames else None
        if osm_node_id: node.osm_node_id = osm_node_id
        osm_highway = node_info['osm_highway'] if 'osm_highway' in reader.fieldnames else None
        if osm_highway: node.osm_highway = osm_highway
        zone_id = node_info['zone_id'] if 'zone_id' in reader.fieldnames else None
        if zone_id: node.zone_id = int(zone_id)

        ctrl_type = node_info['ctrl_type'] if 'ctrl_type' in reader.fieldnames else None
        if ctrl_type: node.ctrl_type = ctrl_type
        node_type = node_info['node_type'] if 'node_type' in reader.fieldnames else None
        if node_type: node.node_type = node_type
        activity_type = node_info['activity_type'] if 'activity_type' in reader.fieldnames else None
        if activity_type: node.activity_type = activity_type
        is_boundary = node_info['is_boundary'] if 'is_boundary' in reader.fieldnames else None
        if is_boundary: node.is_boundary = int(is_boundary)

        intersection_id = node_info['intersection_id'] if 'intersection_id' in reader.fieldnames else None
        if intersection_id:
            node.intersection_id = int(intersection_id)
            if node.intersection_id > max_intersection_id:
                max_intersection_id = node.intersection_id

        poi_id = node_info['poi_id'] if 'poi_id' in reader.fieldnames else None
        if poi_id: node.poi_id = poi_id
        notes = node_info['notes'] if 'notes' in reader.fieldnames else None
        if notes: node.notes = notes

        # others
        for field in other_fields:
            node.other_attrs[field] = node_info[field]

        node_dict[node.node_id] = node
    fin.close()

    max_node_id += 1
    max_intersection_id += 1

    if coordinate_type == 'lonlat':
        coord_array = np.array(node_coord_list)
        central_lon = coord_array[:,0].mean()
        central_lat = coord_array[:,1].mean()
        northern = True if central_lat >= 0 else False

        xs, ys = from_latlon(coord_array[:,0], coord_array[:,1], central_lon)
        xs, ys = np.round(xs, og_settings.local_coord_precision), np.round(ys, og_settings.local_coord_precision)

        for node_no, node_id in enumerate(node_id_list):
            node = node_dict[node_id]
            node.geometry_xy = geometry.Point((xs[node_no],ys[node_no]))

        network.GT = GeoTransformer(central_lon, central_lat, northern)

    network.node_dict = node_dict
    network.max_node_id = max_node_id
    network.max_intersection_id = max_intersection_id
    network.node_other_attrs = other_fields


def _loadLinks(network, link_filepath, coordinate_type, encoding):
    if encoding is None:
        fin = open(link_filepath, 'r')
    else:
        fin = open(link_filepath, 'r', encoding=encoding)
    reader = csv.DictReader(fin)

    fieldnames = reader.fieldnames.copy()
    if '' in fieldnames:
        print('WARNING: columns with an empty header are detected in the link file. these columns will be skipped')
        fieldnames = [fieldname for fieldname in fieldnames if fieldname]
    
    fieldnames_set = set(fieldnames)
    if len(fieldnames) > len(fieldnames_set):
        print('WARNING: columns with duplicate header names are detected in the link file. please check')

    for field in _link_required_fields:
        if field not in fieldnames_set:
            sys.exit(f'ERROR: required field ({field}) does not exist in the link file')
    other_fields = list(fieldnames_set.difference(_link_required_fields.union(_link_optional_fields)))

    node_dict = network.node_dict
    GT = network.GT

    max_link_id = network.max_link_id
    link_dict = {}
    for link_info in reader:
        # required
        link = Link(int(link_info['link_id']))
        if link.link_id > max_link_id: max_link_id = link.link_id

        from_node_id, to_node_id = int(link_info['from_node_id']), int(link_info['to_node_id'])
        if from_node_id == to_node_id:
            print(f'WARNING: from_node and to_node of link {link.link_id} are the same')
            continue

        try:
            link.from_node = node_dict[from_node_id]
        except KeyError:
            print(f'WARNING: from_node {from_node_id} of link {link.link_id} does not exist in the node file')
            continue
        try:
            link.to_node = node_dict[to_node_id]
        except KeyError:
            print(f'WARNING: to_node {to_node_id} of link {link.link_id} does not exist in the node file')
            continue

        lanes = link_info['lanes']
        if lanes:
            link.lanes_list = [int(lanes)]
        else:
            link.lanes_list = [None]

        # optional
        name = link_info['name'] if 'name' in reader.fieldnames else None
        if name: link.name = name
        osm_way_id = link_info['osm_way_id'] if 'osm_way_id' in reader.fieldnames else None
        if osm_way_id: link.osm_way_id = osm_way_id
        dir_flag = link_info['dir_flag'] if 'dir_flag' in reader.fieldnames else None
        if dir_flag: link.dir_flag = int(dir_flag)

        free_speed = link_info['free_speed'] if 'free_speed' in reader.fieldnames else None
        if free_speed: link.free_speed = float(free_speed)
        capacity = link_info['capacity'] if 'capacity' in reader.fieldnames else None
        if capacity: link.capacity = float(capacity)

        link_type_name = link_info['link_type_name'] if 'link_type_name' in reader.fieldnames else None
        if link_type_name: link.link_type_name = link_type_name
        link_type = link_info['link_type'] if 'link_type' in reader.fieldnames else None
        if link_type:
            try:
                link.link_type = int(link_type)
            except ValueError:
                print(f'WARNING: link_type {link_type} of link {link.link_id} is not an integer')

        geometry_str = link_info['geometry'] if 'geometry' in reader.fieldnames else None
        if geometry_str:
            if coordinate_type == 'lonlat':
                link.geometry = wkt.loads(geometry_str)
                if not link.geometry.is_valid:
                    print(f'WARNING: link {link.link_id} geometry is not a valid LineString')
                    continue
                link.geometry_xy = GT.geo_from_latlon(link.geometry)
            elif coordinate_type == 'meter':        # todo
                pass
            elif coordinate_type == 'feet':         # todo
                pass

        allowed_uses = link_info['allowed_uses'] if 'allowed_uses' in reader.fieldnames else None
        if allowed_uses: link.allowed_uses = allowed_uses.split(';')

        from_biway = link_info['from_biway'] if 'from_biway' in reader.fieldnames else None
        if from_biway:
            if from_biway == '1':
                link.from_bidirectional_way = True
            elif from_biway == '0':
                link.from_bidirectional_way = False

        is_link = link_info['is_link'] if 'is_link' in reader.fieldnames else None
        if is_link:
            if is_link == '1':
                link.is_link = True
            elif is_link == '0':
                link.is_link = False

        VDF_fftt1 = link_info['VDF_fftt1'] if 'VDF_fftt1' in reader.fieldnames else None
        if VDF_fftt1: link.VDF_fftt1 = float(VDF_fftt1)
        VDF_cap1 = link_info['VDF_cap1'] if 'VDF_cap1' in reader.fieldnames else None
        if VDF_cap1: link.VDF_cap1 = float(VDF_cap1)

        # others
        for field in other_fields:
            link.other_attrs[field] = link_info[field]

        link_dict[link.link_id] = link
        link.from_node.outgoing_link_list.append(link)
        link.to_node.incoming_link_list.append(link)

    fin.close()
    max_link_id += 1

    network.max_link_id = max_link_id
    network.link_dict = link_dict
    network.link_other_attrs = other_fields


def _loadMovements(network, movement_filepath, coordinate_type, encoding):
    if encoding is None:
        fin = open(movement_filepath, 'r')
    else:
        fin = open(movement_filepath, 'r', encoding=encoding)
    reader = csv.DictReader(fin)

    for field in _mvmt_required_fields:
        if field not in reader.fieldnames:
            sys.exit(f'ERROR: required field ({field}) does not exist in the movement file')
    other_fields = list(set(reader.fieldnames).difference(_mvmt_required_fields.union(_mvmt_optional_fields)))

    node_dict = network.node_dict
    link_dict = network.link_dict
    GT = network.GT

    max_movement_id = network.max_movement_id

    for movement_info in reader:
        # required
        movement = Movement(int(movement_info['mvmt_id']))
        if movement.movement_id > max_movement_id: max_movement_id = movement.movement_id

        node_id = int(movement_info['node_id'])
        try:
            node = node_dict[node_id]
        except KeyError:
            print(f'WARNING: node {node_id} of movement {movement.movement_id} does not exist in the node file')
            continue

        ib_link_id = int(movement_info['ib_link_id'])
        try:
            ib_link = link_dict[ib_link_id]
        except KeyError:
            print(f'WARNING: ib_link {ib_link_id} of movement {movement.movement_id} does not exist in the link file')
            continue
        if ib_link.lanes is None:
            print(f'WARNING: ib_link {ib_link_id} of movement {movement.movement_id} does not have lanes information')
            continue
        start_ib_lane = int(movement_info['start_ib_lane'])
        if start_ib_lane > ib_link.lanes:
            print(f'WARNING: start_ib_lane of movement {movement.movement_id} is larger than total lanes of ib_link {ib_link_id}')
            continue
        end_ib_lane_str = movement_info['end_ib_lane']
        end_ib_lane = int(end_ib_lane_str) if end_ib_lane_str else start_ib_lane

        ob_link_id = int(movement_info['ob_link_id'])
        try:
            ob_link = link_dict[ob_link_id]
        except KeyError:
            print(f'WARNING: ob_link {ob_link_id} of movement {movement.movement_id} does not exist in the link file')
            continue
        if ob_link.lanes is None:
            print(f'WARNING: ob_link {ob_link_id} of movement {movement.movement_id} does not have lanes information')
            continue
        start_ob_lane = int(movement_info['start_ob_lane'])
        if start_ob_lane > ob_link.lanes:
            print(f'WARNING: start_ob_lane of movement {movement.movement_id} is larger than total lanes of ob_link {ob_link_id}')
            continue
        end_ob_lane_str = movement_info['end_ob_lane']
        end_ob_lane = int(end_ob_lane_str) if end_ob_lane_str else start_ob_lane

        ib_lanes, ob_lanes = end_ib_lane - start_ib_lane + 1, end_ob_lane - start_ob_lane + 1
        if ib_lanes != ob_lanes:
            print(f'WARNING: ib_lanes ({ib_lanes}) and ob_lanes ({ob_lanes}) of movement {movement.movement_id} are not consistent')
            continue
        movement.lanes = ib_lanes

        movement.ib_link, movement.start_ib_lane, movement.end_ib_lane = ib_link, start_ib_lane, end_ib_lane
        movement.ob_link, movement.start_ob_lane, movement.end_ob_lane = ob_link, start_ob_lane, end_ob_lane

        # optional
        type_file = movement_info['type'] if 'type' in reader.fieldnames else None
        mvmt_txt_id_file = movement_info['mvmt_txt_id'] if 'mvmt_txt_id' in reader.fieldnames else None
        if type_file and mvmt_txt_id_file:
            movement.type, movement.mvmt_txt_id = type_file, mvmt_txt_id_file
        else:
            mvmt_txt_id, mvmt_type = getMovementDescription(ib_link, ob_link)
            movement.type = type_file if type_file else mvmt_type
            movement.mvmt_txt_id = mvmt_txt_id_file if mvmt_txt_id_file else mvmt_txt_id

        penalty = movement_info['penalty'] if 'penalty' in reader.fieldnames else None
        if penalty: movement.penalty = float(penalty)
        capacity = movement_info['capacity'] if 'capacity' in reader.fieldnames else None
        if capacity: movement.capacity = float(capacity)
        ctrl_type = movement_info['ctrl_type'] if 'ctrl_type' in reader.fieldnames else None
        if ctrl_type: movement.ctrl_type = ctrl_type
        volume = movement_info['volume'] if 'volume' in reader.fieldnames else None
        if volume: movement.volume = float(volume)
        free_speed = movement_info['free_speed'] if 'free_speed' in reader.fieldnames else None
        if free_speed: movement.free_speed = float(free_speed)
        allowed_uses = movement_info['allowed_uses'] if 'allowed_uses' in reader.fieldnames else None
        if allowed_uses: movement.allowed_uses = allowed_uses.split(';')
        generated_by_osm2gmns = movement_info['generated_by_osm2gmns'] if 'generated_by_osm2gmns' in reader.fieldnames else None
        if generated_by_osm2gmns:
            if generated_by_osm2gmns == '1':
                movement.generated_by_osm2gmns = True
            elif generated_by_osm2gmns == '0':
                movement.generated_by_osm2gmns = False

        geometry_str = movement_info['geometry'] if 'geometry' in reader.fieldnames else None
        if geometry_str:
            if coordinate_type == 'lonlat':
                movement.geometry = wkt.loads(geometry_str)
                movement.geometry_xy = GT.geo_from_latlon(movement.geometry)
            elif coordinate_type == 'meter':        # todo
                pass
            elif coordinate_type == 'feet':         # todo
                pass
        else:
            if coordinate_type == 'lonlat':
                movement.geometry_xy = getMovementGeometry(ib_link, ob_link)
                movement.geometry = GT.geo_to_latlon(movement.geometry_xy)
            elif coordinate_type == 'meter':        # todo
                pass
            elif coordinate_type == 'feet':         # todo
                pass

        # others
        for field in other_fields:
            movement.other_attrs[field] = movement_info[field]

        node.movement_list.append(movement)

    fin.close()
    max_movement_id += 1

    network.max_movement_id = max_movement_id
    network.movement_other_attrs = other_fields


def _loadSegments(network, segment_filepath, encoding):
    if encoding is None:
        fin = open(segment_filepath, 'r')
    else:
        fin = open(segment_filepath, 'r', encoding=encoding)
    reader = csv.DictReader(fin)

    for field in _segment_required_fields:
        if field not in reader.fieldnames:
            sys.exit(f'ERROR: required field ({field}) does not exist in the segment file')
    other_fields = list(set(reader.fieldnames).difference(_segment_required_fields.union(_segment_optional_fields)))

    node_dict = network.node_dict
    link_dict = network.link_dict

    max_segment_id = network.max_segment_id

    for segment_info in reader:
        # required
        segment = Segment(int(segment_info['segment_id']))
        if segment.segment_id > max_segment_id: max_segment_id = segment.segment_id

        link_id = int(segment_info['link_id'])
        try:
            link = link_dict[link_id]
        except KeyError:
            print(f'WARNING: link {link_id} of segment {segment.segment_id} does not exist in the link file')
            continue

        if link.lanes is None:
            print(f'WARNING: link {link_id} of segment {segment.segment_id} does not have lanes information')
            continue

        segment.link = link

        ref_node_id = int(segment_info['ref_node_id'])
        try:
            ref_node = node_dict[ref_node_id]
        except KeyError:
            print(f'WARNING: ref_node {ref_node_id} of segment {segment.segment_id} does not exist in the node file')
            continue
        segment.ref_node = ref_node

        segment.start_lr = float(segment_info['start_lr'])
        segment.end_lr = float(segment_info['end_lr'])
        segment.l_lanes_added = int(segment_info['l_lanes_added'])
        segment.r_lanes_added = int(segment_info['r_lanes_added'])

        # optional

        # others
        for field in other_fields:
            segment.other_attrs[field] = segment_info[field]

        link.segment_list.append(segment)

    fin.close()
    max_segment_id += 1

    network.max_segment_id = max_segment_id
    network.segment_other_attrs = other_fields


def _loadGeometries(network, geometry_filepath, encoding):
    pass


def _loadPOIs(network, poi_filepath, encoding):
    if encoding is None:
        fin = open(poi_filepath, 'r')
    else:
        fin = open(poi_filepath, 'r', encoding=encoding)
    reader = csv.DictReader(fin)

    max_poi_id = network.max_poi_id
    GT = network.GT

    POI_list = []
    for poi_info in reader:
        poi = POI()
        name = poi_info['name']
        if name: poi.name = name
        poi.poi_id = int(poi_info['poi_id'])
        if poi.poi_id > max_poi_id: max_poi_id = poi.poi_id
        osm_way_id = poi_info['osm_way_id']
        if osm_way_id: poi.osm_way_id = osm_way_id
        osm_relation_id = poi_info['osm_relation_id']
        if osm_relation_id: poi.osm_relation_id = osm_relation_id
        building = poi_info['building']
        if building: poi.building = building
        amenity = poi_info['amenity']
        if amenity: poi.amenity = amenity
        leisure = poi_info['leisure']
        if leisure: poi.leisure = leisure
        way = poi_info['way']
        if way: poi.way = way

        poi.geometry = wkt.loads(poi_info['geometry'])
        lon, lat = poi.geometry.centroid.x, poi.geometry.centroid.y
        poi.centroid = geometry.Point((round(lon,og_settings.lonlat_coord_precision),round(lat,og_settings.lonlat_coord_precision)))

        poi.geometry_xy = GT.geo_from_latlon(poi.geometry)
        x, y = poi.geometry_xy.centroid.x, poi.geometry_xy.centroid.y
        poi.centroid_xy = geometry.Point((round(x,og_settings.local_coord_precision),round(y,og_settings.local_coord_precision)))

        POI_list.append(poi)

    fin.close()
    max_poi_id += 1

    network.max_poi_id = max_poi_id


def loadNetFromCSV(folder='', node_file=None, link_file=None, movement_file=None,
                   segment_file=None, geometry_file=None, POI_file=None,
                   coordinate_type='lonlat', enconding=None):
    """
    Load a network from csv files in GMNS format

    Parameters
    ----------
    folder: str
        the folder where network files are stored
    node_file: str
        filename of the node file. required
    link_file: str
        filename of the link file. required
    movement_file: str, None
        filename of the movement file. optional
    segment_file: str, None
        filename of the segment file. optional
    geometry_file: str, None
        filename of the geometry file. optional
    POI_file: str, None
        filename of the POI file. optional
    coordinate_type: str
        the coordinate system used by the network to be loaded. can be lonlat, meter, feet
    enconding: str, None
        the encoding used by the network files. if None, osm2gmns will use the default encoding of the local operating system

    Returns
    -------
    network: Network
        an osm2gmns Network object

    """

    if node_file is None:
        sys.exit('ERROR: node_file is not specified')
    node_filepath = os.path.join(folder, node_file)
    if not os.path.isfile(node_filepath):
        sys.exit(f'ERROR: cannot open node_file {node_filepath}')

    if link_file is None:
        sys.exit('ERROR: link_file is not specified')
    link_filepath = os.path.join(folder, link_file)
    if not os.path.isfile(link_filepath):
        sys.exit(f'ERROR: cannot open link_file {link_filepath}')

    if movement_file is not None:
        movement_filepath = os.path.join(folder, movement_file)
        if not os.path.isfile(movement_filepath):
            sys.exit(f'ERROR: cannot open movement_file {movement_filepath}')
    else:
        movement_filepath = None

    if segment_file is not None:
        segment_filepath = os.path.join(folder, segment_file)
        if not os.path.isfile(segment_filepath):
            sys.exit(f'ERROR: cannot open segment_file {segment_filepath}')
    else:
        segment_filepath = None

    if geometry_file is not None:
        geometry_filepath = os.path.join(folder, geometry_file)
        if not os.path.isfile(geometry_filepath):
            sys.exit(f'ERROR: cannot open geometry_file {geometry_filepath}')
    else:
        geometry_filepath = None

    if POI_file is not None:
        POI_filepath = os.path.join(folder, POI_file)
        if not os.path.isfile(POI_filepath):
            sys.exit(f'ERROR: cannot open POI_file {POI_filepath}')
    else:
        POI_filepath = None

    network = Network()

    if og_settings.verbose:
        print('Loading Network From CSV Files')

    _loadNodes(network, node_filepath, coordinate_type, enconding)

    _loadLinks(network, link_filepath, coordinate_type, enconding)

    if movement_file is not None:
        _loadMovements(network, movement_filepath, coordinate_type, enconding)

    if segment_file is not None:
        _loadSegments(network, segment_filepath, enconding)

    if geometry_file is not None:
        _loadGeometries(network, geometry_filepath, enconding)

    if POI_file is not None:
        _loadPOIs(network, POI_filepath, enconding)

    return network