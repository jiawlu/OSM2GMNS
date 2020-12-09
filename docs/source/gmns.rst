===========
GMNS
===========

`GMNS`_ (General Modeling Network Specification), proposed by the Zephyr Foundation, 
which aims to advance the field through flexible and efficient support, education, 
guidance, encouragement, and incubation.

The two necessary files used in GMNS to describe a network: ``node.csv`` and ``link.csv``.

- node.csv

The node file is a list of vertices that locate points on a map. Typically, they will
represent intersections, but may also represent other points, such as a transition between
divided and undivided highway\ :sup:`[1]`. We add several additional attributes to the node file
to make it more suitable for transportation modelling. Detailed node data dictionary is
listed below.

.. table::
    :class: classic

    +-------------+---------------+----------+---------------------------------------------------------------+
    |    Field    |      Type     | Required?|                           Comments                            |
    +=============+===============+==========+===============================================================+
    |    name     |     string    |          |                                                               |
    +-------------+---------------+----------+---------------------------------------------------------------+
    |  node_id    |       int     |   yes    | unique key                                                    |
    +-------------+---------------+----------+---------------------------------------------------------------+
    | osm_node_id | string or int |          | corresponding point id in osm data                            |
    +-------------+---------------+----------+---------------------------------------------------------------+
    | osm_highway |     string    |          | point type in osm data                                        |
    +-------------+---------------+----------+---------------------------------------------------------------+
    |  zone_id    |       int     |          |                                                               |
    +-------------+---------------+----------+---------------------------------------------------------------+
    |  ctrl_type  |       int     |          | 1: Signalized; 0: not                                         |
    +-------------+---------------+----------+---------------------------------------------------------------+
    |  node_type  |     string    |          |                                                               |
    +-------------+---------------+----------+---------------------------------------------------------------+
    |activity_type|     string    |          | defined by adjacent links                                     |
    +-------------+---------------+----------+---------------------------------------------------------------+
    | is_boundary |      bool     |          | 1: boundary; 0: not                                           |
    +-------------+---------------+----------+---------------------------------------------------------------+
    |  x_coord    |     double    |   yes    | WGS 84 is used in osm                                         |
    +-------------+---------------+----------+---------------------------------------------------------------+
    |  y_coord    |     double    |   yes    | WGS 84 is used in osm                                         |
    +-------------+---------------+----------+---------------------------------------------------------------+
    | main_node_id|      int      |          | nodes belonging to one complex intersection have the same id  |
    +-------------+---------------+----------+---------------------------------------------------------------+
    |   poi_id    |      int      |          | id of the corresponding poi                                   |
    +-------------+---------------+----------+---------------------------------------------------------------+

- link.csv

A link is an edge in a network, defined by the nodes it travels from and to. It may have associated geometry
information\ :sup:`[2]`. Similar to node.csv, We also added several new attributes to the link file. Detailed
link data dictionary is listed below.

.. table::
    :class: classic

    +----------------+---------------+----------+---------------------------------------------------------------+
    |      Field     |      Type     | Required?|                           Comments                            |
    +================+===============+==========+===============================================================+
    |      name      |     string    |          |                                                               |
    +----------------+---------------+----------+---------------------------------------------------------------+
    |    link_id     |      int      |   yes    | unique key                                                    |
    +----------------+---------------+----------+---------------------------------------------------------------+
    |   osm_way_id   | string or int |          | corresponding way id in osm data                              |
    +----------------+---------------+----------+---------------------------------------------------------------+
    |  from_node_id  |      int      |   yes    |                                                               |
    +----------------+---------------+----------+---------------------------------------------------------------+
    |   to_node_id   |      int      |   yes    |                                                               |
    +----------------+---------------+----------+---------------------------------------------------------------+
    |    dir_flag    |     enum      |          | 1: forward, -1: backward, 0:bidirectionial                    |
    +----------------+---------------+----------+---------------------------------------------------------------+
    |     length     |     float     |          | unit: meter                                                   |
    +----------------+---------------+----------+---------------------------------------------------------------+
    |      lanes     |      int      |          |                                                               |
    +----------------+---------------+----------+---------------------------------------------------------------+
    |   free_speed   |     float     |          |                                                               |
    +----------------+---------------+----------+---------------------------------------------------------------+
    |    capacity    |     float     |          | unit: veh/hr/lane                                             |
    +----------------+---------------+----------+---------------------------------------------------------------+
    | link_type_name |     string    |          |                                                               |
    +----------------+---------------+----------+---------------------------------------------------------------+
    |    link_type   |       int     |          |                                                               |
    +----------------+---------------+----------+---------------------------------------------------------------+
    |    geometry    |     Geometry  |          | `wkt`_                                                        |
    +----------------+---------------+----------+---------------------------------------------------------------+
    |  allowed_uses  |      enum     |          | auto, bike, walk                                              |
    +----------------+---------------+----------+---------------------------------------------------------------+
    |   from_biway   |      bool     |          | 1: link created from a bidirectional way, 0: not              |
    +----------------+---------------+----------+---------------------------------------------------------------+

Other two optional files including ``movement.csv`` and ``segement.csv`` follow the exact same format as what
being defined in the GMMS standard. Readers can check the GMNS website for details.

In addition to the above files defined in the GMNS standard, osm2gmns can also produce ``poi.csv`` files
where point of interest information is stored. Detailed poi data dictionary is listed below.

.. table::
    :class: classic

    +-----------------+---------------+----------+---------------------------------------------------------------+
    |      Field      |      Type     | Required?|                           Comments                            |
    +=================+===============+==========+===============================================================+
    |       name      |     string    |          |                                                               |
    +-----------------+---------------+----------+---------------------------------------------------------------+
    |      poi_id     |      int      |   yes    | unique key                                                    |
    +-----------------+---------------+----------+---------------------------------------------------------------+
    |    osm_way_id   | string or int |          | corresponding way id in osm data                              |
    +-----------------+---------------+----------+---------------------------------------------------------------+
    | osm_relation_id | string or int |          | corresponding relation id in osm data                         |
    +-----------------+---------------+----------+---------------------------------------------------------------+
    |     building    |     string    |          | building tag in osm data                                      |
    +-----------------+---------------+----------+---------------------------------------------------------------+
    |     amenity     |     string    |          | amenity tag in osm data                                       |
    +-----------------+---------------+----------+---------------------------------------------------------------+
    |     geometry    |    Geometry   |   yes    | `wkt`_                                                        |
    +-----------------+---------------+----------+---------------------------------------------------------------+
    |     centroid    |    Geometry   |          | `wkt`_                                                        |
    +-----------------+---------------+----------+---------------------------------------------------------------+


\ :sup:`[1]` https://github.com/zephyr-data-specs/GMNS/blob/master/Specification/Node.md

\ :sup:`[2]` https://github.com/zephyr-data-specs/GMNS/blob/master/Specification/Link.md

.. _`GMNS`: https://github.com/zephyr-data-specs/GMNS
.. _`wkt`: https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry