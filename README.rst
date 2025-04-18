osm2gmns
====================================
| **Authors**: `Jiawei Lu`_, `Xuesong (Simon) Zhou`_
| **Email**: lujiaweiwk@gmail.com, xzhou74@asu.edu


osm2gmns is a high-performance Python package designed to convert `OpenStreetMap`_ (OSM) 
data into standardized transportation networks. Leveraging a C++ core wrapped in an 
intuitive Python interface, osm2gmns offers both computational speed and ease of use. 
It empowers researchers and practitioners to generate detailed, multi-modal networks 
(driving, cycling, walking, railway, aeroway) for any region worldwide with minimal 
coding effort.

The package outputs networks primarily in the `GMNS`_ (General Modeling Network Specification) 
format, promoting interoperability and simplifying data exchange within the transportation 
modeling community.

.. code-block:: python

    >>> import osm2gmns as og
    >>> net = og.getNetFromFile('map.osm')
    >>> og.outputNetToCSV(net)


Citation
====================================

If osm2gmns contributes to your research, please cite the following publication:

Lu, J., & Zhou, X.S. (2023). Virtual track networks: A hierarchical modeling framework and 
open-source tools for simplified and efficient connected and automated mobility (CAM) system 
design based on general modeling network specification (GMNS). Transportation Research 
Part C: Emerging Technologies, 153, 104223. [`link`_]


User's guide
====================================

Users are referred to `user's guide`_ for a detailed introduction of osm2gmns.



.. _`Jiawei Lu`: https://www.linkedin.com/in/jiawlu/
.. _`Xuesong (Simon) Zhou`: https://www.linkedin.com/in/xzhou/
.. _`OpenStreetMap`: https://www.openstreetmap.org
.. _`GMNS`: https://github.com/zephyr-data-specs/GMNS
.. _`link`: https://doi.org/10.1016/j.trc.2023.104223
.. _`user's guide`: https://osm2gmns.readthedocs.io