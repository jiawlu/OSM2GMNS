from .network import *
from .complex_intersection import *
from .consolidate_intersections import *
from .activity import *
from .writefile import *
from .settings import *



print('osm2gmns, version 0.2.0')

if print_log:
    logging.basicConfig(level=print_log_level,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='osm2gmns.log',
                        filemode='w')