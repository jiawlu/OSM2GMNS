===========
Quick Start
===========

In this section, some examples are provided to quickly show how to use osm2gmns 
to generate, manipulate and output networks.

To reduce uncertainties while directly parsing network data from the osm server via APIs, osm2gmns 
uses downloaded osm files to extract useful network information. As a result, the first step is preparing 
osm files.

Thanks to the open-source nature of OpenStreetMap, there are lots of APIs and mirror sites that we can use to
download osm map data. Users are referred to the :ref:`section-get-osm-data` section for details.

In this guide, we use the region around Arizona State University, Tempe Campus as an example to introduce 
some major functions in osm2gmns. The downloaded osm file is named as ``asu.osm``.


Parse OSM Data
=========================

Obtain a transportation network from an osm file and write it to csv files.

.. code-block:: python

    >>> import osm2gmns as og
    >>> net = og.getNetFromFile('asu.osm')
    >>> og.outputNetToCSV(net)

In this example, we use the function ``getNetFromFile`` to parse the osm file and obtain a network object. The
network object is a ``net`` instance, which contains all the information of the network. The function
``outputNetToCSV`` will output the parsed network to csv files. By default, the output folder is set as
the current working directory. Users can specify the output folder by using the argument ``output_folder``.
The default output files are ``node.csv`` and ``link.csv``, which contain node and link information respectively.


Consolidate Intersections
=========================

In OpenStreetMap, one large intersection is often represented by multiple nodes. This structure brings some
difficulties when performing traffic-oriented modelings. osm2gmns enables users to consolidate intersections
that are originally represented by multiple nodes into a single node. Note that osm2gmns only identifies and
consolidates signalized intersections.

.. code-block:: python

    >>> net = og.getNetFromFile('asu.osm')
    >>> og.consolidateComplexIntersections(net, auto_identify=True)
    >>> og.outputNetToCSV(net)

.. figure:: _images/consolidation.png
    :name: consolidate_pic
    :align: center
    :width: 100%

    Complex intersection consolidation

Users can visualize the consolidated network in `QGIS`_ or `NeXTA`_.
For complex interestions that were not successfully identified and consolidated by osm2gmns, users can manually specify
them by revising the column "intersection_id" in node.csv and utilize the commands below to do the re-consolidation.
Nodes assgined with the same "intersection_id" will be consolidated into a new node.

.. code-block:: python

    >>> net = og.loadNetFromCSV(node_file='node.csv', link_file='link.csv')
    >>> og.consolidateComplexIntersections(net, auto_identify=False)
    >>> og.outputNetToCSV(net, output_folder='consolidated')


Network Types and POI
=========================

osm2gmns supports five different network types, including ``auto``, ``bike``, ``walk``, ``railway``, ``aeroway``.
Users can get different types of networks by specifying the argument ``network_types``  (default: ``(auto,)``).

.. code-block:: python

    >>> # obtain the network for bike
    >>> net = og.getNetFromFile('asu.osm', network_types='bike')
    >>> # obtain the network for walk and bike
    >>> net = og.getNetFromFile('asu.osm', network_types=('walk','bike'))
    >>> # obtain the network for auto, railway and aeroway
    >>> net = og.getNetFromFile('asu.osm', network_types=('auto','railway','aeroway'))

Obtain POIs (Point of Interest) from osm map data.

.. code-block:: python

    >>> net = og.getNetFromFile('asu.osm', POI=True)

If ``POI`` (default: ``False``) is set as ``True``, a file named ``poi.csv`` will be generated when outputting
a network using function ``outputNetToCSV``.

.. figure:: _images/poi1.png
    :name: poi1
    :align: center
    :width: 100%

    Network with POIs

Connect POIs with transportation network.

.. code-block:: python

    >>> net = og.getNetFromFile('asu.osm', POI=True)
    >>> og.connectPOIWithNet(net)

By using function ``connectPOIWithNet``, a node located at the centroid of each POI will be generated to
represent the POI. Then connector links will be built to connect the POI node with the nearest node in the
transportation network.

.. figure:: _images/poi2.png
    :name: poi2
    :align: center
    :width: 100%

    Connect POIs with network


Generate Multi-Resolution Networks
==================================

Multi-resolution functionalities are currently not available in v1 of osm2gmns.
Users can the latest version of V0. Check out the v0 `user's guide`_ for details.


.. _`QGIS`: https://qgis.org
.. _`NeXTA`: https://github.com/asu-trans-ai-lab/NeXTA4GMNS
.. _`user's guide`: https://osm2gmns.readthedocs.io/en/v0.x