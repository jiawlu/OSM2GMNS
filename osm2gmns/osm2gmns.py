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
    library_name = "libosm2gmns.dll"
    os.add_dll_directory(os.path.join(os.path.dirname(__file__), "dlls"))
elif current_os == "Linux":
    library_name = "libosm2gmns.so"
else:
    raise OSError("Unsupported operating system")

oglib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), library_name))


def initlib():
    oglib.initializeAbslLoggingPy.argtypes = []

    oglib.getNetFromFilePy.argtypes = [ctypes.c_char_p,
                                       ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                       ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                       ctypes.c_bool, ctypes.c_float,
                                       ctypes.c_bool]
    oglib.getNetFromFilePy.restype = ctypes.c_void_p

    oglib.consolidateComplexIntersectionsPy.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_char_p, ctypes.c_float]

    oglib.generateNodeActivityInfoPy.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    oglib.outputNetToCSVPy.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    oglib.getNumberOfNodesPy.argtypes = [ctypes.c_void_p]
    oglib.getNumberOfNodesPy.restype = ctypes.c_uint64
    oglib.getNumberOfLinksPy.argtypes = [ctypes.c_void_p]
    oglib.getNumberOfLinksPy.restype = ctypes.c_uint64

    oglib.initializeAbslLoggingPy()


class Network:
    def __init__(self):
        self.cnet = None

    @property
    def number_of_nodes(self):
        return oglib.getNumberOfNodesPy(self.cnet)

    @property
    def number_of_links(self):
        return oglib.getNumberOfLinksPy(self.cnet)


def getNetFromFile(filename='map.osm', link_types=(), connector_link_types=(), POI=False, POI_sampling_ratio=1.0,
                   strict_boundary=True):
    network = Network()

    link_types_byte_string = [link_type.encode() for link_type in link_types]
    link_types_arr = (ctypes.c_char_p * len(link_types_byte_string))(*link_types_byte_string)
    connector_link_types_byte_string = [link_type.encode() for link_type in connector_link_types]
    connector_link_types_arr = (ctypes.c_char_p * len(connector_link_types_byte_string))(*connector_link_types_byte_string)
    network.cnet = oglib.getNetFromFilePy(filename.encode(),
                                          link_types_arr, len(link_types_arr),
                                          connector_link_types_arr, len(connector_link_types_arr),
                                          POI, POI_sampling_ratio,
                                          strict_boundary)

    return network


def consolidateComplexIntersections(network, auto_identify=False, intersection_file='', int_buffer=20.0):
    oglib.consolidateComplexIntersectionsPy(network.cnet, auto_identify, intersection_file.encode(), int_buffer)


def generateNodeActivityInfo(network, zone_file=''):
    oglib.generateNodeActivityInfoPy(network.cnet, zone_file.encode())


def outputNetToCSV(network, output_folder=''):
    oglib.outputNetToCSVPy(network.cnet, output_folder.encode())
