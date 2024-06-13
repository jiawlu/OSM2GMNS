from osm2gmns.osmnet.build_net import getNetFromFile
from osm2gmns.osmnet.combine_links import combineShortLinks
from osm2gmns.osmnet.complex_intersection import consolidateComplexIntersections
from osm2gmns.osmnet.enrich_net_info import generateNodeActivityInfo, generateLinkVDFInfo
from osm2gmns.osmnet.pois import connectPOIWithNet
from osm2gmns.osmnet.visualization import show, saveFig
from osm2gmns.movement.generate_movements import generateMovements
from osm2gmns.multiresolutionnet.build_mrnet import buildMultiResolutionNets
from osm2gmns.io.load_from_csv import loadNetFromCSV
from osm2gmns.io.downloader import downloadOSMData
from osm2gmns.io.writefile import outputNetToCSV
from osm2gmns.utils.util import config
from osm2gmns.func_lib.extract_relation_id import getOSMRelationID
import osm2gmns.settings as og_settings


__version__ = '0.7.6'
print(f'osm2gmns, {__version__}')

__all__ = [
    'getNetFromFile',
    'combineShortLinks',
    'consolidateComplexIntersections',
    'generateNodeActivityInfo',
    'generateLinkVDFInfo',
    'connectPOIWithNet',
    'show',
    'saveFig',
    'generateMovements',
    'buildMultiResolutionNets',
    'loadNetFromCSV',
    'downloadOSMData',
    'outputNetToCSV',
    'config',
    'getOSMRelationID',
    'og_settings'
]



# todo: railway allowed_use

# todo: turns
# todo: parse speed

# todo: link_id: int, str
# todo: compatible with networkx
# todo: mrnet bike walk
# todo: movement generation

# todo: default speed railway

# todo: og.link_types
# todo: combine_link remove segment

# TODO: find global relation id locally (user can update locally as well)