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


Installation
====================================

.. code-block:: bash

    pip install osm2gmns

If you meet installation issues, please refer to the `user's guide`_ for solutions.


Simple examples
====================================

You can find the osm map file used in the examples below at 'sample networks/Arizona State University, Tempe Campus'

Quickly get the network with point of interet (POI) information from an osm file

.. code:: python

    >>> import osm2gmns as og
    >>> net = og.getNetFromFile('asu.osm', POI=True)
    >>> og.outputNetToCSV(net)

Generate multi-resolution networks from an osm file

.. code:: python

    >>> import osm2gmns as og
    >>> net = og.getNetFromFile('asu.osm')
	>>> og.consolidateComplexIntersections(net, auto_identify=True)
	>>> og.buildMultiResolutionNets(net)
    >>> og.outputNetToCSV(net)


Visualization
====================================

You can visualize generated networks using `NeXTA`_ or `QGis`_.

.. figure:: https://github.com/jiawlu/OSM2GMNS/blob/master/sample%20networks/Arizona%20State%20University%2C%20Tempe%20Campus/net_asu.png
    :name: case_asu
    :align: center
    :width: 100%

    Arizona State Unversity, Tempe Campus


User's guide
====================================
You can check the `user's guide`_ for a detailed introduction of osm2gmns.


.. _`OpenStreetMap`: https://www.openstreetmap.org
.. _`GMNS`: https://github.com/zephyr-data-specs/GMNS
.. _`NeXTA`: https://github.com/xzhou99/NeXTA-GMNS
.. _`QGis`: https://qgis.org
.. _`user's guide`: https://osm2gmns.readthedocs.io