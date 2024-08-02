===========
GMNS
===========

General Modeling Network Specification (`GMNS`_), proposed by the `Zephyr Foundation`_, 
defines a common human and machine readable format for sharing routable road network files. 
It is designed to be used in multi-modal static and dynamic transportation planning and 
operations models. It will facilitate the sharing of tools and data sources by modelers. 
For additional information on GMNS goals, history and requirements, please see the `wiki`_.


GMNS (version 0.92) includes the following features for use in static models:

- Configuration information and use definitions.
- Node and link files, to establish a routable network.

For dynamic models, GMNS (version 0.92) includes the following optional additional features:

- A segment file, with information that overrides the characteristics of a portion of a link.
- A lane file that allocates portions of the right-of-way. Lanes include travel lanes used by motor vehicles. They may also optionally include bike lanes, parking lanes, and shoulders.
- A segment_lane file that specifies additional lanes, dropped lanes, or changes to lane properties on a segment of a link.
- A movement file that specifies how inbound and outbound lanes connect at an intersection.
- Link, segment, lane and movement time-of-day (TOD) files, that allocate usage of network elements by time-of-day and day-of-week.
- Signal phase and timing files, for basic implementation of traffic signals.

osm2gmns uses GMNS as the standard when processing and manipulating networks, and thus any
network in GMNS format is fully compatible with osm2gmns.


.. _`GMNS`: https://github.com/zephyr-data-specs/GMNS
.. _`Zephyr Foundation`: https://zephyrtransport.org
.. _`wiki`: https://github.com/zephyr-data-specs/GMNS/wiki
