osm2gmns
====================================
| **Authors**: Jiawei Lu, Xuesong (Simon) Zhou
| **Email**: jiaweil9@asu.edu, xzhou74@asu.edu


osm2gmns is an open-source Python package that enables users to conveniently obtain and
manipulate any networks from OpenStreetMap (OSM). With a single line of Python code,
users can obtain and model drivable, bikeable, walkable, railway, and aeroway networks
for any region in the world and output networks to CSV files in GMNS format for seamless
data sharing and research collaboration. osm2gmns mainly focuses on providing researchers and
practitioners with flexible, standard and ready-to-use multi-modal transportation networks,
as well as a bunch of customized and practical functions to facilitate various research
and applications on traffic modeling.


Publication
====================================

Lu, J., & Zhou, X.S. (2023). Virtual track networks: A hierarchical modeling framework and
open-source tools for simplified and efficient connected and automated mobility (CAM) system
design based on general modeling network specification (GMNS). Transportation Research
Part C: Emerging Technologies, 153, 104223. `paper link`_


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

Quickly get the network with point of interest (POI) information from an osm file

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


Get relation id of a place of interest and download the corresponding osm file
=====================================================================================================================
You can use the following code to get the relation id of a place of interest and download the corresponding osm file.

.. code:: python

    >>> import osm2gmns as og
    # get relation id of a place of interest
    # For the place of interest, e.g. Arizona State University
    # e.g. "Tempe, Arizona, United States"
    # e.g. "Arizona, US"
    # e.g. "Beijing Jiaotong University, Beijing, China"
    >>> rel_id = og.getOSMRelationID('Arizona State University')
    >>> rel_id
        Info: Found relation id 3444656 from web
        Info: location of the place of interest:
        {
            "place_id": 318528634,
            "licence": "Data \u00a9 OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "osm_type": "relation",
            "osm_id": 3444656,
            "lat": "33.4213174",
            "lon": "-111.93316305413154",
            "class": "amenity",
            "type": "university",
            "place_rank": 30,
            "importance": 0.5547365758311374,
            "addresstype": "amenity",
            "name": "Arizona State University",
            "display_name": "Arizona State University, 1151, South Forest Avenue, Tempe Junction, Tempe, Maricopa County, Arizona, 85281, United States",
            "boundingbox": [
                "33.4102062",
                "33.4329786",
                "-111.9411651",
                "-111.9092447"
            ]
        }
    3444656

    # download the corresponding osm file
    >>> og.downloadOSMData(rel_id, 'asu.osm')


User's guide
====================================
You can check the `user's guide`_ for a detailed introduction of osm2gmns.


.. _`OpenStreetMap`: https://www.openstreetmap.org
.. _`GMNS`: https://github.com/zephyr-data-specs/GMNS
.. _`paper link`: https://doi.org/10.1016/j.trc.2023.104223
.. _`user's guide`: https://osm2gmns.readthedocs.io