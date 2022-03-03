osm2gmns
====================================
| **Authors**: Jiawei Lu, Xuesong (Simon) Zhou
| **Email**: jiaweil9@asu.edu, xzhou74@asu.edu


osm2gmns is an open-source Python package that enables users to conveniently obtain and 
manipulate any networks from `OpenStreetMap`_ (OSM). With a single line of Python code, 
users can obtian and model drivable, bikeable, walkable, railway, and aeroway networks 
for any regions in the world, and output networks to csv files in `GMNS`_ format for seamless
data sharing and research collaboration. osm2gmns mainly focus on providing researchers and 
practitioners with flexible, standard and ready-to-use multi-module transportation networks, 
as well as a bunch of customized and practical functions to facilitate various reseaches 
and applications on traffic modeling.


Main Features
====================================

- Obtain any networks from OSM. osm2gmns parses map data from OSM and output networks to 
  csv files in GMNS format.
- Standard network format. osm2gmns adopts GMNS as the network format for seamless data 
  sharing and research collaboration.
- Ready-to-use network. osm2gmns cleans erroneous information from osm map data and is able 
  to fill up critical missing values, i.e., lanes, speed and capacity, to quickly provide 
  ready-to-use networks.
- Directed network. two directed road links are generated for each bi-directional osm ways identified by osm2gmns
- Multi-module support. five different network types are supported, including auto, bike, walk, railway, and aeroway
- Customized and practical functions to facilitate traffic modeling. functions include 
  complex intersection consolidation, moevement generation, traffic zone creation, short link combination, 
  network visualization.
- Multi-Resolution modeling. osm2gmns automatically construct the corresponding mesoscopic and microscopic
  networks for any macroscopic network in GMNS format.


Contents
====================================

.. toctree::
   :maxdepth: 2

   installation
   gmns
   mrm
   quick-start
   functions
   sample-net
   acknowledgement


For program source code and sample network files, readers can visit the project  `homepage`_
at ASU Trans+AI Lab Github. Interested readers can also check the `link`_ for our online
transportation modelling visualization platform, in which network data is provided by osm2gmns.



.. _`OpenStreetMap`: https://www.openstreetmap.org/
.. _`GMNS`: https://github.com/zephyr-data-specs/GMNS
.. _`homepage`: https://github.com/asu-trans-ai-lab
.. _`link`: https://asu-trans-ai-lab.github.io/website_openlayer_4GMNS/