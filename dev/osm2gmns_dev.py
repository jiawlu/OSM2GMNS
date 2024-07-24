import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import osm2gmns as og

map_folder = r'dev/maps/yuba'

map_name = 'map.osm.pbf'

net = og.getNetFromFile(os.path.join(map_folder, map_name),
                        link_types=['motorway', 'trunk', 'primary', 'secondary'],
                        connector_link_types=['tertiary'])

og.consolidateComplexIntersections(net, auto_identify=True)

og.generateNodeActivityInfo(net)

og.outputNetToCSV(net, map_folder)

