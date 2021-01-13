OSM2GMNS
========

`OpenStreetMap`_ (OSM) is a free, open-source, editable map website that can provide free
download. osm2gmns, as a data conversion tool, can directly convert the OSM map data
to node and link network files in `GMNS`_ format. Users can convert and model drivable,
walkable, railway, or aeroway networks with a single line of Python code.

Installation
------------

.. code-block:: bash

    pip install osm2gmns

If you meet installation issues, please refer to the `user guide`_ for solutions.


Simple example
--------------

Get network from osm file and conduct intersection consolidation

.. code:: python

    >>> import osm2gmns as og

    >>> net = og.getNetFromOSMFile('map.osm')
    >>> # for large networks, getNetFromPBFFile() is recommended
    >>> og.outputNetToCSV(net)


Visualization
-------------

You can visualize generated networks using `NeXTA`_ or `QGis`_.

.. figure:: https://github.com/jiawei92/OSM2GMNS/blob/master/test/asu.PNG
    :name: case_asu
    :align: center
    :width: 100%

    Arizona State Unversity, Tempe Campus


User guide
-------------
Users can check the `user guide`_ for a detailed introduction of osm2gmns.


.. _`OpenStreetMap`: https://www.openstreetmap.org
.. _`GMNS`: https://github.com/zephyr-data-specs/GMNS
.. _`NeXTA`: https://github.com/xzhou99/NeXTA-GMNS
.. _`QGis`: https://qgis.org
.. _`user guide`: https://osm2gmns.readthedocs.io