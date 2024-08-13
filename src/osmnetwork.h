//
// Created by Lu, Jiawei on 5/23/24.
//

#ifndef OSM2GMNS_OSMNETWORK_H
#define OSM2GMNS_OSMNETWORK_H

#include <absl/container/flat_hash_map.h>
#include <absl/container/flat_hash_set.h>
#include <geos/geom/Geometry.h>
#include <geos/geom/GeometryFactory.h>

#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>
#include <osmium/handler.hpp>
#include <osmium/osm/item_type.hpp>
#include <osmium/osm/node.hpp>
#include <osmium/osm/relation.hpp>
#include <osmium/osm/way.hpp>
#include <string>
#include <vector>

#include "osmconfig.h"

class OsmNode;
class OsmWay;
class OsmRelation;

class OsmHandler : public osmium::handler::Handler {
 public:
  explicit OsmHandler(const absl::flat_hash_set<ModeType>& mode_types, absl::flat_hash_set<HighWayLinkType> link_types,
                      absl::flat_hash_set<HighWayLinkType> connector_link_types, bool POI);

  void node(const osmium::Node& node);
  void way(const osmium::Way& way);
  void relation(const osmium::Relation& relation);

  void updateParseTargets(bool parse_node, bool parse_way, bool parse_relation);

  std::vector<OsmNode*>& osmNodeVector();
  std::vector<OsmWay*>& osmWayVector();
  std::vector<OsmRelation*>& osmRelationVector();

 private:
  bool parse_node_{false};
  bool parse_way_{false};
  bool parse_relation_{false};
  absl::flat_hash_set<OsmIdType> nodes_used_in_ways_;
  absl::flat_hash_set<OsmIdType> ways_used_in_relations_;

  absl::flat_hash_set<ModeType> highway_mode_types_;
  bool include_railway_{false};
  bool include_aeroway_{false};
  absl::flat_hash_set<HighWayLinkType> link_types_;
  absl::flat_hash_set<HighWayLinkType> connector_link_types_;
  bool POI_{false};

  std::vector<OsmNode*> osm_node_vector_;
  std::vector<OsmWay*> osm_way_vector_;
  std::vector<OsmRelation*> osm_relation_vector_;
};

class OsmNode {
 public:
  explicit OsmNode(const osmium::Node& node);

  [[nodiscard]] OsmIdType osmNodeId() const;
  [[nodiscard]] const std::string& name() const;
  [[nodiscard]] double getX() const;
  [[nodiscard]] double getY() const;
  // [[nodiscard]] const std::unique_ptr<geos::geom::Point>& geometry() const;
  [[nodiscard]] bool isSignalized() const;
  [[nodiscard]] int32_t usageCount() const;
  [[nodiscard]] bool isTypologyNode() const;
  [[nodiscard]] std::vector<OsmWay*> incomingWayVector() const;
  [[nodiscard]] std::vector<OsmWay*> outgoingWayVector() const;

  // void initOsmNode(const geos::geom::GeometryFactory* factory, const geos::geom::Polygon* boundary,
  //                  bool strict_boundary);
  void changeUsageCount(int32_t usage_count_changes);
  void setIsEndingNode(bool is_ending_node);
  void setIsTypologyNode();
  void addIncomingWay(OsmWay* osm_way);
  void addOutgoingWay(OsmWay* osm_way);

 private:
  OsmIdType osm_node_id_;
  std::string name_;
  // std::unique_ptr<geos::geom::Point> geometry_;
  double x, y;
  std::string highway_;
  // std::string signal_;

  bool is_signalized_{false};
  bool in_region_{true};

  int32_t usage_count_{0};
  bool is_ending_node_{false};
  bool is_typology_node_{false};
  std::vector<OsmWay*> incoming_way_vector_;
  std::vector<OsmWay*> outgoing_way_vector_;

  std::string notes_;
};

class OsmWay {
 public:
  explicit OsmWay(const osmium::Way& way);

  [[nodiscard]] OsmIdType osmWayId() const;
  [[nodiscard]] const std::string& name() const;
  [[nodiscard]] std::optional<int32_t> lanes() const;
  [[nodiscard]] std::optional<int32_t> forward_lanes() const;
  [[nodiscard]] std::optional<int32_t> backward_lanes() const;
  [[nodiscard]] const std::vector<OsmNode*>& refNodeVector() const;
  [[nodiscard]] OsmNode* fromNode() const;
  [[nodiscard]] OsmNode* toNode() const;
  [[nodiscard]] WayType wayType() const;
  [[nodiscard]] HighWayLinkType highwayLinkType() const;
  [[nodiscard]] bool isTargetLinkType() const;
  [[nodiscard]] bool isTargetConnectorLinkType() const;
  [[nodiscard]] std::optional<bool> isOneway() const;
  [[nodiscard]] bool isReversed() const;
  [[nodiscard]] std::optional<float> maxSpeed() const;
  [[nodiscard]] std::string maxSpeedRaw() const;
  [[nodiscard]] const std::string& toll() const;
  [[nodiscard]] const std::string& building() const;
  [[nodiscard]] const std::string& amenity() const;
  [[nodiscard]] const std::string& leisure() const;

  [[nodiscard]] const std::vector<OsmIdType>& refNodeIdVector() const;
  [[nodiscard]] const std::vector<ModeType>& allowedModeTypes() const;
  [[nodiscard]] bool includeTheWay() const;
  [[nodiscard]] const std::vector<std::vector<OsmNode*>>& segmentNodesVector() const;

