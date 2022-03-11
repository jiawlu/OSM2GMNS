# OSM2GMNS

OSM2GMNS is an open-source python package which can help users easily convert
networks from [OpenStreetMap](https://www.openstreetmap.org/) to .csv files with
standard [GMNS](https://github.com/zephyr-data-specs/GMNS) format for
visualization, traffic simulation and planning purpose.

# Problem
As discussed in the article by Dr. David Ory at https://medium.com/zephyrfoundation/osmnx-software-badge-3e206db65825, a key feature of a travel model is an explicit representation of space. OpenStreetMap has been a theoretically-appealing option for creating travel model base maps. Practically, however, OpenStreetMap has not been useful for at least the following reasons:
1. it is not routable, 2. the structure of its attributes are not aligned with travel models, and 3. the attribute data is not sufficiently complete.
The OSMnx package created by Geoff Boeing elegantly solves the first of these problems. OSM2GMNS aims to further address the second challenge using GMNS  format. https://github.com/zephyr-data-specs/GMNS 

# Solution
OpenStreetMap (OSM) is a free, open-source, editable map website that can provide free downloads. osm2gmns, as a data conversion tool, can directly convert the OSM map data to node and link network files in the GMNS format. Users can convert and model drivable, walkable, railway, or aeroway networks with a few lines of Python code.

The related package net2cell aims to help users automatically generate hybrid (macroscopic, mesoscopic and microscopic) transportation networks to accommodate different modelling need.
https://asu-trans-ai-lab.github.io/website_openlayer_4GMNS/

Related youtube videos:
https://www.youtube.com/watch?v=xEdrbuiOozs
Building and Visualizing a Model from Scratch with OSM2GMNS and QGIS, contributed by Rachel Dai, a high school student at Arizona
https://www.youtube.com/watch?v=6hoYJtEaTn4

# Install

Install OSM2GMNS via pip

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
pip install osm2gmns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Simple example

Our latest user guide can be found at 
https://osm2gmns.readthedocs.io/en/latest/ 

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


# Contributions
Any contributions are welcomed including advise new applications of osm2gmns, enhance documentation (this guideline and docstrings in the source code), refactor and/or optimize the source code, report and/or resolve potential issues/bugs, suggest and/or add new functionalities, etc.

OSM2GMNS has a very simple workflow setup, i.e., master for release (on both GitHub and PyPI) and dev for development. If you would like to work directly on the source code (and probably the documentation), please make sure that the destination branch of your pull request is dev, i.e., all potential changes/updates shall go to the dev branch before merging into master for release.

You are encouraged to join our Slack workspace at https://www.democracylab.org/projects/639  for more discussions and collaborations.

At the current stage, the following contributions are highly appreciated. 
1. Code reivew and optimization. 
2. Test users: Three packages of osm2gmns, signal2gmns and path2gmns need to be systematically tested in the different subareas, multiple modes and cities, in combination or separately.
3. Data visualization. Our current QGIS and NEXTA version is at  https://github.com/asu-trans-ai-lab/QGIS_NeXTA4GMNS
4. Developers are needed for integrating this set of tools to simulators such as AB streets, MATSIM or SUMO. 


# Visualization and user guide 

You can visualize generated networks using
[NeXTA](https://github.com/asu-trans-ai-lab/DTALite/tree/main/release) or [QGIS](https://qgis.org/)
and check out user guide at https://github.com/asu-trans-ai-lab/QGIS_NeXTA4GMNS

![](<https://github.com/jiawei92/OSM2GMNS/blob/master/test/asu.PNG>)

# latest source code 
https://github.com/jiawei92/OSM2GMNS/tree/master/osm2gmns


