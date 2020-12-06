===========
Quick Start
===========

In this section, some examples will be used to demonstrate how to use osm2gmns to generate, manipulate
and output networks.

Download OSM Data
=========================

To reduce the uncertainty while directly downloading data from osm server via APIs, osm2gmns uses offline
osm files to extract useful network information. Thus, the first step is preparing osm files.

Thanks to the open-source nature of openstreetmap, there are lots of APIs and mirrors that we can use to
download osm data. We listed some frequently used approaches here for users to choose.


- Openstreetmap Homepage

Go to openstreetmap `homepage`_, then click the ``Export`` button to enter Export mode. Before downloading,
you may need to span and zoom in/out the map to make your target area is properly shown on the screen.
Or, you can use ``Manually select a different area`` to select the area more precisely. Click the ``Export``
button in blue to export the network you selected.

Note that if the target area is too large, you may get an error message: You requested too many nodes
(limit is 50000). Either request a smaller area, or use planet.osm. In that situation, you can alway click
``Overpass API`` to download the network you need via a mirror.

.. figure:: _images/osmhp.png
    :name: osmhp_pic
    :align: center
    :width: 100%

    Download osm data from openstreetmap homepage


- Geofabrik

Different from downloading network from openstreetmap homepage, `Geofabrik`_ enables you to download network data for
administrative areas. In openstreetmap homepage, we can only download areas defined by rectangles. In Geofabrik
homepage, you can click the corresponding quick link of your interseted region to download the network data you
need. You can always click the name of regions to check if sub region data are available.

Generally, network data of each region are stored in three file format, including ``.pbf``, ``.shp`` and
``.osm``. Users can choose any one to download. osm2gmns supports ``.pbf`` and ``.osm`` files. In osm2gmns,
networks stored in ``.osm`` files are parsed quickly than those stored in ``.pbf`` files. However, compared with
``.pbf`` files, ``.osm`` files take much more hard disk space to store networks and much more space in RAM while parsing.

.. figure:: _images/geofabrik.png
    :name: geofabrik_pic
    :align: center
    :width: 100%

    Download osm data from Geofabrik


- BBBike

If your target area is neither an administrative region nor a rectangle, `BBBike`_ may be a good choice.
`BBBike`_ enables you to select your own region using a polygon. `BBBike`_ supports numerous file formats
to output and store network data. Users can select a propoer one according to their requirements.

.. figure:: _images/bbbike.png
    :name: bbbike_pic
    :align: center
    :width: 100%

    Download osm data from BBBike



Parse OSM Data
=========================

We use the region around Arizona State University, Tempe Campus in this guide to introduce major functions
in osm2gmns.

Get network from osm file.

.. code-block:: python

    >>> import osm2gmns as og

    >>> net = og.getNetFromOSMFile('asu.osm')

A link will be included into the network file from osm database if part of the link lies in the region
that user selected. If argument ``strict_mode`` (default: ``True``) is set as ``True``, link parts that
outside the region will be cut off when parsing osm data. If argument ``strict_mode`` is set as ``False``,
all links in the network file will be kept.

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


One loaded network may contain several sub networks, with any sub network is not accessible from others.
In most cases, these sub networks include a large sub network and some isolated nodes or links. When the
number of nodes of a sub network is less than argument ``min_nodes`` (default: ``1``), this sub network
will be discarded.

In order to simplify the resulting network, argument ``simplify`` is set as ``True`` by default. When
``simplify`` is enabled, two-degree nodes (one incoming link and one outgoing link) will be removed, and
two adjacent links will be combined to generate a new link.


Noticed that most links do not have lanes information in the network file provided by openstreetmap, there
is a default lanes dictionary for each link type in osm2gmns. By setting ``default_lanes`` (default:  ``False``)
as ``True``, a default value will be assigned to a link if it does not come with lanes information. The
default dictionary in osm2gmns:

