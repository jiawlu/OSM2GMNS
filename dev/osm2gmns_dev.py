import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import osm2gmns as og

map_folder = r'test_dev/maps/yuba'
net = og.getNetFromFile(os.path.join(map_folder, 'map.osm.pbf'))
og.outputNetToCSV(net, map_folder)

