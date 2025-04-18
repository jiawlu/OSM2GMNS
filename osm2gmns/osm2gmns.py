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

def getNetFromFile(filepath, mode_types='auto', link_types=[], connector_link_types=[], POI=False, POI_sampling_ratio=1.0,
                   osm_node_attributes=[], osm_link_attributes=[], osm_poi_attributes=[],
                   strict_boundary=True):
    """
    Read and parse an osm file.

    Parameters
    ----------
    filepath: str
        path of an osm file. supported osm file formats: ``.osm``, ``.xml``, and ``.pbf``.
    mode_types: str or list of str, default 'auto'
        osm2gmns supports five different mode types, including auto, bike, walk, railway, and aeroway.
        mode_types can be any one or any combinations of the five supported mode types.
    link_types: str or list of str, default []
        supported link types: motorway, trunk, primary, secondary, tertiary, residential, service, cycleway,
        footway, track, unclassified, connector, railway, and aeroway. an empty list means all link 
        types are included.
    connector_link_types: str or list of str, default []
        supported connector link types: same as argument link_types. a link with its type in the 
        connector_link_types will be included in the resulting network only if it is directly connected to 
        another link with its type in the link_types. It is very useful when users want to keep some links
        connected to the main network for traffic zone modeling purposes. An empty list means no connector
        links.
    POI: bool, default False
        if parse point of interest information.
    POI_sampling_ratio: float, default 1.0
        prcentage of POIs to be extracted if POI is set as True. this value should be a float number between 0.0 and 1.0.
    osm_node_attributes: str or list of str, default []
        when parsing osm node data, osm2gmns will extract important pre-defined attributes, such as node_id, name.
        If users want to extract other attributes, they can specify the attribute names in this argument.
    osm_link_attributes: str or list of str, default []
        similar to the argument osm_node_attributes, but for link attributes.
    osm_poi_attributes: str or list of str, default []
        similar to the argument osm_node_attributes, but for POI attributes.
    strict_boundary: bool, default True
        typically, a link will be included in the map file from osm database if part of the link 
        lies in the region that users defined. True, link segments that outside the region will be 
        cut off when parsing osm data. Otherwise, all links in the map file will be completely parsed and imported.

    Returns
    -------
    network: Network
        osm2gmns Network object
    """
        
    network = Network()

    mode_types_byte_string = [mode_type.encode() for mode_type in _checkStringToTuple(mode_types)]
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

    network.cnet = oglib.getNetFromFilePy(filepath.encode(),
                                          mode_types_arr, len(mode_types_arr),
                                          link_types_arr, len(link_types_arr),
                                          connector_link_types_arr, len(connector_link_types_arr),
                                          POI, POI_sampling_ratio,
                                          osm_node_attributes_arr, len(osm_node_attributes_arr),
                                          osm_link_attributes_arr, len(osm_link_attributes_arr),
                                          osm_poi_attributes_arr, len(osm_poi_attributes_arr),
                                          strict_boundary)
    return network


def consolidateComplexIntersections(network, auto_identify=False, intersection_filepath=None, int_buffer=20.0):
    """
    Consolidate each complex intersection that are originally represented by multiple nodes in osm into one node. 
    osm2gmns support the following three ways to define complex intersections.

    (1) set the argument auto_identify as True, then osm2gmns will automatically identify complex intersections and assign
    intersection_id for corresponding nodes.

    (2) provide an intersection file that specifies the central position (required) and buffer (optional) of each complex intersection.

    (3) if the target network is loaded from csv files using function loadNetFromCSV. before loading the network, 
    the user can specify complex intersection information in the node.csv file. Nodes with the same intersection_id 
    will be considered as belonging to the same complex intersection.

    The priority of the three approaches is (3) > (2) > (1).

    Parameters
    ----------
    network: Network
        osm2gmns Network object
    auto_identify: bool, default False
        if automatically identify complex intersections using built-in methods in osm2gmns.
        Rules to identify if two nodes belong to a complex intersection: (a) ctrl_type of the two nodes must be signal, and
        (b) there is a link connecting these two nodes, and the length of the link is shorter than or equal to the argument int_buffer.
    intersection_filepath: str or None, default None
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

    oglib.consolidateComplexIntersectionsPy(network.cnet, 
                                            auto_identify, 
                                            intersection_filepath.encode() if intersection_filepath is not None else '', 
                                            int_buffer)


def generateNodeActivityInfo(network, zone_filepath=None):
    """
    Generate node activity information, including activity_type, is_boundary, zone_id for nodes. activity_type includes
    motorway, primary, secondary, tertiary, residential, etc, and is determined by adjacent links.

    Parameters
    ----------
    network: Network
        osm2gmns Network object
    zone_filepath: str or None, default None
        filepath of a zone file. If a zone_file is provided, zone_id of boundary nodes will be determined by the 
        information provided in the zone_file. Otherwise, for each boundary node, its node_id will be used as zone_id.
        format of the zone_file: csv file with the following fields: "zone_id", "x_coord", "y_coord", "geometry".
        geometry can be POINT, POLYGON, or MULTIPOLYGON with WKT format. users can also use x_coord and y_coord to
        provide POINT information.
        for each boundary node, osm2gmns will find the zone (POLYGON or MULTIPOLYGON) that contains the node and assign 
        the zone_id to the node. if the node is not in any zone, osm2gmns will find the nearest POINT and assign corresponding
        zone_id.

    Returns
    -------
    None
    """

    oglib.generateNodeActivityInfoPy(network.cnet,
                                     zone_filepath.encode() if zone_filepath is not None else '')


def fillLinkAttributesWithDefaultValues(network, 
                                        default_lanes=False, default_lanes_dict={}, 
                                        default_speed=False, default_speed_dict={}, 
                                        default_capacity=False, default_capacity_dict={}):
    """
    Fill link attributes with default values. If a link does not have a specific attribute,
    osm2gmns will assign a default value for the attribute. The default value is determined by the link type.
    Users can also provide a dictionary to overwrite the built-in default values for each link type.
    The key is the link_type, and the value is the default value for the link type.

    Parameters
    ----------
    network: Network
        osm2gmns Network object    
    default_lanes: bool, default False
        if True, assign a default lanes value for links without lanes information.
    default_lanes_dict: dict
        users can provide a dictionary to overwrite built-in default values for lanes.
        No need to provide a default value for each link type. only provide a default value for each link type that needs to be overwritten.
    default_speed: bool, default False
        if True, assign a default speed value for links without speed information.
    default_speed_dict: dict
        smilar to the argument default_lanes_dict, but for speed.
    default_capacity: bool, default False
        if True, assign a default capacity value for links without capacity information.
    default_capacity_dict: dict
        similar to the argument default_lanes_dict, but for capacity.

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
        path of the folder to store network files.

    Returns
    -------
    None
    """
    
    oglib.outputNetToCSVPy(network.cnet, output_folder.encode())
