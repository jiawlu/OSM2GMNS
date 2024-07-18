//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_NETWORKS_H
#define OSM2GMNS_NETWORKS_H

#include <absl/container/flat_hash_set.h>
#include <geos/geom/Geometry.h>
#include <geos/geom/LineString.h>
#include <geos/geom/MultiPolygon.h>
#include <geos/geom/Point.h>
#include <geos/geom/Polygon.h>

#include <cstddef>
#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <vector>

#include "osmconfig.h"
#include "osmnetwork.h"
// #include <map>
// #include <string>
// #include <vector>
//
// #include "geos/geom/Geometry.h"
//
//
using NetIdType = int64_t;

class Node;
class Link;

class Node {
 public:
  explicit Node(const OsmNode* osm_node, const geos::geom::GeometryFactory* factory);

  void setNodeId(NetIdType node_id);

  [[nodiscard]] NetIdType nodeId() const;
  [[nodiscard]] OsmIdType osmNodeId() const;
  [[nodiscard]] const std::string& name() const;
  [[nodiscard]] const std::unique_ptr<geos::geom::Point>& geometry() const;

 private:
  NetIdType node_id_{-1};
  OsmIdType osm_node_id_{-1};
  const OsmNode* osm_node_;
  std::string name_;
  std::unique_ptr<geos::geom::Point> geometry_;
  //  unsigned long osm_node_id{};
  //  std::string osm_highway{};
  //  std::string ctrl_type{};
  //  Geometry* geometry{};
  //  double x{}, y{};
  //  std::string notes{};

  std::vector<Link*> outgoing_link_vector_;
  std::vector<Link*> incoming_link_vector_;

  //  void buildFromOSMNode(OSMNode* osmnode) {
  //    name = osmnode->name();
  //    osm_node_id = osmnode->osm_node_id;
  //    osm_highway = osmnode->osm_highway;
  //    ctrl_type = osmnode->ctrl_type;
  //    geometry = osmnode->geometry;
  //    x = osmnode->x;
  //    y = osmnode->y;
  //    self.geometry_xy = osmnode.geometry_xy notes = osmnode->notes;
  //  }
};

class Link {
 public:
  explicit Link(Node* from_node, Node* to_node);
  explicit Link(const OsmWay* osm_way, const std::vector<OsmNode*>& osm_nodes, bool forward_direction,
                const geos::geom::GeometryFactory* factory);

  [[nodiscard]] NetIdType linkId() const;
  [[nodiscard]] OsmIdType osmWayId() const;
  [[nodiscard]] const std::string& name() const;
  [[nodiscard]] OsmNode* fromOsmNode() const;
  [[nodiscard]] OsmNode* toOsmNode() const;
  [[nodiscard]] Node* fromNode() const;
  [[nodiscard]] Node* toNode() const;
  [[nodiscard]] HighWayLinkType highwayLinkType() const;
  [[nodiscard]] const std::unique_ptr<geos::geom::LineString>& geometry() const;
  [[nodiscard]] std::optional<int32_t> lanes() const;
  [[nodiscard]] std::optional<float> freeSpeed() const;
  [[nodiscard]] const std::string& toll() const;

  void setLinkId(NetIdType link_id);
  void setFromNode(Node* from_node);
  void setToNode(Node* to_node);

 private:
  NetIdType link_id_{-1};
  OsmIdType osm_way_id_{-1};
  std::string name_;
  OsmNode* from_osm_node_{nullptr};
  OsmNode* to_osm_node_{nullptr};
  Node* from_node_{nullptr};
  Node* to_node_{nullptr};
  HighWayLinkType highway_link_type_{HighWayLinkType::OTHER};
  std::unique_ptr<geos::geom::LineString> geometry_;
  std::optional<int32_t> lanes_;
  std::optional<float> free_speed_;
  std::string toll_;
};

class POI {
 public:
  explicit POI(const OsmWay* osm_way, std::unique_ptr<geos::geom::Polygon> geometry);
  explicit POI(const OsmRelation* osm_relation, std::unique_ptr<geos::geom::MultiPolygon> geometry);

  [[nodiscard]] NetIdType poiId() const;
  [[nodiscard]] const std::string& name() const;
  [[nodiscard]] std::optional<OsmIdType> osmWayId() const;
  [[nodiscard]] std::optional<OsmIdType> osmRelationId() const;
  [[nodiscard]] const std::string& building() const;
  [[nodiscard]] const std::string& amenity() const;
  [[nodiscard]] const std::string& leisure() const;
  [[nodiscard]] const std::unique_ptr<geos::geom::Geometry>& geometry() const;
  [[nodiscard]] const std::unique_ptr<geos::geom::Point>& centroidGeometry() const;

  void setPOIId(NetIdType poi_id);

 private:
  NetIdType poi_id_{-1};
  std::string name_;
  std::optional<OsmIdType> osm_way_id_;
  std::optional<OsmIdType> osm_relation_id_;
  std::string building_;
  std::string amenity_;
  std::string leisure_;

  std::unique_ptr<geos::geom::Geometry> geometry_;
  std::unique_ptr<geos::geom::Point> centroid_geometry_;
};

class Network {
 public:
  explicit Network(OsmNetwork* osmnet, absl::flat_hash_set<HighWayLinkType> link_types,
                   absl::flat_hash_set<HighWayLinkType> connector_link_types, bool POI);
  ~Network();
  Network(const Network&) = delete;
  Network& operator=(const Network&) = delete;
  Network(Network&&) = delete;
  Network& operator=(Network&&) = delete;

  [[nodiscard]] size_t numberOfNodes() const;
  [[nodiscard]] size_t numberOfLinks() const;
  [[nodiscard]] const std::vector<Node*>& nodeVector() const;
  [[nodiscard]] const std::vector<Link*>& linkVector() const;
  [[nodiscard]] const std::vector<POI*>& poiVector() const;

 private:
  void createNodesAndLinksFromOsmNetwork();
  void createNodesAndLinksFromOneWay(const OsmWay* osm_way, std::vector<std::vector<Link*>>& m_link_vector);
  [[nodiscard]] std::vector<OsmWay*> identifyConnectorWays() const;
  void createPOIsFromOsmNetwork();
  void createPOIsFromOsmWays(std::vector<std::vector<POI*>>& m_poi_vector);
  void createPOIsFromOneOsmWay(const OsmWay* osm_way, std::vector<std::vector<POI*>>& m_poi_vector);
  void createPOIsFromOsmRelations(std::vector<std::vector<POI*>>& m_poi_vector);
  void createPOIsFromOneOsmRelation(const OsmRelation* osm_relation, std::vector<std::vector<POI*>>& m_poi_vector);

  OsmNetwork* osmnet_;
  geos::geom::GeometryFactory::Ptr factory_;
  absl::flat_hash_set<HighWayLinkType> link_types_;
  absl::flat_hash_set<HighWayLinkType> connector_link_types_;
  bool POI_;

  // absl::flat_hash_map<NetIdType, Node*> node_dict_;
  // absl::flat_hash_map<NetIdType, Link*> link_dict_;
  std::vector<Node*> node_vector_;
  std::vector<Link*> link_vector_;
  std::vector<POI*> poi_vector_;

  NetIdType max_node_id_{0};
  NetIdType max_link_id_{0};
};

#endif  // OSM2GMNS_NETWORKS_H
