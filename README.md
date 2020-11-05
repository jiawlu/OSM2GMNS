# OSM2GMNS
OSM2GMNS is a open-source python package which can help users easily transform networks from [OpenStreetMap](https://www.openstreetmap.org/) to .csv files with standard [GMNS](https://github.com/zephyr-data-specs/GMNS) format for visualization, traffic simulation and planning purpose.

# Install
Install OSM2GMNS via pip
```shell
pip install osm2gmns
```

# Simple example
Get network from map.osm file and consolidate complex intersections

    >>> net = og.getNetFromOSMFile('map.osm')
    # output node.csv, link.csv and complex_intersection.csv (automatically generated complex intersection information)
    >>> og.outputNetToCSV(net)  

    # check and modify (if necessary) complex_intersection.csv before complex intersection consolidation
    >>> net = og.getNetFromCSV()
    >>> og.consolidateComplexIntersections(net, external_file='complex_intersection.csv')
    >>> og.outputNetToCSV(net, output_folder='consolidated')

# Visualization
You can visualize generated networks using [NeXTA](https://github.com/xzhou99/NeXTA-GMNS) or [QGis](https://qgis.org/)

![visualization in NeXTA.](https://github.com/jiawei92/OSM2GMNS/blob/master/test/asu.PNG)