  void identifyWayType(const absl::flat_hash_set<ModeType>& highway_mode_types, bool include_railway,
                       bool include_aeroway, const absl::flat_hash_set<HighWayLinkType>& link_types,
                       const absl::flat_hash_set<HighWayLinkType>& connector_link_types, bool POI,
                       const absl::flat_hash_set<OsmIdType>& ways_used_in_relations);
  void initOsmWay(const absl::flat_hash_map<OsmIdType, OsmNode*>& osm_node_dict);
  void splitIntoSegments();

  // void setUsedByRelation(bool used_by_relation);

 private:
  void identifyHighwayType(const absl::flat_hash_set<ModeType>& highway_mode_types,
                           const absl::flat_hash_set<HighWayLinkType>& link_types,
                           const absl::flat_hash_set<HighWayLinkType>& connector_link_types);
  void identifyRailwayType();
  void identifyAerowayType();
  void generateHighwayAllowedModeTypes(const absl::flat_hash_set<ModeType>& highway_mode_types);
  void mapRefNodes(const absl::flat_hash_map<OsmIdType, OsmNode*>& osm_node_dict);
  void configAttributes();

  OsmIdType osm_way_id_;
  std::string highway_;
  std::string railway_;
  std::string aeroway_;
  std::string name_;
  std::string lanes_raw_;
  std::string forward_lanes_raw_;
  std::string backward_lanes_raw_;
  std::string oneway_raw_;
  std::string max_speed_raw_;
  std::optional<int32_t> lanes_;
  std::optional<int32_t> forward_lanes_;
  std::optional<int32_t> backward_lanes_;
  std::optional<bool> is_oneway_{true};
  bool is_reversed_{false};  // ToDo: use when generating segments
  std::optional<float> max_speed_;
  std::string toll_;

  std::string building_;
  std::string amenity_;
  std::string leisure_;
  std::string junction_;
  std::string area_;
  std::string motor_vehicle_;
  std::string motorcar_;
  std::string service_;
  std::string access_;
  std::string foot_;
  std::string bicycle_;

  std::vector<OsmIdType> ref_node_id_vector_;
  std::vector<OsmNode*> ref_node_vector_;
  OsmNode* from_node_{nullptr};
  OsmNode* to_node_{nullptr};
  bool contains_unknown_ref_nodes_{false};

  WayType way_type_{WayType::OTHER};
  std::vector<ModeType> allowed_mode_types_;
  HighWayLinkType highway_link_type_{HighWayLinkType::OTHER};
  bool is_target_link_type_{false};
  bool is_target_connector_link_type_{false};
  bool include_the_way_{false};
  // bool used_by_relation_{false};

  int number_of_segments_{0};
  std::vector<std::vector<OsmNode*>> segment_nodes_vector_;
};

class OsmRelation {
 public:
  explicit OsmRelation(const osmium::Relation& relation);

  void initOsmRelation(const absl::flat_hash_map<OsmIdType, OsmWay*>& osm_way_dict);

  [[nodiscard]] OsmIdType osmRelationId() const;
  [[nodiscard]] const std::string& name() const;
  [[nodiscard]] const std::vector<OsmIdType>& memberIdVector() const;
  [[nodiscard]] const std::vector<osmium::item_type>& memberTypeVector() const;
  [[nodiscard]] const std::vector<OsmWay*>& memberWayVector() const;
  [[nodiscard]] const std::vector<std::string>& memberWayRoleVector() const;
  [[nodiscard]] const std::string& building() const;
  [[nodiscard]] const std::string& amenity() const;
  [[nodiscard]] const std::string& leisure() const;

 private:
  OsmIdType osm_relation_id_;
  std::string name_;
  std::vector<OsmIdType> member_id_vector_;
  std::vector<osmium::item_type> member_type_vector_;
  std::vector<std::string> member_role_vector_;
  std::vector<OsmWay*> member_way_vector_;
  std::vector<std::string> member_way_role_vector_;
  std::string building_;
  std::string amenity_;
  std::string leisure_;
};

class OsmNetwork {
 public:
  explicit OsmNetwork(const std::filesystem::path& osm_filepath, absl::flat_hash_set<ModeType> mode_types,
                      absl::flat_hash_set<HighWayLinkType> link_types,
                      absl::flat_hash_set<HighWayLinkType> connector_link_types, bool POI, bool strict_boundary);
  ~OsmNetwork();
  OsmNetwork(const OsmNetwork&) = delete;
  OsmNetwork& operator=(const OsmNetwork&) = delete;
  OsmNetwork(OsmNetwork&&) = delete;
  OsmNetwork& operator=(OsmNetwork&&) = delete;

  [[nodiscard]] const std::optional<std::unique_ptr<geos::geom::Polygon>>& boundary() const;
  [[nodiscard]] const std::vector<OsmWay*>& osmWayVector() const;
  [[nodiscard]] const std::vector<OsmRelation*>& osmRelationVector() const;

 private:
  void processOsmData();
  void initializeElements();
  void createWaySegments();

  absl::flat_hash_set<ModeType> mode_types_;
  absl::flat_hash_set<HighWayLinkType> link_types_;
  absl::flat_hash_set<HighWayLinkType> connector_link_types_;
  bool POI_;
  bool strict_boundary_;

  geos::geom::GeometryFactory::Ptr factory_;
  std::optional<std::unique_ptr<geos::geom::Polygon>> boundary_;

  std::vector<OsmNode*> osm_node_vector_;
  std::vector<OsmWay*> osm_way_vector_;
  std::vector<OsmRelation*> osm_relation_vector_;

  // std::vector<OsmWay*> link_way_vector{};

  // geos::geom::Geometry* bounds{};
};

#endif  // OSM2GMNS_OSMNETWORK_H
