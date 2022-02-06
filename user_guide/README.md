# osm2gmns

**Author:** Jiawei Lu, Xuesong (Simon) Zhou

**Email:** jiaweil9@asu.edu, xzhou74@asu.edu

[OpenStreetMap](https://www.openstreetmap.org/) (OSM) is a free, open-source, editable map website that can provide free downloads. [osm2gmns](https://github.com/jiawlu/OSM2GMNS), as a data conversion tool, can directly convert the OSM map data to node and link network files encoded in the [GMNS](https://github.com/zephyr-data-specs/GMNS) format. Users can convert and model drivable, walkable, railway, or aeroway networks with a single line of Python code. Besides, this package can novelty generate multi-resolution networks for transportation analysis with different intentions.

## Installation

You can install the latest release of osm2gmns at [PyPI](https://pypi.org/project/osm2gmns/) via pip:

```python
$ pip install osm2gmns
```

If you need a specific version of osm2gmns, say, 0.6.3, you should enter the following command:
```python
$ pip install osm2gmns==0.6.3
```

### Dependency
After running the command above, the osm2gmns package along with four necessary dependency packages (Shapely, pandas, osmium and protobuf) will be installed to your computer (if they have not been installed yet).

If you install osm2gmns in a conda environment, you may get an error message: 
```python
OSError: [WinError 126] The specified module could not be found
```
To resolve this issue, you need to uninstall the Shapely package first, and reinstall it manually using the command below.
```python
$ conda install shapely
```

## Contents

For program source code and sample network files, readers can visit the project [homepage](https://github.com/asu-trans-ai-lab) at ASU Trans+AI Lab Github. Interested readers can also check the [link](https://asu-trans-ai-lab.github.io/website_openlayer_4GMNS/) for our online transportation modelling visualization platform, in which network data is provided by osm2gmns.

### Download OSM Data

To reduce uncertainties while directly parsing network data from the osm server via APIs, the osm2gmns package uses downloaded OSM files to extract useful network information. As a result, the first step is preparing OSM files.

Thanks to the open-source nature of OpenStreetMap, there are lots of APIs and mirror sites that we can use to download osm map data. We list several popular sites here for users to choose.

1. OpenStreetMap Homepage

On OpenStreetMap [homepage](https://www.openstreetmap.org/), click the **Export** button to enter Export mode. Before downloading, you may need to span and zoom in/out the map to make sure that your target area is properly shown on the screen. Or, you can use **Manually select a different area** to select your area more precisely. Click the **Export** button in blue to export the network you want.


Note that if the target area is too large, you may get an error message: “You requested too many nodes (limit is 50000). Either request a smaller area, or use planet.osm”. In this case, you can always click **Overpass API** to download the network you need via a mirror site.

![](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/osmhp.png)

**Fig. 1 Download osm data from OpenStreetMap homepage**

2. Geofabrik

Different from the way of downloading map data from OpenStreetMap homepage, [Geofabrik](https://download.geofabrik.de/) enables you to download network data for administrative areas. On OpenStreetMap homepage, we can only download areas defined by rectangles. In Geofabrik, you can click the corresponding quick link of your interested region to download the map data you need. You can always click the name of regions to check if sub region data are available.

Generally, there are three types of file format for users to choose when downloading map data. The osm2gmns package supports **_.pbf_**, **_.xml_** and **_.osm_** files. In osm2gmns, networks stored in **_.osm_** files are parsed more quickly than those stored in **_.pbf_** files. However, compared with **_.pbf_** files, **_.osm_** files take much more hard disk space to store networks and much more space in RAM while parsing.

![](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/geofabrik.png)

**Fig. 2 Download osm data from Geofabrik**

3. BBBike

If your target area is neither an administrative region nor a rectangle, [BBBike](https://extract.bbbike.org/) may be a good choice. [BBBike](https://extract.bbbike.org/) enables you to select your region using a polygon. [BBBike](https://extract.bbbike.org/) supports numerous file formats to output and store network data. Users can select a proper one according to their requirements.

![](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/bbbike.png)

**Fig. 3 Download osm data from BBBike**


### General Modeling Network Specification (GMNS)

The osm2gmns package can transfer OSM data into a standard General Modeling Network Specification (GMNS) data structure and store the data into more redable and editable CSV files. General Travel Network Format Specification is a product of [Zephyr Foundation](https://github.com/zephyr-data-specs), which aims to advance the field through flexible and efficient support, education, guidance, encouragement, and incubation. For a given network, there are two necessary CSV files——node.csv and link.csv for storing the basic topological and geometric properties of the network. The website of GMNS is https://github.com/zephyr-data-specs/GMNS. You could find descriptions of fields in: https://github.com/zephyr-data-specs/GMNS/tree/master/Specification_md or https://github.com/zephyr-data-specs/GMNS/tree/master/Specification.

### Multi-resolution Network (MRM)

Transportation networks can have different spatial granularities, each of them are intended to carry out various analysis, optimization, simulation, and management. In this section, we introduce the concept of multi-resolution network (MRM), which is one of the novelties of this package. Three types of networks, namely microscopic network, mesoscopic network, and macroscopic network, are refered to as the MRM.

To demonstrate the MRM process, the Maryland case study used open-source tools to build a multiresolution I–95 network. The research team first downloaded original map data for the subarea network from OSM, then converted it to macroscopic GMNS network files. The team generated corresponding mesoscopic and microscopic networks by using the open-source tools. Notably, OSM often represents one large intersection with multiple nodes to allow flexibility of user input; however, this structure makes the simulation of traffic signal timing very difficult. Accordingly, the team developed a function to consolidate intersection nodes, generating a new node to replace existing nodes for each intersection within a certain buffer.

The open-source tools support five different transportation modes to facilitate multimodal modeling, including automobile, bicycle, walking, rail, and air. The tools can also import POI nodes and create connectors. This case study adopted and extended the GMNS-based representation for ABM and macro-, meso-, and microlayers of representation to achieve a hybrid-resolution network construction. The study adopted the GMNS standard for multiresolution transportation network representation, even though the developers mainly designed GMNS for macroscopic networks. As a result, this MRM-oriented study extends the GMNS-based representation for both mesoscopic and microscopic networks. In the long run, the researchers intend the proposed open-data and open-source framework to create a free open-package and open-data ecosystem, which could reduce the cost and complexity of managing computers and simulation models. The base representation of GMNS would allow different communities to build versions of a high-fidelity virtual model from different open and user-contributed data sources.

#### Mesoscopic Network Representation

Compared to the original macroscopic network, the mesoscopic network has more detailed information in the intersections. In the mesoscopic network, the research team expanded each intersection represented by a node in the macroscopic network. The team built a connector link for each intersection movement to facilitate intersection modeling, especially for signalized intersections.

Macroscopic and mesoscopic networks have different link-level coding schemes. Macroscopic networks often represent a road segment between two adjacent intersections as a link; however, lane changes sometimes occur within a link, especially when close to intersections. Changes in the number of lanes result in capacity changes, but the link attributes cannot properly reflect these changes. This situation may bring inconvenience or even potential errors when performing network modeling. In the GMNS standard, the comma-separated values (CSV) file, segment.csv, stores lane changes. The research team split and converted each link with lane changes from a macroscopic network to multiple mesoscopic links so that each mesoscopic link has a homogeneous capacity.

#### Microscopic Network Representation

In the Maryland case study, microscopic networks used a lane-by-lane, cell-based representation. Instead of a conceptual line segment, lanes represented each link. The research team further discretized lanes into small cells to accurately describe vehicle motion status when moving on the road. The team also created changing cells to enable vehicles to switch trajectories between lanes. Users can customize the length of cells to accommodate different modeling needs.

![](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/macronet.png)

**Fig. 4 Macroscopic network representation**

![](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/mesonet.png)

**Fig. 5 Mesoscopic network representation**

![](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/micronet.png)

**Fig. 6 Microscopic network representation**

### Descriptions of columns in the files of macroscopic networks

**Table 1. Descriptions of columns in the file storing the information of _NODEs_ in macroscopic networks**

| Column | Type | Description | Can it be empty |
| --- | --- | --- | --- | 
| name | string | Name of the node. | Yes |
| node_id | int | ID of the node, starts from 0. | No |
| osm_node_id | int | ID of the node encoded in OSM format. | No |
| osm_highway | string | Additional information associated with highway of the node. | Yes |
| zone_id | int | ID of the zone to which the node belongs. | Yes |
| ctrl_type | string | Type of control of the node. | Yes |
| node_type | string | Type of the node. | Yes |
| activity_type | string | Type of activities of the node | It depends |
| is_boundary | int | Whether the nodes is the boundary of the network. It can be 0 (No), 1(Yes), -1(Yes), or 2(Yes).  | No |
| x_coord | float | The longitude / x-coordinate of the node.  | No |
| y_coord | float | The latitude / y-coordinate of the node.  | No |
| main_node_id | int | ID of the corresponding node in the macroscopic network. | Yes |
| poi_id | int | ID of the corresponding POI. | Yes |
| notes | int | Additional descriptions. | Yes |

![is_boundary](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/is_boundary.png)

**Fig. 7 The effects of distinct values of _is_boundary_**

**Table 2. Descriptions of columns in the file storing the information of _LINKs_ in macroscopic networks**

| Column | Type | Description | Can it be empty |
| --- | --- | --- | --- | 
| name | string | Name of the link. | Yes |
| link_id | int | ID of the link, starts from 0. | No |
| osm_way_id | int | ID of the way / link encoded in OSM format. | No |
| from_node_id | int | ID of the head node in the link. | No |
| to_node_id | int | ID of the tail node in the link. | No |
| dir_flag | int | 1: forward, -1: backward, 0:bidirectionial. | No |
| length | float | The length of the link (meter). | No |
| lanes | int | Number of lanes in the link. | No |
| free_speed | int | Free-flow speed of the link (km/hr). | No |
| capacity | int | Capacity of the link (PCE/hr).  | No |
| link_type_name | string | Name of type of the link. | No |
| link_type | int | A number representing the type of the link. | No |
| geometry | string | Geometry information of the link encoded in [WKT](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry) format. | No |
| allowed_uses | string | A string representing the supported mode in the link. | No |
| from_biway | int | 1: link created from a bidirectional way, 0: not | No |
| is_link | int | Can be 0 or 1. =0 ..., =1... | No |
| VDF_fftt1 | float | Free-flow travel time (min) of the link in the volume-delay function. | Yes |
| VDF_cap1 | float | Capacity (PCE/hr) of the link in the volume-delay function. | Yes |


**Table 3. Descriptions of columns in the file storing the information of _MOVEMENT_ in macroscopic networks**

| Column | Type | Description | Can it be empty |
| --- | --- | --- | --- | 
| mvmt_id | int | ID of the movement, starts from 0. | No |
| node_id | int | ID of the node associated with the movement. | No |
| osm_node_id | int | ID of the node encoded in OSM format. | No |
| name | string | Name of the movement. | Yes |
| ib_link_id | int | ID of the inbound link of the movement. | No |
| start_ib_lane | int | Sequence no. of the first lane in the movement of the inbound link. | No |
| end_ib_lane | int | Sequence no. of the last lane in the movement of the inbound link. | No |
| ob_link_id | int | ID of the outbound link of the movement. | No |
| start_ob_lane | int | Sequence no. of the first lane in the movement of the outbound link. | No |
| end_ob_lane | int | Sequence no. of the last lane in the movement of the outbound link. | No |
| lanes | int | Number of the available lanes for the movement. | No |
| ib_osm_node_id | int | ID of the inbound node encoded in OSM format. | No |
| ob_osm_node_id | int | ID of the outbound node encoded in OSM format. | No |
| type | string | Type of the movement, including "left", "right", "thru", "uturn". | No |
| penalty | float  | Penalty of the movement.| Yes |
| capacity | int  | Capacity of the movement.| Yes |
| ctrl_type | string | Type of control for the movement. | Yes |
| mvmt_txt_id | string | A string representing the direction and type of the movement. | No |
| volume | float | Flow volume which traverse the movement within a specific period of time. | Yes | 
| free_speed | float | Free-flow speed of the movement (km/hr). | Yes | 
| allowed_uses | string | Available transport mode of the movement. | Yes | 


**Table 4. Descriptions of columns in the file storing the information of _POI_ in macroscopic networks**

| Column | Type | Description | Can it be empty |
| --- | --- | --- | --- | 
| name | string | Name of the POI. | Yes |
| poi_id | int | ID of the POI, starts from 0. | No |
| osm_way_id | int | ID of the way encoded in OSM format corresponding to this POI. | No |
| osm_relation_id | int | ID of the relation in OSM format corresponding to this POI. | Yes |
| building | string | A string indicating the type of the building of this POI. | Yes |
| amenity | string | A string indicating the type of the amenity of this POI. | Yes |
| way | string  | Way of the POI. | Yes |
| geometry | string | Geometry information of the POI encoded in [WKT](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry) format. | No |
| centroid | string | Geometry information of the centroid within the POI encoded in [WKT](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry) format. | No |
| area | float | The area of the POI (square meter). | No |
| area_ft2 | float | The area of the POI (square foot). | No |

### Descriptions of columns in the files of mesoscopic networks

The osm2gmns package novelty transfer the macroscopic network into a mesoscopic network and a microscopic network, enabling practitioners and researchers to carry out various transportation planning, designing, optimization, simulation, and computation under different spatial granularities.


**Table 5. Descriptions of columns in the file storing the information of _NODEs_ in mesoscopic networks**

| Column | Type | Description | Can it be empty |
| --- | --- | --- | --- | 
| node_id | int | ID of the node. | No |
| zone_id | int | ID of the zone to which the node belongs. | Yes |
| x_coord | float | The longitude / x-coordinate of the node. | No |
| y_coord | float | The latitude / y-coordinate of the node. | No |
| macro_node_id | int | ID of node from the macroscopic network corresponding to this node. | No |
| macro_link_id | int | ID of link from the macroscopic network corresponding to this node.  | Yes |
| activity_type | string | Type of activity for the node.  | No |
| is_boundary | int | Whether the nodes is the boundary of the network. It can be 0 (No), 1(Yes), -1(Yes), or 2(Yes). | No |


**Table 6. Descriptions of columns in the file storing the information of _LINKs_ in mesoscopic networks**

| Column | Type | Description | Can it be empty |
| --- | --- | --- | --- | 
| link_id | int | ID of the link, starts from 0. | No |
| from_node_id | int | ID of the head node in the link. | No |
| to_node_id | int | ID of the tail node in the link. | No |
| facility_type | string | Type of the facility associated with the link.  | Yes |
| dir_flag | int | 1: forward, -1: backward, 0:bidirectionial. | No |
| length | float | The length of the link (meter). | No |
| lanes | int | Number of lanes in the link. | No |
| capacity | int | Capacity of the link (PCE/hr).  | No |
| free_speed | int | Free-flow speed of the link (km/hr). | No |
| link_type_name | string | Name of type of the link. | No |
| link_type | int | A number representing the type of the link. | No |
| cost | float | Cost consumed for traversing the link. (dollar) | No |
| geometry | string | Geometry information of the link encoded in [WKT](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry) format. | No |
| macro_node_id | int | ID of node from the macroscopic network corresponding to this link. | No |
| macro_link_id | int | ID of link from the macroscopic network corresponding to this link.  | Yes |
| mvmt_txt_id | int | A string representing the direction and type of the movement. | Yes |

### Descriptions of columns in the files of microscopic networks

**Table 7. Descriptions of columns in the file storing the information of _NODEs_ in microscopic networks**

| Column | Type | Description | Can it be empty |
| --- | --- | --- | --- | 
| node_id | int | ID of the node, starts from 0. | No |
| zone_id | int | ID of the zone to which the node belongs. | Yes |
| x_coord | float | The longitude / x-coordinate of the node. | No |
| y_coord | float | The latitude / y-coordinate of the node. | No |
| meso_link_id | int | ID of the link from the mesoscopic network corresponding to this node.| No |
| lane_no | int | Sequence no. of the lane which the node belongs to. | No |
| is_boundary | int | Whether the nodes is the boundary of the network. It can be 0 (No), 1(Yes), -1(Yes), or 2(Yes).  | No |

**Table 8. Descriptions of columns in the file storing the information of _LINKs_ in microscopic networks**

| Column | Type | Description | Can it be empty |
| --- | --- | --- | --- | 
| link_id | int | ID of the link, starts from 0. | No |
| from_node_id | int | ID of the head node in the link. | No |
| to_node_id | int | ID of the tail node in the link. | No |
| facility_type | string | Type of the facility associated with the link.| Yes |
| dir_flag | int | 1: forward, -1: backward, 0:bidirectionial. | No |
| length | float | The length of the link (meter). | No |
| lanes | int | Number of lanes in the link. | No |
| capacity | int | Capacity of the link (PCE/hr).  | No |
| free_speed | int | Free-flow speed of the link (km/hr). | No |
| link_type_name | string | Name of type of the link. | No |
| link_type | int | A number representing the type of the link. | No |
| cost | float | Cost consumed for traversing the link. (dollar) | No |
| geometry | string | Geometry information of the link encoded in [WKT](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry) format. | No |
| macro_node_id | int | ID of node from the macroscopic network corresponding to this link. | Yes |
| macro_link_id | int | ID of link from the macroscopic network corresponding to this link.  | No |
| macro_meso_id | int | ID of link from the mesoscopic network corresponding to this link.  | No |
| cell_type | int | Type of the cell. | No |
| additional_cost | int | Additional cost of the link.  | No |
| mvmt_txt_id | int | A string representing the direction and type of the movement. | Yes |

### Complex Intersection Consolidation

In urban road transportation network, intersections are everywhere which are the junction points at which several links are connected. In OpenStreetMap(OSM), one intersection is often represented by multiple nodes. Unfortunately, the strucutre of intersections provided by OSM is usually not suited for microscopic signal timing and traffic simution. Besides, the topological and geometrical information of intersections are not needed all the time because whether to take intersections into consideration depends on the intention and focus of the transportation planning, designing, operation and management. Therefore, the osm2gmns develops the functionality of complex intersection consolidation. Users are enabled to consolidate intersections into a single node while parsing networks. Fig. 1 shows the effect of consolidation via the NeXTA software. Note that NeXTA is a software for visualization, simulation, analysis, and calculation for transportation network, which is also developed by Dr. Xuesong (Simon) Zhou. 这里应该给一个NeXTA的下载地址或者GitHub Repo地址

![](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/consolidateComplexIntersections3.png)

**Fig. 8 The effect of complex intersection consolidation by the osm2gmns package**

## Python API

### **getNetFromFile**

```python
getNetFromFile(filename='map.osm',network_types=('auto',), link_types='all', POI=False, POI_sampling_ratio=1.0, strict_mode=True, offset='no', min_nodes=1, combine=False, bbox=None, default_lanes=False, default_speed=False, default_capacity=False)
```
Get network object from file. Supports _\*.osm, \*.xml, and \*.pbf_ file extensions read from a local filesystem. 

It is from: **_osm2gmns.osmnet.built_net.py_**.

**Parameters:**


**filename : _str, path object or file-like object, default ‘map.osm’_**

Name of the openstreetmap file. Now the osm2gmns package supports three types of input files: _\*.osm, \*.xml, and \*.pbf_. Note that you need to add the suffix to explicitly express the file type, and the directory of the input file is also needed to be specified.

**network_types : _string, tuple of strings, list of strings, or set of strings, default_ (_'auto'_,)**

The osm2gmns package supports five different network types. Use this parameter to configure the type of the network to be parsed. The type of the network can be: _auto, bike, walk, railway_, or _aeroway_.

**link_types : _string, tuple of strings, list of strings, or set of strings, default 'all'_**

Configure the type of links in the network to be parsed. The type of the link can be: _motorway, trunk, primary, secondary, tertiary, residential, service, cycleway, footway, track, unclassified, connector, railway,_ or _aeroway_.

**POI : _bool, default False_**

Controls whether to extract POI (Point of Interest) information from the OSM map file. If argument **_POI_** is set as **_True_**, then the POI information will be loaded into the **_Network_** object.

**POI_sampling_ratio : _int, or float, default 1.0_**

Percentage of POI information to be extracted as a sample. This value should be no less than 0.0 and be no greater than 1.0.

**strict_mode : _bool, default True_**

Controls whether the strict mode is activated for parsing the network. If argument **_strict\_mode_** is set as **_False_**, all links in the OSM network file will be loaded into the **_Network_** object.

![bstrict1](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/bstrict1.png)

**Fig. 9 Parsed network with _strict\_mode=False_**

![bstrict2](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/bstrict2.png)

**Fig. 10 Parsed network with _strict\_mode=True_**

**offset : _string, default 'no'_**

Controls whether to make offset for links in the macroscopic network. The value of this parameter can be: "_left_", "_right_", or "_no_".

![offset1](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/offset1.png)

**Fig. 11 Parsed network with _offset=no_**

![offset2](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/offset2.png)

**Fig. 12 Parsed network with _offset=right_**

![offset3](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/offset3.png)

**Fig. 13 Parsed network with _offset=left_**

**min_nodes : _int, default 1_**

The loaded network may contain several sub-networks, with some sub networks are not accessible from others. In most cases, the whole network includes a large sub network and some isolated nodes or links. When the number of nodes of a sub network is less than argument **_min_nodes_** (default: 1), this sub network will be discarded.

**combine : _bool, default False_**

Users can use argument _combine_ to control whether to carry out the short link combinations. If _combine_ is enabled, two-degree nodes (one incoming link and one outgoing link) will be removed, and two adjacent links will be combined to generate a new link.

**bbox : _a tuple of four float / int values, or a list of four float / int values, default None_**

Controls the geographical boundary of network object, consisting of minimum latitude, minimum longtitude, maximum latitude, and maximum longitude sequentially.

**default_lanes : _bool, or dict, default False_**

Whether to use the default settings for number of lanes. You can customize the lanes count settings by passing the information in a dict data structure to this parameter.

**default_speed : _bool, or dict, default False_**

Whether to use the default settings for speed. You can customize the speed settings by passing speed information in a dict data structure to this parameter.

**default_capacity : _bool, or dict, default False_**

Whether to use the default settings for capacity. You can customize the capacity settings by passing capacity information in a dict data structure to this parameter.

**Returns : _osm2gmns.networkclass.macronet.Network_**

This method returns an instance of **_Network_** object.

### **consolidateComplexIntersections**

```python
consolidateComplexIntersections(network, auto_identify=False, int_buffer=20.0)
```

Consolidate complex intersections into one node for a network. In OpenStreetMap, one large intersection is often represented by multiple nodes. This structure brings some difficulties when conducting traffic simulations (hard to model traffic signals in these intersections). The osm2gmns package enables users to consolidate intersections while parsing networks, i.e., generate a new node to replace existing nodes for each large intersection.

![](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/consolidateComplexIntersections1.png)

**Fig. 14 The visualization of a intersection before the consolidation**

![](https://github.com/marcolee19970823/osm2gmns_user_guide/blob/main/media/consolidateComplexIntersections2.png)

**Fig. 15 The visualization of a intersection after the consolidation**

**Parameters:**

**network : _object_**

Instance of network class, which has intersections to be consolidated. 

**auto_identify : _bool, default False_**

Whether to automatically identify complex intersections by built-in methods from the osm2gmns package.

**int_buffer : _float, default 20.0_**

A threshold to check whether two connected nodes belong to the same intersection. Specifically, if the length of the link which connects two nodes is shorter than int_buffer, then the two nodes are considered to be from the same intersection. Note that the unit of this parameter is meter.

**Returns : _None_**

This method modifies information of input network instance and returns None.

### generateNodeActivityInfo
```python
generateNodeActivityInfo(network)
```
Generate activity type of nodes and add such information into the network. The activity types of nodes include: motorway, primary, secondary, tertiary, residential, etc. Note that the activity information of nodes is by adjacent links. The field "_activity_type_" and "_is_boundary_" will be generated and loaded into the CSV file recording the information for nodes.   

**Parameters:**

**network : _object_**

The instance of the _Network_ class.

**Returns : _None_**

This method modifies information of input network object and returns None.

### buildMultiResolutionNets
```python
buildMultiResolutionNets(macronet, auto_movement_generation=True, connector_type=None, width_of_lane=3.5, length_of_cell=7.0)
```

Build multi-resolution networks from the source (macroscopic) network, namely the mesoscopic network and the microscopic network.

**Parameters:**

**macronet : _object_**

The instance of _osm2gmns.networkclass.macronet.Network_ class.

**auto_movement_generation : _bool, default True_**

Controls whether automatically generate movement information for macronet.

**connector_type : _int, default None_**

Configure the link type of connectors.

**width_of_lane : _float, default 3.5_**

The width of lanes, note that the unit of this parameter is meter.

**length_of_cell : _float, default 7.0_**

The length of cells, note that the unit of this parameter is meter.

**Returns : _None_**

This method modifies information of input macronet and returns None.


### outputNetToCSV
```python
outputNetToCSV(network, output_folder='', prefix='', projection=False, encoding=None)
```
Output network information to CSV files.

**Parameters:**

**network : _object_**

The instance of **_osm2gmns.networkclass.macronet.Network_** class.

**output_folder : _str_**

Directory in which the output CSV files locate. Users can use argument _output_folder_ to specify the folder to store output files. 

**prefix : _str_**

Prefix of output CSV files.

**projection : _bool, default False_**

Choose the way to process the information about geometry and coordinates.

**encoding : _str, default None_**

A string representing the encoding to use in the output file.

**Returns : _None_**

This method outputs the information into CSV files and returns None.

### **loadNetFromCSV**

```python
loadNetFromCSV(folder='', node_file=None, link_file=None, movement_file=None, segment_file=None, geometry_file=None, POI_file=None, coordinate_type='lonlat', enconding=None)
```

Read CSV files and subtract information of the network. The information will be loaded into the **_osm2gmns.networkclass.macronet.Network_** class.

**Parameters:**

**folder : _str_**

Directory in which the input CSV files locate.

**node_file : _str_**

A string representing the name of CSV file which stores the information of nodes. Note that the file extension should also be added into the string.

**link_file : _str_**

A string representing the name of CSV file which stores the information of links. Note that the file extension should also be added into the string.

**movement_file : _str_**

A string representing the name of CSV file which stores the information of movements. Note that the file extension should also be added into the string.

**segment_file : _str_**

A string representing the name of CSV file which stores the information of segments. Note that the file extension should also be added into the string.

**geometry_file : _str_**

A string representing the name of CSV file which stores the information of geometries. Note that the file extension should also be added into the string.

**POI_file : _str_**

A string representing the name of CSV file which stores the information of POIs. Note that the file extension should also be added into the string.

**coordinate_type : _str, default 'lonlat'_**

A string controlling the type of the coordinate information. Three types are supported in osm2gmns packages, including '_lonlat_', '_meter_', and '_feet_'.

**encoding : _str, default None_**

A string representing the encoding to use in the input file.

**Returns : _osm2gmns.networkclass.macronet.Network_**

This method returns an instance of **_Network_** object.

## Workflow

The osm2gmns package aims to transfer network data from OpenStreetMap (OSM) to GMNS format and generate multi-resolution networks (MRMs).

Step 1: Download map file from [OpenStreetMap](https://www.openstreetmap.org/) website.

Step 2: Use osm2gmns package to read the downloaded map file and generate readable and editable CSV files storing network information with different spatial granularities.

Step 3: Load CSV files of networks via GIS software (i.e., [QGIS](https://www.qgis.org/en/site/) and [NeXTA](https://github.com/asu-trans-ai-lab/NeXTA4GMNS)) to visualize the MRMs. 

Step 4: Check whether there is any missing, out of date, partial or inaccurate data. 

Step 5: Manully modify the information in CSV files of the **_macroscopic_** network.

Step 6: Read the modified CSV files and regenerate mesoscopic and microscopic networks by osm2gmns package. 

Please try the illustration [code](https://github.com/marcolee19970823/osm2gmns_user_guide/tree/main/osm2gmns_illustration_code) for a quick start.

## Default values

For convenience, osm2gmns package provides default values for parameters and variables.

**Table 9. The default settings associated with various link types**


| Link Type | Number of lanes (No unit) | Default Speed (km/h) | Default Capacity (PCE/lane/h) |
| --- | --- | --- | --- |
| motorway | 4 | 120 | 2300 |
| trunk | 3 | 100 | 2200 |
| primary | 3 | 80 | 1800 |
| secondary | 2 | 60 | 1600 |
| tertiary | 2 | 40 | 1200 |
| residential | 1 | 30 | 1000 |
| service | 1 | 30 | 800 |
| cycleway | 1 | 5 | 800 |
| footway | 1 | 5 | 800 |
| track | 1 | 30 | 800 |
| unclassified | 1 | 30 | 800 |
| connector | 2 | 120 | 9999 |

## Structure of the osm2gmns package

The osm2gmns package is composed of the following sub-packages the modules, as listed in Table 10.

**Table 10. The structure of the osm2gmns package**


| Sub-package | Module | Brief description | 
| --- | --- | --- | 
| io | \_\_init\_\_.py | Empty file. |
|  | downloader.py | Download map file from OSM. | 
|  | load_from_csv.py | Load network from CSV files. |
|  | output_mrnet.py | Generate MRMs and output them into CSV files. |
|  | read_from_osm.py | Read information from OSM files. |
|  | readfile_mp.py | Read files in a multi-processing way. |
|  | writefile.py | Output MRMs into CSV files. |
| movement | \_\_init\_\_.py | Empty file. |
| | auto_connection.py | Generate movements. |
| multiresolutionnet | \_\_init\_\_.py | Empty file. |
|  | built_mrnet.py | Build MRMs objects. |
|  | netgen.py | Define classes representing MRMs. |
| networkclass | \_\_init\_\_.py | Empty file. |
| | basenet.py | Define classes representing the basic network. |
| | macronet.py | Define classes representing the macroscopic network. |
| | mesonet.py | Define classes representing the mesoscopic network. |
| | micronet.py | Define classes representing the microscopic network. |

## Contribution

Any contributions are welcomed including advise new applications of **_osm2gmns_**, enhance documentation (this guideline and [docstrings](https://docs.python-guide.org/writing/documentation/#writing-docstrings) in the source code), refactor and/or optimize the source code, report and/or resolve potential issues/bugs, suggest and/or add new functionalities, etc.

## Citation
Lu, J. and Zhou, X. _osm2gmns_. https://github.com/jiawlu/OSM2GMNS. Accessed Month, Day, Year.

## Acknowledgement
This project is partially supported by National Science Foundation – United States under Grant No. CMMI 1663657 “Collaborative Research: Real-time Management of Large Fleets of Self-Driving Vehicles Using Virtual CyberTracks”

The second author also thanks for the early support from FHWA project titled “The Effective Integration of Analysis, Modeling, and Simulation Tools-AMS DATA HUB CONCEPT OF OPERATIONS”. https://www.fhwa.dot.gov/publications/research/operations/13036/004.cfm

This document is prepared with the help from [Chongnan Li](https://github.com/marcolee19970823).
