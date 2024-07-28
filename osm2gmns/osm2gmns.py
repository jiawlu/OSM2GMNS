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

oglib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), library_name))


class StrIntDict(ctypes.Structure):
    _fields_ = [("key", ctypes.c_char_p), ("value", ctypes.c_int)]

class StrFloatDict(ctypes.Structure):
    _fields_ = [("key", ctypes.c_char_p), ("value", ctypes.c_float)]


def initlib():
    oglib.initializeAbslLoggingPy.argtypes = []

    oglib.releaseNetworkMemoryPy.argtypes = [ctypes.c_void_p]

    oglib.getNetFromFilePy.argtypes = [ctypes.c_char_p,
                                       ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                       ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                       ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                       ctypes.c_bool, ctypes.c_float,
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
                   strict_boundary=True, **kwargs):
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

    network.cnet = oglib.getNetFromFilePy(filename.encode(),
                                          mode_types_arr, len(mode_types_arr),
                                          link_types_arr, len(link_types_arr),
                                          connector_link_types_arr, len(connector_link_types_arr),
                                          POI, POI_sampling_ratio,
                                          strict_boundary)
    return network


def consolidateComplexIntersections(network, auto_identify=False, intersection_file='', int_buffer=20.0):
    oglib.consolidateComplexIntersectionsPy(network.cnet, auto_identify, intersection_file.encode(), int_buffer)


def generateNodeActivityInfo(network, zone_file=''):
    oglib.generateNodeActivityInfoPy(network.cnet, zone_file.encode())


def fillLinkAttributesWithDefaultValues(network, default_lanes=False, default_lanes_dict={}, default_speed=False, default_speed_dict={}, default_capacity=False, default_capacity_dict={}):
    default_lanes_dict_ = (StrIntDict * len(default_lanes_dict))(*[(k.encode(), v) for k, v in default_lanes_dict.items()])
    default_speed_dict_ = (StrFloatDict * len(default_speed_dict))(*[(k.encode(), v) for k, v in default_speed_dict.items()])
    default_capacity_dict_ = (StrIntDict * len(default_capacity_dict))(*[(k.encode(), v) for k, v in default_capacity_dict.items()])
    oglib.fillLinkAttributesWithDefaultValuesPy(network.cnet,
                                                default_lanes, default_lanes_dict_, len(default_lanes_dict_),
                                                default_speed, default_speed_dict_, len(default_speed_dict_),
                                                default_capacity, default_capacity_dict_, len(default_capacity_dict_))


def outputNetToCSV(network, output_folder=''):
    oglib.outputNetToCSVPy(network.cnet, output_folder.encode())
