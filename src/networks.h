//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_NETWORKS_H
#define OSM2GMNS_NETWORKS_H

#include <absl/container/flat_hash_map.h>
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

using NetIdType = int64_t;

class Node;
class Link;

class Node {
 public:
  explicit Node(const OsmNode* osm_node, const geos::geom::GeometryFactory* factory);
  explicit Node(NetIdType node_id, const std::vector<Node*>& nodes, NetIdType intersection_id,
                const geos::geom::GeometryFactory* factory);

  void setNodeId(NetIdType node_id);
  void setZoneId(NetIdType zone_id);
  void setBoundary(int16_t boundary);
  void setActivityType(HighWayLinkType activity_type);
  void setIntersectionId(NetIdType intersection_id);
  // void setIsValid(bool is_valid);
  void addIncomingLink(Link* link);
  void addOutgoingLink(Link* link);

  [[nodiscard]] NetIdType nodeId() const;
  [[nodiscard]] const std::vector<const OsmNode*>& osmNodes() const;
  [[nodiscard]] std::string osmNodeId() const;
  [[nodiscard]] const std::string& name() const;
  [[nodiscard]] bool isSignalized() const;
  [[nodiscard]] const std::unique_ptr<geos::geom::Point>& geometry() const;
  [[nodiscard]] std::optional<NetIdType> zoneId() const;
  [[nodiscard]] std::optional<int16_t> boundary() const;
  [[nodiscard]] std::optional<HighWayLinkType> activityType() const;
  [[nodiscard]] std::optional<NetIdType> intersectionId() const;
  // [[nodiscard]] bool isValid() const;
  [[nodiscard]] const std::vector<Link*>& incomingLinkVector() const;
  [[nodiscard]] const std::vector<Link*>& outgoingLinkVector() const;

 private:
  NetIdType node_id_{-1};
  std::vector<const OsmNode*> osm_nodes_;
  std::string name_;
  bool is_signalized_{false};
  std::unique_ptr<geos::geom::Point> geometry_;
  std::optional<NetIdType> zone_id_;
  // boundary: 0 - not a boundary node; -1 - incoming only; 1 - outgoing only; 2 - both incoming and outgoing
  std::optional<int16_t> boundary_;
  std::optional<HighWayLinkType> activity_type_;
  std::optional<NetIdType> intersection_id_;
  // bool is_valid_{true};
  //  unsigned long osm_node_id{};
  //  std::string osm_highway{};
  //  std::string ctrl_type{};
  //  Geometry* geometry{};
  //  double x{}, y{};
  //  std::string notes{};

  std::vector<Link*> incoming_link_vector_;
  std::vector<Link*> outgoing_link_vector_;
};

class Link {
 public:
  explicit Link(Node* from_node, Node* to_node);
  explicit Link(const OsmWay* osm_way, const std::vector<OsmNode*>& osm_nodes, bool forward_direction,
                size_t osm_way_seq_, const geos::geom::GeometryFactory* factory);

  [[nodiscard]] NetIdType linkId() const;
  [[nodiscard]] OsmIdType osmWayId() const;
  [[nodiscard]] size_t osmWaySeq() const;
  [[nodiscard]] const std::string& name() const;
  [[nodiscard]] OsmNode* fromOsmNode() const;
  [[nodiscard]] OsmNode* toOsmNode() const;
  [[nodiscard]] Node* fromNode() const;
  [[nodiscard]] Node* toNode() const;
  [[nodiscard]] HighWayLinkType highwayLinkType() const;
  [[nodiscard]] const std::unique_ptr<geos::geom::LineString>& geometry() const;
  [[nodiscard]] double length() const;
  // [[nodiscard]] bool isValid() const;
  [[nodiscard]] std::optional<int32_t> lanes() const;
  [[nodiscard]] std::optional<float> freeSpeed() const;
  [[nodiscard]] std::string freeSpeedRaw() const;
  [[nodiscard]] std::optional<int32_t> capacity() const;
  [[nodiscard]] const std::vector<ModeType>& allowedModeTypes() const;
  [[nodiscard]] const std::string& toll() const;

  void setLinkId(NetIdType link_id);
  void setFromNode(Node* from_node);
  void setToNode(Node* to_node);
  void setLanes(int32_t lanes);
  void setFreeSpeed(float free_speed);
  void setCapacity(int32_t capacity);
  // void setIsValid(bool is_valid);

