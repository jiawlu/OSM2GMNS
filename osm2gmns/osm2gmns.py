# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2/17/23 3:02 PM
# @desc         [script description]


import platform
import ctypes
import os

current_os = platform.system()
if current_os == "Darwin":
    library_name = "libosm2gmns.dylib"
elif current_os == "Windows":
    library_name = "osm2gmns.dll"
elif current_os == "Linux":
    library_name = "libosm2gmns.so"
else:
    raise OSError("Unsupported operating system")

oglib = None
try:
    oglib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), library_name))
except OSError:
    print("failed to load osm2gmns dynamic library.")


class StrIntDict(ctypes.Structure):
    _fields_ = [("key", ctypes.c_char_p), ("value", ctypes.c_int)]

class StrFloatDict(ctypes.Structure):
    _fields_ = [("key", ctypes.c_char_p), ("value", ctypes.c_float)]


def initlib():
    if oglib is None:
        return
    
    oglib.initializeAbslLoggingPy.argtypes = []

    oglib.releaseNetworkMemoryPy.argtypes = [ctypes.c_void_p]

    oglib.getNetFromFilePy.argtypes = [ctypes.c_char_p,
                                       ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                       ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                       ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                       ctypes.c_bool, ctypes.c_float,
                                       ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                       ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                       ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                       ctypes.c_bool]
    oglib.getNetFromFilePy.restype = ctypes.c_void_p

    oglib.consolidateComplexIntersectionsPy.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_char_p, ctypes.c_float]

    oglib.generateNodeActivityInfoPy.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    oglib.fillLinkAttributesWithDefaultValuesPy.argtypes = [ctypes.c_void_p,
                                                            ctypes.c_bool, ctypes.POINTER(StrIntDict), ctypes.c_size_t,
                                                            ctypes.c_bool, ctypes.POINTER(StrFloatDict), ctypes.c_size_t,
                                                            ctypes.c_bool, ctypes.POINTER(StrIntDict), ctypes.c_size_t]

    oglib.outputNetToCSVPy.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    oglib.getNumberOfNodesPy.argtypes = [ctypes.c_void_p]
    oglib.getNumberOfNodesPy.restype = ctypes.c_uint64
    oglib.getNumberOfLinksPy.argtypes = [ctypes.c_void_p]
    oglib.getNumberOfLinksPy.restype = ctypes.c_uint64

    oglib.initializeAbslLoggingPy()


class Network:
    def __init__(self):
        self.cnet = None

    def __del__(self):
        oglib.releaseNetworkMemoryPy(self.cnet)

    @property
    def number_of_nodes(self):
        return oglib.getNumberOfNodesPy(self.cnet)

    @property
    def number_of_links(self):
        return oglib.getNumberOfLinksPy(self.cnet)


def _checkStringToTuple(arg_val):
    return (arg_val,) if isinstance(arg_val, str) else arg_val

