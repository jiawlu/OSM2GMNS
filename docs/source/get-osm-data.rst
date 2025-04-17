.. _section-get-osm-data:

============
Get OSM Data
============

Four options

1) OpenStreetMap Homepage

On OpenStreetMap `homepage`_, click the ``Export`` button to enter Export mode. Before downloading,
you may need to span and zoom in/out the map to make sure that your target area is properly shown on the screen.
Or, you can use ``Manually select a different area`` to select your area more precisely. Click the ``Export``
button in blue to export the network you want.

Note that if the target area is too large, you may get an error message: "You requested too many nodes
(limit is 50000). Either request a smaller area, or use planet.osm". In this case, you can always click
``Overpass API`` to download the network you need via a mirror site.

.. figure:: _images/osmhp.png
    :name: osmhp_pic
    :align: center
    :width: 100%

    Download osm data from OpenStreetMap homepage


2) Geofabrik

Different from the way of downloading map data from OpenStreetMap homepage, `Geofabrik`_ enables you to
download network data for administrative areas. On OpenStreetMap homepage, we can only download areas
defined by rectangles. In Geofabrik, you can click the corresponding quick link of your interested
region to download the map data you need. You can always click the name of regions to check if sub region
data are available.

Generally, there are three types of file format for users to choose when downloading map data.
osm2gmns supports ``.pbf`` and ``.osm`` files. In osm2gmns, networks stored in ``.osm`` files
are parsed more quickly than those stored in ``.pbf`` files. However, compared with ``.pbf`` files,
``.osm`` files take much more hard disk space to store networks and much more space in RAM while parsing.

.. figure:: _images/geofabrik.png
    :name: geofabrik_pic
    :align: center
    :width: 100%

    Download osm data from Geofabrik


3) BBBike

If your target area is neither an administrative region nor a rectangle, `BBBike`_ may be a good choice.
`BBBike`_ enables you to select your region using a polygon. `BBBike`_ supports numerous file formats
to output and store network data. Users can select a proper one according to their requirements.

.. figure:: _images/bbbike.png
    :name: bbbike_pic
    :align: center
    :width: 100%

    Download osm data from BBBike

.. note::

    - The file formats of map data supported in osm2gmns include ``.osm``, ``.xml``, and ``.pbf``.


4) Overpass API

osm2gmns also enables users to download OSM data within the region of interest using a built-in function.
A region can be a state, city, or even university. On OpenStreetMap `homepage`_, search the region name to get
its unique relation id. The following example shows how to download Tempe city OSM data using function
``downloadOSMData``.

.. figure:: _images/osm_id.png
    :name: osm_id
    :align: center
    :width: 100%

    Get region id from OpenStreetMap homepage

.. code-block:: python

    >>> import osm2gmns as og

    >>> og.downloadOSMData(110833, 'tempe.osm')


osm2gmns built-in function: getOSMRelationID
Get the relation id of a place of interest, eg. "Arizona State University", "Arizona, United States", "Tempe, AZ"...

.. code-block:: python

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


.. _`homepage`: https://www.openstreetmap.org
.. _`Geofabrik`: https://download.geofabrik.de/
.. _`BBBike`: https://extract.bbbike.org/