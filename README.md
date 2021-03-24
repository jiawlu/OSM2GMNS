# OSM2GMNS

OSM2GMNS is an open-source python package which can help users easily convert
networks from [OpenStreetMap](https://www.openstreetmap.org/) to .csv files with
standard [GMNS](https://github.com/zephyr-data-specs/GMNS) format for
visualization, traffic simulation and planning purpose.

# Install

Install OSM2GMNS via pip

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
pip install osm2gmns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Simple example

Create a network from map.osm file and consolidate complex intersections

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
>>> net = og.getNetFromOSMFile('map.osm')
# output node.csv, link.csv and complex_intersection.csv (automatically generated complex intersection information)
>>> og.outputNetToCSV(net)  

# check and modify (if necessary) network files before complex intersection consolidation
>>> net = og.getNetFromCSV()
>>> og.consolidateComplexIntersections(net)
>>> og.outputNetToCSV(net, output_folder='consolidated')
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Visualization and user Guide 

You can visualize generated networks using
[NeXTA](https://github.com/asu-trans-ai-lab/DTALite/tree/main/release) or [QGIS](https://qgis.org/)
and check out user guide at https://github.com/asu-trans-ai-lab/QGIS_NeXTA4GMNS

![](<https://github.com/jiawei92/OSM2GMNS/blob/master/test/asu.PNG>)

# latest source code 
https://github.com/jiawei92/OSM2GMNS/tree/master/osm2gmns