def getNetFromFile(filename='map.osm', mode_types=('auto',), link_types=(), connector_link_types=(), POI=False, POI_sampling_ratio=1.0,
                   osm_node_attributes=(), osm_link_attributes=(), osm_poi_attributes=(),
                   strict_boundary=True, **kwargs):
    """
    Get an osm2gmns Network object from an osm file

    Parameters
    ----------
    filename: str
        path of an osm file; can be absolute or relative path; supported osm file formats: .osm, .xml, and .pbf
    network_types: str, tuple of strings, list of strings, or set of strings
        osm2gmns supports five different network types, including auto, bike, walk, railway, and aeroway.
        network_types can be any one or any combinations of the five supported network types
    link_types: str, tuple of strings, list of strings, or set of strings
        supported link types: motorway, trunk, primary, secondary, tertiary, residential, service, cycleway,
        footway, track, unclassified, connector, railway, and aeroway.
    POI: bool
        if extract point of interest information
    POI_sampling_ratio: float
        prcentage of POIs to be extracted if POI is set as True. this value should be a float number between 0.0 and 1.0.
    strict_mode: bool
        if True, network elements (node, link, poi) outside the boundary will be discarded
    offset: str
        offset overlapping links. the value of this argument can be 'left', 'right', or 'no'
    min_nodes: int
        a network return by the function may contain several sub-networks that are disconnected from each other.
        sub-networks with the number of nodes less than min_nodes will be discarded
    combine: bool
        if True, adjacent short links with the same attributes will be combined into a long link. the operation will only
        be performed on short links connected with a two-degree nodes (one incoming link and one outgoing link)
    bbox: tuple of four float/int values, list of four float/int values, None
        specify the boundary of the network to be extracted, consisting of minimum latitude, minimum longtitude, maximum latitude, and maximum longitud.
        if None, osm2gmns will try to find network boundary from the input osm file
    default_lanes: bool, dict
        if True, assign a default value for links without lanes information based on built-in settings. if a dict,
        assign a default value for links without lanes information based on the dict passed by users.
    default_speed: bool, dict
        if True, assign a default value for links without speed information based on built-in settings. if a dict,
        assign a default value for links without speed information based on the dict passed by users.
    default_capacity: bool, dict
        if True, assign a default value for links without capacity information based on built-in settings. if a dict,
        assign a default value for links without capacity information based on the dict passed by users.
    start_node_id: int
        osm2gmns assigns node_ids to generated nodes starting from start_node_id.
    start_link_id: int
        osm2gmns assigns link_ids to generated links starting from start_link_id

    Returns
    -------
    network: Network
        osm2gmns Network object
    """
        
    network = Network()

    mode_types_ = _checkStringToTuple(mode_types)
    if 'network_types' in kwargs:
        print('[WARNING] deprecated argument network_types, please use mode_types.')
        mode_types_ = _checkStringToTuple(kwargs['network_types'])
    mode_types_byte_string = [mode_type.encode() for mode_type in _checkStringToTuple(mode_types_)]
    mode_types_arr = (ctypes.c_char_p * len(mode_types_byte_string))(*mode_types_byte_string)

    link_types_byte_string = [link_type.encode() for link_type in _checkStringToTuple(link_types)]
    link_types_arr = (ctypes.c_char_p * len(link_types_byte_string))(*link_types_byte_string)
    connector_link_types_byte_string = [link_type.encode() for link_type in _checkStringToTuple(connector_link_types)]
    connector_link_types_arr = (ctypes.c_char_p * len(connector_link_types_byte_string))(*connector_link_types_byte_string)

    osm_node_attributes_byte_string = [attr.encode() for attr in _checkStringToTuple(osm_node_attributes)]
    osm_node_attributes_arr = (ctypes.c_char_p * len(osm_node_attributes_byte_string))(*osm_node_attributes_byte_string)
    osm_link_attributes_byte_string = [attr.encode() for attr in _checkStringToTuple(osm_link_attributes)]
    osm_link_attributes_arr = (ctypes.c_char_p * len(osm_link_attributes_byte_string))(*osm_link_attributes_byte_string)
    osm_poi_attributes_byte_string = [attr.encode() for attr in _checkStringToTuple(osm_poi_attributes)]
    osm_poi_attributes_arr = (ctypes.c_char_p * len(osm_poi_attributes_byte_string))(*osm_poi_attributes_byte_string)

    network.cnet = oglib.getNetFromFilePy(filename.encode(),
                                          mode_types_arr, len(mode_types_arr),
                                          link_types_arr, len(link_types_arr),
                                          connector_link_types_arr, len(connector_link_types_arr),
                                          POI, POI_sampling_ratio,
                                          osm_node_attributes_arr, len(osm_node_attributes_arr),
                                          osm_link_attributes_arr, len(osm_link_attributes_arr),
                                          osm_poi_attributes_arr, len(osm_poi_attributes_arr),
                                          strict_boundary)
    return network