.. code-block:: python

    default_lanes_dict = {'motorway': 4, 'trunk': 3, 'primary': 3, 'secondary': 2, 'tertiary': 2,
                          'residential': 1, 'service': 1, 'cycleway':1, 'footway':1, 'track':1,
                          'unclassified': 1, 'connector': 2}
    default_speed_dict = {'motorway': 59, 'trunk': 39, 'primary': 39, 'secondary': 39, 'tertiary': 29,
                          'residential': 29, 'service': 29, 'cycleway':9, 'footway':4, 'track':29,
                          'unclassified': 29, 'connector':59}

``default_lanes`` also accepts a dictionary. In that case, osm2gmns will use the dictionary provided by users
to update the default dictionary, and keep defualt lanes of link types not in user's dictionary unchanged.

Similarly for argument ``default_speed``.

.. note::

    - In the current release (0.1.1), osm2gmns can only load networks from ``.osm`` files. ``.pbf``
      format will be supported in the next release (0.2.0).


Output Networks to CSV
=========================

Based on the ``net`` instance from the last step, ``outputNetToCSV`` can be called to output the parsed network
to csv files.

.. code-block:: python

    >>> og.outputNetToCSV(net)

Users can use argument ``output_folder`` to specify the folder to store output files. Node information will be
written to ``node.csv``, while link information will be written to ``link.csv``.

If ``simplify`` is set as ``True``
when parsing the network, ``segment.csv`` will also be created to store lane changes in links. Lane changes occur
when combining two adjacent links with different lanes in the simplification step.


Consolidate Intersections
=========================

In openstreetmap, one large intersection is often represented by multiple nodes. This structure brings some
difficulties when conducting traffic simulations (hard to model traffic signals in these intersections).
osm2gmns enables users to consolidate interstions while parsing networks, e.g. generate a new node to replace
existing nodes for each large intersection.

.. code-block:: python

    >>> net = og.getNetFromOSMFile('asu.osm')
    >>> og.consolidateComplexIntersections(net)

When conducting function ``getNetFromOSMFile``, osm2gmns will automatically identify complex intersections based
on the argument ``int_buffer`` (defalut: ``20.0``). Nodes that belong to one complex intersection will be assigned
with a same ``main_node_id``, but these nodes will not be consolidated into one node until function
``consolidateComplexIntersections`` is called.

.. figure:: _images/consolidate.png
    :name: consolidate_pic
    :align: center
    :width: 100%

    Complex intersection consolidation

Users can also check and revise the complex intersection identification results first, then conduct the consolidating
operation to achieve more reasonable outcomes.

.. code-block:: python

    >>> net = og.getNetFromOSMFile('asu.osm')
    >>> og.outputNetToCSV(net)
    >>> # check the main_node_id column in node.csv
    >>> net = og.getNetFromCSV()
    >>> og.consolidateComplexIntersections(net)
    >>> og.outputNetToCSV(net, output_folder='consolidated')


Network Types and POI
=========================

osm2gmns supports five network types in total, including ``auto``, ``bike``, ``walk``, ``railway``, ``aeroway``.
Extract the auto and railway network from a osm file by setting ``network_type`` (default: ``(auto,)``) as
``(auto,railway)``:

.. code-block:: python

    >>> net = og.getNetFromOSMFile('asu.osm', network_type=('auto','railway','aeroway'))

Get POIs (Point of Interest) from osm files.

.. code-block:: python

    >>> net = og.getNetFromOSMFile('asu.osm', POIs=True)

If ``POIs`` (default: ``False``) is set as ``True``, a file named ``poi.csv`` will be generated when calling
function ``outputNetToCSV``.

.. figure:: _images/poi1.png
    :name: poi1
    :align: center
    :width: 100%

    Network with POIs

Connect POIs with network.

.. code-block:: python

    >>> net = og.getNetFromOSMFile('asu.osm', POIs=True)
    >>> og.connectPOIWithNet(net)

By calling function ``connectPOIWithNet``, a node located at the centroid of each POI will be generated to
represent the POI, then connector links will be used to connect the POI node with the nearest node in the network.

.. figure:: _images/poi2.png
    :name: poi2
    :align: center
    :width: 100%

    Connect POIs with network


.. _`homepage`: https://www.openstreetmap.org
.. _`Geofabrik`: https://download.geofabrik.de/
.. _`BBBike`: https://extract.bbbike.org/