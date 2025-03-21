osm2gmns
====================================
| **Authors**: Jiawei Lu, Xuesong (Simon) Zhou
| **Email**: lujiaweiwk@gmail.com, xzhou74@asu.edu


osm2gmns is an open-source Python package that enables users to conveniently obtain and 
manipulate any networks from `OpenStreetMap`_ (OSM). The core of osm2gmns is written using
c++ for efficiency and the package is wrapped in Python for ease of use.

With a single line of Python code, 
users can obtain and model drivable, bikeable, walkable, railway, and aeroway networks 
for any region in the world and output networks to CSV files in `GMNS`_ format for seamless 
data sharing and research collaboration. osm2gmns mainly focuses on providing researchers and 
practitioners with flexible, standard and ready-to-use multi-modal transportation networks, 
as well as a bunch of customized and practical functions to facilitate various research 
and applications on traffic modeling.

.. note::

osm2gmns v1.x is not fully backward compatible with v0.x. In v1.x, the core of osm2gmns is
rewritten in c++ for efficiency. In addition, many new features and functionalities are introduced,
therefore, public API functions are changed accordingly. Users should refer to the correct
version of user guide for the corresponding version of osm2gmns.

As of today, the multi-resolution modeling (MRM) feature is not available in osm2gmns v1.x yet.
Users who need MRM should use osm2gmns v0.x. The user guide for osm2gmns v0.x can be found
`here`_.

Publication
====================================

Lu, J., & Zhou, X.S. (2023). Virtual track networks: A hierarchical modeling framework and 
open-source tools for simplified and efficient connected and automated mobility (CAM) system 
design based on general modeling network specification (GMNS). Transportation Research 
Part C: Emerging Technologies, 153, 104223. `paper link`_

If you use osm2gmns in your work, please cite the above paper.

Main Features
====================================

- Obtain any networks from OSM. osm2gmns parses map data from OSM and output networks to 
  csv files in GMNS format.
- Standard network format. osm2gmns adopts GMNS as the network format for seamless data 
  sharing and research collaboration.
- Ready-to-use network. osm2gmns cleans erroneous information from OSM map data and is able 
  to fill up critical missing values, e.g., lanes, speed and capacity, to quickly provide 
  ready-to-use networks.
- Directed network. two directed links are generated for each bi-directional osm ways identified by osm2gmns.
- Multi-modal support. five different network types are supported, including auto, bike, walk, railway, and aeroway
- Customized and practical functions to facilitate traffic modeling. functions include 
  complex intersection consolidation, moevement generation, traffic zone creation, short link combination, 
  network visualization.
- Multi-resolution modeling. osm2gmns automatically constructs the corresponding mesoscopic and microscopic
  networks for any macroscopic networks in GMNS format.


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
transportation modelling visualization platform, in which network data are provided by osm2gmns.



.. _`OpenStreetMap`: https://www.openstreetmap.org/
.. _`GMNS`: https://github.com/zephyr-data-specs/GMNS
.. _`here`: https://doi.org/10.1016/j.trc.2023.104223
.. _`paper link`: https://doi.org/10.1016/j.trc.2023.104223
.. _`homepage`: https://github.com/asu-trans-ai-lab
.. _`link`: https://asu-trans-ai-lab.github.io/website_openlayer_4GMNS/
