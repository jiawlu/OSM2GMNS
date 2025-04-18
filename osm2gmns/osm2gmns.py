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
    Parses an OpenStreetMap file and creates a transportation network object.

    Parameters
    ----------
    filepath : str
        Path to the input OSM file (.osm, .xml, or .pbf format).
    mode_types : str or list of str
        Specifies the transportation modes to include. Options: 'auto', 'bike',
        'walk', 'railway', 'aeroway'. Can be a single string or a list of strings.
    link_types : str or list of str
        Filters the network to include only specified OSM link types. If 
        empty, all relevant link types for the selected `mode_types` are included.
        Supported types include: 'motorway', 'trunk', 'primary', 'secondary',
        'tertiary', 'residential', 'service', 'cycleway', 'footway', 'track',
        'unclassified', 'connector', 'railway', 'aeroway'.
    connector_link_types : str or list of str
        Specifies link types that should only be included if they connect directly
        to links included via `link_types`. Useful for connecting main networks
        to specific areas (e.g., for traffic zones). Same supported types as
        `link_types`. If empty, no connector links are specifically handled
        this way.
    POI : bool
        If True, extracts Points of Interest (POIs) from the OSM data.
    POI_sampling_ratio : float
        Fraction of POIs to extract if POI is True. Must be between 0.0 and 1.0.
    osm_node_attributes : str or list of str
        List of additional OSM tag keys whose values should be extracted as attributes
        for nodes. If empty, only default attributes are extracted.
    osm_link_attributes : str or list of str
        List of additional OSM tag keys whose values should be extracted as attributes
        for links. If empty, only default attributes are extracted.
    osm_poi_attributes : str or list of str
        List of additional OSM tag keys whose values should be extracted as attributes
        for POIs. If empty, only default attributes are extracted.
    strict_boundary : bool
        If True, clips links that cross the boundary of the downloaded OSM region.
        If False, includes the full geometry of any link that partially falls
        within the region.

    Returns
    -------
    Network
        An osm2gmns Network object containing the parsed transportation network data.
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
    Consolidates multiple OSM nodes representing a single complex intersection into one node.

    Simplifies network topology by merging nodes that form complex junctions,
    often found at large, signalized intersections in OSM data. Consolidation
    can be based on (1) automatic detection, (2) an external file defining intersections,
    or (3) pre-assigned 'intersection_id' attributes in nodes (if network is loaded from CSV,
    nodes with the same 'intersection_id' will be considered as belonging to the same
    complex intersection).

    Priority for defining intersections: (3) Pre-existing 'intersection_id' in nodes,
    (2) `intersection_filepath`, (1) `auto_identify`.

    Parameters
    ----------
    network : Network
        The osm2gmns Network object to modify.
    auto_identify : bool
        If True, attempts to automatically identify complex intersections based on
        built-in rules: nodes must have 'ctrl_type' = 'signal' and be connected
        by a link shorter than or equal to `int_buffer`.
    intersection_filepath : str or None
        Path to a CSV file defining complex intersections. Required columns:
        'x_coord', 'y_coord' (defining the intersection center). Optional column:
        'int_buffer' (overrides the global `int_buffer` for that specific intersection).
        Nodes within the buffer distance of a defined center will be consolidated.
    int_buffer : float
        The distance threshold (in meters) used for consolidation. Applied globally
        if `auto_identify` is True, or per-intersection if not specified in the
        `intersection_filepath`.

    Returns
    -------
    None
        Modifies the input `network` object in place.
    """

    oglib.consolidateComplexIntersectionsPy(network.cnet, 
                                            auto_identify, 
                                            intersection_filepath.encode() if intersection_filepath is not None else '', 
                                            int_buffer)


def generateNodeActivityInfo(network, zone_filepath=None):
    """
    Generates activity_type, is_boundary, zone_id for nodes in the network.

    Analyzes the network topology to assign relevant attributes to nodes, useful
    for transportation modeling. 'activity_type' (e.g., 'motorway', 'residential')
    is inferred from adjacent links. 'is_boundary' indicates if a node is at the
    edge of the defined network area. 'zone_id' assigns nodes to traffic analysis
    zones (TAZs).

    Parameters
    ----------
    network : Network
        The osm2gmns Network object to modify.
    zone_filepath : str or None
        Path to a zone definition file (CSV). If provided, 'zone_id' for boundary
        nodes is determined based on this file. Otherwise, the 'node_id' is used
        as the 'zone_id' for boundary nodes.
        Expected CSV fields: "zone_id", "x_coord", "y_coord", "geometry".
        'geometry' should be in WKT format (POINT, POLYGON, or MULTIPOLYGON).
        'x_coord' and 'y_coord' can alternatively define POINT geometry.
        Boundary nodes are assigned the 'zone_id' of the containing polygon/multipolygon,
        or the nearest point zone if not within any polygon.

    Returns
    -------
    None
        Modifies the input `network` object in place by adding or updating node attributes.
    """

    oglib.generateNodeActivityInfoPy(network.cnet,
                                     zone_filepath.encode() if zone_filepath is not None else '')


def fillLinkAttributesWithDefaultValues(network, 
                                        default_lanes=False, default_lanes_dict={}, 
                                        default_speed=False, default_speed_dict={}, 
                                        default_capacity=False, default_capacity_dict={}):
    """
    Assigns default values to link attributes (lanes, speed, capacity) if they are missing.

    Populates essential link attributes based on 'link_type' for links where
    this information wasn't available in the source OSM data. Users can rely on
    built-in defaults or provide dictionaries to override them for specific link types.

    Parameters
    ----------
    network : Network
        The osm2gmns Network object to modify.
    default_lanes : bool
        If True, assign default lane counts to links missing this attribute.
    default_lanes_dict : dict
        A dictionary mapping link types (str) to default lane counts (int).
        Overrides built-in defaults for the specified link types. Example: 
        {'motorway': 3, 'primary': 3}.
    default_speed : bool
        If True, assign default speed limits (km/h) to links
        missing this attribute.
    default_speed_dict : dict
        A dictionary mapping link types (str) to default speed limits (float).
        Overrides built-in defaults. Example: {'residential': 20.0}.
    default_capacity : bool
        If True, assign default capacities (vehicles per hour per lane) to links
        missing this attribute.
    default_capacity_dict : dict
        A dictionary mapping link types (str) to default capacities (int).
        Overrides built-in defaults. Example: {'primary': 1800}.

    Returns
    -------
    None
        Modifies the input `network` object in place by adding or updating link attributes.
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
    Exports the network object data to CSV files in GMNS format.

    Writes network information into
    separate CSV files (node.csv, link.csv, poi.csv) adhering to the
    General Modeling Network Specification (GMNS).

    Parameters
    ----------
    network : Network
        The osm2gmns Network object containing the data to be exported.
    output_folder : str
        The directory path where the CSV files will be saved. If empty or not
        provided, defaults to the current working directory.

    Returns
    -------
    None
        Creates CSV files in the specified output folder.
    """
    
    oglib.outputNetToCSVPy(network.cnet, output_folder.encode())
