# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2/17/23 3:02 PM
# @desc         [script description]


import ctypes

# libfile = r"../osm2gmns_c/cmake-build-release-clang/libosm2gmns.dylib"
libfile = r"../osm2gmns_c/build/libosm2gmns.dylib"
# libfile = r"../osm2gmns_c/build/lib.macosx-11.1-arm64-cpython-311/osm2gmns.pyd"
mylib = ctypes.CDLL(libfile)


def initlib():
    mylib.getNetFromFilePy.argtypes = [ctypes.c_char_p, ctypes.c_bool]
    mylib.getNetFromFilePy.restype = ctypes.c_void_p

    mylib.outputNetToCSVPy.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    mylib.getNumberOfNodesPy.argtypes = [ctypes.c_void_p]
    mylib.getNumberOfNodesPy.restype = ctypes.c_int32
    mylib.getNumberOfLinksPy.argtypes = [ctypes.c_void_p]
    mylib.getNumberOfLinksPy.restype = ctypes.c_int32


class Network:
    def __init__(self):
        self.cnet = None

    @property
    def number_of_nodes(self):
        return mylib.getNumberOfNodesPy(self.cnet)

    @property
    def number_of_links(self):
        return mylib.getNumberOfLinksPy(self.cnet)


def getNetFromFile(filename='map.osm', network_types=('auto',), link_types='all', POI=False, POI_sampling_ratio=1.0,
                   strict_mode=True, offset='no', min_nodes=1, combine=False, bbox=None,
                   default_lanes=False, default_speed=False, default_capacity=False, start_node_id=0, start_link_id=0):
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

    # if og_settings.verbose:
    #     print('arguments used for network parsing:')
    #     print(f'  filename: {filename}')
    #     print(f'  network_types: {network_types}')
    #     print(f'  link_types: {link_types}')
    #     print(f'  POI: {POI}')
    #     print(f'  POI_sampling_ratio: {POI_sampling_ratio}')
    #     print(f'  strict_mode: {strict_mode}')
    #     print(f'  offset: {offset}')
    #     print(f'  min_nodes: {min_nodes}')
    #     print(f'  combine: {combine}')
    #     print(f'  bbox: {bbox}')
    #     print(f'  default_lanes: {default_lanes}')
    #     print(f'  default_speed: {default_speed}')
    #     print(f'  default_capacity: {default_capacity}')
    #     print(f'  start_node_id: {start_node_id}')
    #     print(f'  start_link_id: {start_link_id}\n')
    #
    #     print('Building Network from OSM file')

    # network_types_, link_types_, POI_, POI_sampling_ratio_, strict_mode_, offset_, min_nodes_, combine_, \
    #     bbox_, default_lanes_, default_speed_, default_capacity_, start_node_id_, start_link_id_ = \
    #     checkArgs_getNetFromFile(filename, network_types, link_types, POI, POI_sampling_ratio, strict_mode, offset,
    #                              min_nodes, combine, bbox, default_lanes, default_speed, default_capacity, start_node_id,
    #                              start_link_id)

    network = Network()
    network.cnet = mylib.getNetFromFilePy(filename.encode(), POI)

    return network


def outputNetToCSV(network, output_folder='', prefix='', projection=False, encoding=None):
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

    mylib.outputNetToCSVPy(network.cnet, output_folder.encode())

    # if og_settings.verbose:
    #     print('Outputting Network Files')
    #
    # if output_folder:
    #     if not os.path.isdir(output_folder): os.mkdir(output_folder)
    #
    # node_filename = f'{prefix}node.csv'
    # _outputNode(network, output_folder, node_filename, projection, encoding)
    #
    # link_filename = f'{prefix}link.csv'
    # _outputLink(network, output_folder, link_filename, projection, encoding)
    #
    # movement_filename = f'{prefix}movement.csv'
    # _outputMovement(network, output_folder, movement_filename, projection, encoding)
    #
    # poi_filename = f'{prefix}poi.csv'
    # _outputPOI(network, output_folder, poi_filename, projection, encoding)
    #
    # if network.mesonet is not None:
    #     outputMesoNet(network.mesonet, output_folder, prefix, projection, encoding)
    # if network.micronet is not None:
    #     outputMicroNet(network.micronet, output_folder, prefix, projection, encoding)
