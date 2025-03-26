===========
Quick Start
===========

In this section, some examples are provided to quickly show how to use osm2gmns 
to generate, manipulate and output networks.


Get OSM Data
=========================

To reduce uncertainties while directly parsing network data from the osm server via APIs, osm2gmns uses downloaded
osm files to extract useful network information. As a result, the first step is preparing osm files.

Thanks to the open-source nature of OpenStreetMap, there are lots of APIs and mirror sites that we can use to
download osm map data. We introduce different download options in the get-osm-data section.


Parse OSM Data
=========================

We use the region around Arizona State University, Tempe Campus in this guide to introduce some major functions
in osm2gmns.

Obtain a transportation network from an osm file.

.. code-block:: python

    >>> import osm2gmns as og

    >>> net = og.getNetFromFile('asu.osm')


A link will be included in the network file from osm database if part of the link lies in the region
that users selected. If argument ``strict_mode`` (default: ``True``) is set as ``True``, link segments that
outside the region will be cut off when parsing osm data. If argument ``strict_mode`` is set as ``False``,
all links in the network file will be imported.

.. figure:: _images/bstrict1.png
    :name: bstrict1
    :align: center
    :width: 100%

    Parsed network with ``strict_mode=False``

.. figure:: _images/bstrict2.png
    :name: bstrict2
    :align: center
    :width: 100%

    Parsed network with ``strict_mode=True``


One loaded network may contain several sub networks, with some sub networks not accessible from others.
In most cases, these sub networks include a large sub network and some isolated nodes or links. When the
number of nodes of a sub network is less than argument ``min_nodes`` (default: ``1``), this sub network
will be discarded.

Users can use argument ``combine`` (default: ``False``) to control short link combinations. If ``combine``
is enabled, two-degree nodes (nodes with one incoming link and one outgoing link) will be removed, and two adjacent
links will be combined to generate a new link. Note that link combination will be performed only when two candidate
links have the exact same link attributes, e.g., name, speed, lanes.

Notice that most links do not have "lanes" information in the map data provided by OpenStreetMap. Thus,
we use a default lanes dictionary for each link type in osm2gmns. By setting ``default_lanes`` (default:  ``False``)
as ``True``, the default value will be assigned to a link if it does not come with "lanes" information. The
default dictionary in osm2gmns:

.. code-block:: python

    default_lanes_dict = {'motorway': 4, 'trunk': 3, 'primary': 3, 'secondary': 2, 'tertiary': 2,
                          'residential': 1, 'service': 1, 'cycleway':1, 'footway':1, 'track':1,
                          'unclassified': 1, 'connector': 2}
    default_speed_dict = {'motorway': 120, 'trunk': 100, 'primary': 80, 'secondary': 60, 'tertiary': 40,
                          'residential': 30, 'service': 30, 'cycleway':5, 'footway':5, 'track':30,
                          'unclassified': 30, 'connector':120}
    default_capacity_dict = {'motorway': 2300, 'trunk': 2200, 'primary': 1800, 'secondary': 1600, 'tertiary': 1200,
                          'residential': 1000, 'service': 800, 'cycleway':800, 'footway':800, 'track':800,
                          'unclassified': 800, 'connector':9999}

``default_lanes`` also accepts a dictionary. In that case, osm2gmns will use the dictionary provided by users
to update the default dictionary.

A similar fashion applies for argument ``default_speed`` and ``default_capacity``.


Output Networks to CSV
=========================

Based on the ``net`` instance obtained from the last step, ``outputNetToCSV`` can be used to output the parsed network
to CSV files.

.. code-block:: python

    >>> og.outputNetToCSV(net)

Users can use argument ``output_folder`` to specify the folder to store output files. Node information will be
written to ``node.csv``, while link information will be written to ``link.csv``.


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

osm2gmns can generate the corresponding mesoscopic and microscopic network for any macroscopic networks in GMNS format.

Generate multi-resolution networks from an osm file.

.. code-block:: python

    >>> net = og.getNetFromFile('asu.osm', default_lanes=True)
    >>> og.consolidateComplexIntersections(net, auto_identify=True)
    >>> og.buildMultiResolutionNets(net)
    >>> og.outputNetToCSV(net)

Generate multi-resolution networks from a macroscopic network provided by user (movement information is automatically
generated by osm2gmns).

.. code-block:: python

    >>> net = og.loadNetFromCSV(node_file='node.csv', link_file='link.csv')
    >>> og.buildMultiResolutionNets(net)
    >>> og.outputNetToCSV(net)

Generate multi-resolution networks from a macroscopic network provided by user (movement information is from the user).

.. code-block:: python

    >>> net = og.loadNetFromCSV(node_file='node.csv', link_file='link.csv', movement_file='movement.csv')
    >>> og.buildMultiResolutionNets(net)
    >>> og.outputNetToCSV(net)


.. _`QGIS`: https://qgis.org
.. _`NeXTA`: https://github.com/asu-trans-ai-lab/NeXTA4GMNS