 private:
  NetIdType link_id_{-1};
  OsmIdType osm_way_id_{-1};
  size_t osm_way_seq_{0};
  std::string name_;
  OsmNode* from_osm_node_{nullptr};
  OsmNode* to_osm_node_{nullptr};
  Node* from_node_{nullptr};
  Node* to_node_{nullptr};
  HighWayLinkType highway_link_type_{HighWayLinkType::OTHER};
  std::unique_ptr<geos::geom::LineString> geometry_;
  double length_{-1.0};
  // bool is_valid_{true};
  std::optional<int32_t> lanes_;
  std::optional<float> free_speed_;
  std::string free_speed_raw_;
  std::optional<int32_t> capacity_;
  std::vector<ModeType> allowed_mode_types_;
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

class Zone {
 public:
  explicit Zone(NetIdType zone_id, std::unique_ptr<geos::geom::Geometry> geometry);

  [[nodiscard]] NetIdType zoneId() const;
  [[nodiscard]] const std::unique_ptr<geos::geom::Geometry>& geometry() const;

 private:
  NetIdType zone_id_;
  std::unique_ptr<geos::geom::Geometry> geometry_;
};

class Intersection {
 public:
  explicit Intersection();

 private:
  NetIdType intersection_id_{};
};

class Network {
 public:
  explicit Network(OsmNetwork* osmnet, absl::flat_hash_set<HighWayLinkType> link_types,
                   absl::flat_hash_set<HighWayLinkType> connector_link_types, bool POI, float POI_sampling_ratio);
  ~Network();
  Network(const Network&) = delete;
  Network& operator=(const Network&) = delete;
  Network(Network&&) = delete;
  Network& operator=(Network&&) = delete;

  [[nodiscard]] bool poi() const;
  [[nodiscard]] size_t numberOfNodes() const;
  [[nodiscard]] size_t numberOfLinks() const;
  [[nodiscard]] const std::vector<Node*>& nodeVector() const;
  [[nodiscard]] const std::vector<Link*>& linkVector() const;
  [[nodiscard]] const std::vector<POI*>& poiVector() const;

  void generateNodeActivityInfo(const std::vector<Zone*>& zone_vector = {});
  void fillLinkAttributesWithDefaultValues(const absl::flat_hash_map<HighWayLinkType, int32_t>& default_lanes_dict,
                                           const absl::flat_hash_map<HighWayLinkType, float>& default_speed_dict,
                                           const absl::flat_hash_map<HighWayLinkType, int32_t>& default_capacity_dict);
  void consolidateComplexIntersections(bool auto_identify, const std::vector<Intersection*>& intersection_vector,
                                       float int_buffer);

 private:
  void createNodesAndLinksFromOsmNetwork();
  void createNodesAndLinksFromOneWay(const OsmWay* osm_way, std::vector<std::vector<Link*>>& m_link_vector);
  [[nodiscard]] std::vector<OsmWay*> identifyConnectorWays() const;
  void createPOIsFromOsmNetwork();
  void createPOIsFromOsmWays(std::vector<std::vector<POI*>>& m_poi_vector);
  void createPOIsFromOneOsmWay(const OsmWay* osm_way, std::vector<std::vector<POI*>>& m_poi_vector);
  void createPOIsFromOsmRelations(std::vector<std::vector<POI*>>& m_poi_vector);
  void createPOIsFromOneOsmRelation(const OsmRelation* osm_relation, std::vector<std::vector<POI*>>& m_poi_vector);

  void identifyComplexIntersections(float int_buffer);

  OsmNetwork* osmnet_;
  std::optional<std::unique_ptr<geos::geom::Polygon>> boundary_;
  geos::geom::GeometryFactory::Ptr factory_;
  absl::flat_hash_set<HighWayLinkType> link_types_;
  absl::flat_hash_set<HighWayLinkType> connector_link_types_;
  bool POI_;
  float POI_sampling_ratio_;

  // absl::flat_hash_map<NetIdType, Node*> node_dict_;
  // absl::flat_hash_map<NetIdType, Link*> link_dict_;
  std::vector<Node*> node_vector_;
  std::vector<Link*> link_vector_;
  std::vector<POI*> poi_vector_;

  NetIdType max_node_id_{0};
  NetIdType max_link_id_{0};
  NetIdType max_intersection_id_{0};
};

#endif  // OSM2GMNS_NETWORKS_H
