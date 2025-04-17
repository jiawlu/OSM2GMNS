osm2gmns
====================================
| **Authors**: `Jiawei Lu`_, `Xuesong (Simon) Zhou`_
| **Email**: lujiaweiwk@gmail.com, xzhou74@asu.edu


osm2gmns is a high-performance Python package that transforms `OpenStreetMap`_ (OSM) 
data into standardized transportation networks. With its C++ core wrapped in Python, 
osm2gmns combines computational efficiency with ease of use, allowing researchers 
and practitioners to obtain detailed multi-modal networks with minimal effort.

With just a few lines of Python code, users can obtain and model drivable, bikeable, 
walkable, railway, and aeroway networks for any region in the world. The package 
outputs networks in `GMNS`_ (General Modeling Network Specification) format, facilitating 
seamless data sharing and collaboration within the transportation research community.

.. code-block:: python

    >>> import osm2gmns as og
    >>> net = og.getNetFromFile('map.osm')
    >>> og.outputNetToCSV(net)

.. note::
    osm2gmns v1.x is not fully backward compatible with v0.x due to significant 
    architectural changes and new features. The multi-resolution modeling (MRM) 
    feature is currently available only in v0.x. For MRM functionality, please 
    refer to the `v0.x user guide`_.


Key Features
====================================

1. Performance and Usability

- High-Performance Core: Written in C++ for maximum computational efficiency
- Intuitive Python Interface: Simple API makes complex network extraction straightforward
- Ready-to-Use Networks: Automatic inference of critical attributes (lanes, speed, capacity)

2. Comprehensive Network Modeling

- Multi-Modal Support: Generate networks for vehicles, bicycles, pedestrians, railways, and aeroways
- Directed Network Generation: Automatic creation of directional links for bidirectional roadways
- GMNS Compatibility: Standardized output format for interoperability with other tools

3. Advanced Functionality

- Intersection Consolidation: Simplifies complex junctions for various modeling needs
- Movement Generation: Creates turning movements at intersections
- Traffic Zone Creation: Supports origin-destination modeling
- Short Link Combination: Improves network topology for simulation
- Network Visualization: Built-in tools for visual inspection and verification


Citation
====================================

If you use osm2gmns in your research, please cite:

Lu, J., & Zhou, X.S. (2023). Virtual track networks: A hierarchical modeling framework and 
open-source tools for simplified and efficient connected and automated mobility (CAM) system 
design based on general modeling network specification (GMNS). Transportation Research 
Part C: Emerging Technologies, 153, 104223. [`link`_]


Contents
====================================

.. toctree::
   :maxdepth: 2

   installation
   quick-start
   get-osm-data
   public-api
   gmns
   mrm
   sample-net
   acknowledgement
   

.. _`Jiawei Lu`: https://www.linkedin.com/in/jiawlu/
.. _`Xuesong (Simon) Zhou`: https://www.linkedin.com/in/xzhou/
.. _`OpenStreetMap`: https://www.openstreetmap.org
.. _`GMNS`: https://github.com/zephyr-data-specs/GMNS
.. _`v0.x user guide`: https://osm2gmns.readthedocs.io/en/v0.x
.. _`link`: https://doi.org/10.1016/j.trc.2023.104223