def consolidateComplexIntersections(network, auto_identify=False, intersection_file='', int_buffer=20.0):
    """
    Consolidate each complex intersection that are originally represented by multiple nodes in osm into one node. Nodes
    with the same intersection_id will be consolidated into one node. intersection_id of nodes can be obtained in three ways.

    (1) set the argument auto_identify as True, then osm2gmns will automatically identify complex intersections and assign
    intersection_id for corresponding nodes.

    (2) provide an intersection file that specifies the central position (required) and buffer (optional) of each complex intersection.

    (3) user can assign intersection_id to nodes manually in network csv files (node.csv), and load the network using function loadNetFromCSV provided by osm2gmns.

    The priority of the three approaches is (3) > (2) > (1).
    Rules used in the approach (1) to identify if two nodes belong to a complex intersection: (a) ctrl_type of the two nodes must be signal;
    (b) there is a link connecting these two nodes, and the length of the link is shorter than or equal to the argument int_buffer.

    Parameters
    ----------
    network: Network
        osm2gmns Network object
    auto_identify: bool
        if automatically identify complex intersections using built-in methods in osm2gmns. nodes that belong to a complex
        intersection will be assigned with the same intersection_id
    intersection_file: str
        path of an intersction csv file that specifies complex intersections. required fields: central position of intersections
        (in the form of x_coord and y_coord); optional field: int_buffer (if not specified, the global int_buffer will be used,
        i.e., the forth arugment). For each record in the intersection_file, osm2gmns consolidates all nodes with a distance to the
        central position shorter than buffer.
    int_buffer: float
        the threshold used to check if two nodes belong to one complex intersection. the unit is meter

    Returns
    -------
    None
    """

    oglib.consolidateComplexIntersectionsPy(network.cnet, auto_identify, intersection_file.encode(), int_buffer)


def generateNodeActivityInfo(network, zone_file=''):
    """
    Generate activity information, including activity_type, is_boundary, zone_id for nodes. activity_type includes
    motorway, primary, secondary, tertiary, residential, etc, and is determined by adjacent links,
    If a zone_file is provided, zone_id of boundary nodes will be determined by zones defined in the zone_file.
    Otherwise, for each boundary node, its node_id will be used as zone_id.

    Parameters
    ----------
    network: Network
        osm2gmns Network object
    zone_file: str, None
        filename of the zone file. optional

    Returns
    -------
    None
    """

    oglib.generateNodeActivityInfoPy(network.cnet, zone_file.encode())


def fillLinkAttributesWithDefaultValues(network, default_lanes=False, default_lanes_dict={}, default_speed=False, default_speed_dict={}, default_capacity=False, default_capacity_dict={}):
    """
    Generate activity information, including activity_type, is_boundary, zone_id for nodes. activity_type includes
    motorway, primary, secondary, tertiary, residential, etc, and is determined by adjacent links,
    If a zone_file is provided, zone_id of boundary nodes will be determined by zones defined in the zone_file.
    Otherwise, for each boundary node, its node_id will be used as zone_id.

    Parameters
    ----------
    network: Network
        osm2gmns Network object
    zone_file: str, None
        filename of the zone file. optional

    Returns
    -------
    None
    """

    default_lanes_dict_ = (StrIntDict * len(default_lanes_dict))(*[(k.encode(), v) for k, v in default_lanes_dict.items()])
    default_speed_dict_ = (StrFloatDict * len(default_speed_dict))(*[(k.encode(), v) for k, v in default_speed_dict.items()])
    default_capacity_dict_ = (StrIntDict * len(default_capacity_dict))(*[(k.encode(), v) for k, v in default_capacity_dict.items()])
    oglib.fillLinkAttributesWithDefaultValuesPy(network.cnet,
                                                default_lanes, default_lanes_dict_, len(default_lanes_dict_),
                                                default_speed, default_speed_dict_, len(default_speed_dict_),
                                                default_capacity, default_capacity_dict_, len(default_capacity_dict_))


def outputNetToCSV(network, output_folder=''):
    """
    Output an osm2gmns network object to csv files in GMNS format

    Parameters
    ----------
    network: Network
        an osm2gmns network object
    output_folder: str
        path of the folder to store network files. can be an absolute or a relative path
    prefix: str
        prefix of output csv files
    projection: bool
        if True, osm2gmns will project the network to a local coordinate system when ouptting a network
    encoding: str
        the file encoding used to output a network

    Returns
    -------
    None
    """
    
    oglib.outputNetToCSVPy(network.cnet, output_folder.encode())
