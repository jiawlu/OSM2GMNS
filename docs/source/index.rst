osm2gmns
====================================
| **Authors**: `Jiawei Lu`_, `Xuesong (Simon) Zhou`_
| **Email**: lujiaweiwk@gmail.com, xzhou74@asu.edu


osm2gmns is a high-performance Python package designed to convert `OpenStreetMap`_ (OSM) 
data into standardized transportation networks. Leveraging a C++ core wrapped in an 
intuitive Python interface, osm2gmns offers both computational speed and ease of use. 
**It empowers researchers and practitioners to generate detailed, multi-modal networks (driving, cycling, walking, railway, aeroway) for any region worldwide with minimal coding effort**.

The package outputs networks primarily in the `GMNS`_ (General Modeling Network Specification) 
format, promoting interoperability and simplifying data exchange within the transportation 
modeling community.

.. code-block:: python

    >>> import osm2gmns as og
    >>> net = og.getNetFromFile('map.osm')
    >>> og.outputNetToCSV(net)


.. note::
   **Welcome to the osm2gmns v1.x Documentation!**

   This version introduces significant architectural changes, performance improvements, and 
   new features compared to v0.x, and is **not fully backward compatible**.

   - We encourage users to adopt v1.x for the latest capabilities and ongoing development.
   - v0.x will only receive critical bug fixes moving forward.
   - Functionality like Multi-Resolution Modeling (MRM), currently available only in v0.x, is planned for future v1.x releases. If you require MRM now, please consult the `v0.x user's guide`_.


Key Features
====================================

1. Comprehensive Network Modeling

- Worldwide Network: Generate networks from OpenStreetMap for any region globally
- Multi-Modal Support: Generate networks for vehicles, bicycles, pedestrians, railways, and aeroways
- GMNS Compatibility: Standardized output format for interoperability with other tools

2. Advanced Functionality

- Intersection Consolidation: Simplifies complex junctions for various modeling needs
- Movement Generation: Creates turning movements at intersections
- Directed Network Generation: Automatic creation of directional links for bidirectional roadways
- Traffic Zone Creation: Supports origin-destination modeling
- Ready-to-Use Networks: Automatic inference of critical attributes (lanes, speed, capacity)
- Network Visualization: Built-in tools for visual inspection and verification

3. Performance and Usability

- High-Performance Core: Written in C++ for maximum computational efficiency
- Intuitive Python Interface: Simple API makes complex network extraction straightforward


Citation
====================================

If osm2gmns contributes to your research, please cite the following publication:

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
.. _`v0.x user's guide`: https://osm2gmns.readthedocs.io/en/v0.x
.. _`link`: https://doi.org/10.1016/j.trc.2023.104223
