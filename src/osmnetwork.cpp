//
// Created by Lu, Jiawei on 5/23/24.
//

#include "osmnetwork.h"

#include <absl/container/flat_hash_map.h>
#include <absl/container/flat_hash_set.h>
#include <absl/log/log.h>
#include <absl/strings/match.h>
#include <geos/geom/Coordinate.h>
#include <geos/geom/GeometryFactory.h>
#include <geos/geom/Point.h>
#include <geos/geom/Polygon.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <iostream>
#include <memory>
#include <optional>
#include <osmium/io/any_input.hpp>  // NOLINT
#include <osmium/io/file.hpp>       // NOLINT
#include <osmium/io/reader.hpp>     // NOLINT
#include <osmium/osm/box.hpp>
#include <osmium/osm/item_type.hpp>
#include <osmium/osm/node.hpp>
#include <osmium/osm/relation.hpp>
#include <osmium/osm/tag.hpp>
#include <osmium/osm/way.hpp>
#include <osmium/visitor.hpp>  // NOLINT
#include <regex>
#include <string>
#include <utility>
#include <vector>

#include "constants.h"
#include "osmconfig.h"
#include "utils.h"

const char* getOSMTagValue(const osmium::TagList& tag_list, const char* tag_key) {
  const char* tag_value = tag_list[tag_key];
  return tag_value != nullptr ? tag_value : "";
}

OsmHandler::OsmHandler(const absl::flat_hash_set<ModeType>& mode_types, absl::flat_hash_set<HighWayLinkType> link_types,
                       absl::flat_hash_set<HighWayLinkType> connector_link_types, bool POI)
    : link_types_(std::move(link_types)), connector_link_types_(std::move(connector_link_types)), POI_(POI) {
  for (const ModeType mode_type : mode_types) {
    if (mode_type == ModeType::RAILWAY) {
      include_railway_ = true;
    } else if (mode_type == ModeType::AEROWAY) {
      include_aeroway_ = true;
    } else {
      highway_mode_types_.insert(mode_type);
    }
  }
}
void OsmHandler::node(const osmium::Node& node) { osm_node_vector_.push_back(new OsmNode(node)); }
void OsmHandler::way(const osmium::Way& way) {
  auto* osm_way = new OsmWay(way);
  osm_way->identifyWayType(highway_mode_types_, include_railway_, include_aeroway_, link_types_, connector_link_types_,
                           POI_);
  if (osm_way->includeTheWay()) {
    osm_way_vector_.push_back(osm_way);
  } else {
    delete osm_way;
  }
}
void OsmHandler::relation(const osmium::Relation& relation) {
  if (POI_) {
    auto* osm_relation = new OsmRelation(relation);
    if (osm_relation->building().empty() && osm_relation->amenity().empty() && osm_relation->leisure().empty()) {
      delete osm_relation;
    } else {
      osm_relation_vector_.push_back(osm_relation);
    }
  }
}

std::vector<OsmNode*>& OsmHandler::osmNodeVector() { return osm_node_vector_; }
std::vector<OsmWay*>& OsmHandler::osmWayVector() { return osm_way_vector_; }
std::vector<OsmRelation*>& OsmHandler::osmRelationVector() { return osm_relation_vector_; }

OsmNode::OsmNode(const osmium::Node& node)
    : osm_node_id_(node.id()),
      x(node.location().lon()),
      y(node.location().lat()),
      name_(getOSMTagValue(node.tags(), "name")),
      highway_(getOSMTagValue(node.tags(), "highway")) {
  if (absl::StrContains(highway_, "signal")) {
    is_signalized_ = true;
  }
}

OsmIdType OsmNode::osmNodeId() const { return osm_node_id_; }
const std::string& OsmNode::name() const { return name_; }
const std::unique_ptr<geos::geom::Point>& OsmNode::geometry() const { return geometry_; }
bool OsmNode::isSignalized() const { return is_signalized_; }
int32_t OsmNode::usageCount() const { return usage_count_; }
bool OsmNode::isTypologyNode() const { return is_typology_node_; }
std::vector<OsmWay*> OsmNode::incomingWayVector() const { return incoming_way_vector_; }
std::vector<OsmWay*> OsmNode::outgoingWayVector() const { return outgoing_way_vector_; }

void OsmNode::initOsmNode(const geos::geom::GeometryFactory* factory, const geos::geom::Polygon* boundary,
                          bool strict_boundary) {
  geometry_ = factory->createPoint(geos::geom::Coordinate(x, y));
  if (strict_boundary && !boundary->covers(geometry_.get())) {
    in_region_ = false;
  }
}
void OsmNode::changeUsageCount(int32_t usage_count_changes = 1) { usage_count_ += usage_count_changes; }
void OsmNode::setIsEndingNode(bool is_ending_node) { is_ending_node_ = is_ending_node; }
void OsmNode::setIsTypologyNode() { is_typology_node_ = is_ending_node_ || usage_count_ >= 2 || is_signalized_; }
void OsmNode::addIncomingWay(OsmWay* osm_way) { incoming_way_vector_.push_back(osm_way); }
void OsmNode::addOutgoingWay(OsmWay* osm_way) { outgoing_way_vector_.push_back(osm_way); }

OsmWay::OsmWay(const osmium::Way& way)
    : osm_way_id_(way.id()),
      highway_(getOSMTagValue(way.tags(), "highway")),
      railway_(getOSMTagValue(way.tags(), "railway")),
      aeroway_(getOSMTagValue(way.tags(), "aeroway")),
      name_(getOSMTagValue(way.tags(), "name")),
      lanes_raw_(getOSMTagValue(way.tags(), "lanes")),
      forward_lanes_raw_(getOSMTagValue(way.tags(), "lanes:forward")),
      backward_lanes_raw_(getOSMTagValue(way.tags(), "lanes:backward")),
      oneway_raw_(getOSMTagValue(way.tags(), "oneway")),
      max_speed_raw_(getOSMTagValue(way.tags(), "maxspeed")),
      toll_(getOSMTagValue(way.tags(), "toll")),
      building_(getOSMTagValue(way.tags(), "building")),
      amenity_(getOSMTagValue(way.tags(), "amenity")),
      leisure_(getOSMTagValue(way.tags(), "leisure")),
      junction_(getOSMTagValue(way.tags(), "junction")),
      area_(getOSMTagValue(way.tags(), "area")),
      motor_vehicle_(getOSMTagValue(way.tags(), "motor_vehicle")),
      motorcar_(getOSMTagValue(way.tags(), "motorcar")),
      service_(getOSMTagValue(way.tags(), "service")),
      access_(getOSMTagValue(way.tags(), "access")),
      foot_(getOSMTagValue(way.tags(), "foot")),
      bicycle_(getOSMTagValue(way.tags(), "bicycle")) {
  for (const auto& way_node : way.nodes()) {
    ref_node_id_vector_.push_back(way_node.ref());
  }
}

OsmIdType OsmWay::osmWayId() const { return osm_way_id_; }
const std::string& OsmWay::name() const { return name_; }
std::optional<int32_t> OsmWay::lanes() const { return lanes_; }
std::optional<int32_t> OsmWay::forward_lanes() const { return forward_lanes_; }
std::optional<int32_t> OsmWay::backward_lanes() const { return backward_lanes_; }
const std::vector<OsmNode*>& OsmWay::refNodeVector() const { return ref_node_vector_; }
OsmNode* OsmWay::fromNode() const { return from_node_; }
OsmNode* OsmWay::toNode() const { return to_node_; }
WayType OsmWay::wayType() const { return way_type_; };
HighWayLinkType OsmWay::highwayLinkType() const { return highway_link_type_; }
bool OsmWay::isTargetLinkType() const { return is_target_link_type_; }
bool OsmWay::isTargetConnectorLinkType() const { return is_target_connector_link_type_; }
std::optional<bool> OsmWay::isOneway() const { return is_oneway_; }
bool OsmWay::isReversed() const { return is_reversed_; }
std::optional<float> OsmWay::maxSpeed() const { return max_speed_; }
std::string OsmWay::maxSpeedRaw() const { return max_speed_raw_; }
const std::string& OsmWay::toll() const { return toll_; }
const std::string& OsmWay::building() const { return building_; }
const std::string& OsmWay::amenity() const { return amenity_; }
const std::string& OsmWay::leisure() const { return leisure_; }
const std::vector<ModeType>& OsmWay::allowedModeTypes() const { return allowed_mode_types_; }
bool OsmWay::includeTheWay() const { return include_the_way_; }
const std::vector<std::vector<OsmNode*>>& OsmWay::segmentNodesVector() const { return segment_nodes_vector_; }

void OsmWay::identifyWayType(const absl::flat_hash_set<ModeType>& highway_mode_types, bool include_railway,
                             bool include_aeroway, const absl::flat_hash_set<HighWayLinkType>& link_types,
                             const absl::flat_hash_set<HighWayLinkType>& connector_link_types, bool POI) {
  if ((!(building_.empty() && amenity_.empty() && leisure_.empty())) ||
      (!highway_.empty() && isHighwayPoiType(highway_)) || (!railway_.empty() && isRailwayPoiType(railway_)) ||
      (!aeroway_.empty() && isAerowayPoiType(aeroway_))) {
    if (POI) {
      way_type_ = WayType::POI;
      include_the_way_ = true;
    }
    return;
  }

  if (area_.empty() || area_ == "no") {
    if (!highway_.empty()) {
      highway_link_type_ = highwayStringToLinkType(highway_);
      if (highway_link_type_ == HighWayLinkType::OTHER) {
        if (!isNegligibleHighwayType(highway_)) {
          LOG(WARNING) << "way " << osm_way_id_ << " has a new highway value " << highway_;
        }
        return;
      }
      if (link_types.empty() || link_types.find(highway_link_type_) != link_types.end()) {
        is_target_link_type_ = true;
      }
      if (connector_link_types.find(highway_link_type_) != connector_link_types.end()) {
        is_target_connector_link_type_ = true;
      }
      if (!is_target_link_type_ && !is_target_connector_link_type_) {
        return;
      }
      generateHighwayAllowedModeTypes(highway_mode_types);
      if (!allowed_mode_types_.empty()) {
        way_type_ = WayType::HIGHWAY;
        include_the_way_ = true;
      }
      return;
    }
    if (!railway_.empty()) {
      if (!include_railway || isNegligibleRailwayType(railway_)) {
        return;
      }
      way_type_ = WayType::RAILWAY;
      allowed_mode_types_ = {ModeType::RAILWAY};
      include_the_way_ = true;
      return;
    }
    if (!aeroway_.empty()) {
      if (!include_aeroway || isNegligibleAerowayType(aeroway_)) {
        return;
      }
      way_type_ = WayType::AEROWAY;
      allowed_mode_types_ = {ModeType::AEROWAY};
      include_the_way_ = true;
      return;
    }
  }
  if (POI) {
    include_the_way_ = true;
  }
}

void OsmWay::initOsmWay(const absl::flat_hash_map<OsmIdType, OsmNode*>& osm_node_dict) {
  if (way_type_ == WayType::OTHER && !used_by_relation_) {
    include_the_way_ = false;
    return;
  }
  mapRefNodes(osm_node_dict);
  if (way_type_ == WayType::HIGHWAY || way_type_ == WayType::RAILWAY || way_type_ == WayType::AEROWAY) {
    configAttributes();
  }
}

void OsmWay::splitIntoSegments() {
  const size_t number_of_ref_nodes = ref_node_vector_.size();
  if (number_of_ref_nodes < 2) {
    return;
  }
  int last_idx = 0;
  int idx = 0;
  OsmNode* osmnode = nullptr;

  while (true) {
    std::vector<OsmNode*> m_segment_node_vector{ref_node_vector_[last_idx]};
    for (idx = last_idx + 1; idx < number_of_ref_nodes; idx++) {
      osmnode = ref_node_vector_[idx];
      m_segment_node_vector.push_back(osmnode);
      if (osmnode->isTypologyNode()) {
        last_idx = idx;
        break;
      }
    }

    segment_nodes_vector_.push_back(m_segment_node_vector);
    number_of_segments_++;

    if (idx == number_of_ref_nodes - 1) {
      break;
    }
  }
}

void OsmWay::setUsedByRelation(bool used_by_relation) { used_by_relation_ = used_by_relation; }

void OsmWay::generateHighwayAllowedModeTypes(const absl::flat_hash_set<ModeType>& highway_mode_types) {
  if (highway_mode_types.find(ModeType::AUTO) != highway_mode_types.end()) {
    if (checkAllowedUsedAutoInMotor_Vehicle(motor_vehicle_) || checkAllowedUsedAutoInMotorCar(motorcar_) ||
        (!checkAllowedUsedAutoExHighway(highway_) && !checkAllowedUsedAutoExMotor_Vehicle(motor_vehicle_) &&
         !checkAllowedUsedAutoExMotorCar(motorcar_) && !checkAllowedUsedAutoExAccess(access_) &&
         !checkAllowedUsedAutoExService(service_))) {
      allowed_mode_types_.push_back(ModeType::AUTO);
    }
  }
  if (highway_mode_types.find(ModeType::BIKE) != highway_mode_types.end()) {
    if (checkAllowedUsedBikeInBicycle(bicycle_) ||
        (!checkAllowedUsedBikeExHighway(highway_) && !checkAllowedUsedBikeExBicycle(bicycle_) &&
         !checkAllowedUsedBikeExService(service_) && !checkAllowedUsedBikeExAccess(access_))) {
      allowed_mode_types_.push_back(ModeType::BIKE);
    }
  }
  if (highway_mode_types.find(ModeType::WALK) != highway_mode_types.end()) {
    if (checkAllowedUsedWalkInFoot(foot_) ||
        (!checkAllowedUsedWalkExHighway(highway_) && !checkAllowedUsedWalkExFoot(foot_) &&
         !checkAllowedUsedWalkExService(service_) && !checkAllowedUsedWalkExAccess(access_))) {
      allowed_mode_types_.push_back(ModeType::WALK);
    }
  }
}

void OsmWay::mapRefNodes(const absl::flat_hash_map<OsmIdType, OsmNode*>& osm_node_dict) {
  if (ref_node_id_vector_.empty()) {
    return;
  }
  const size_t number_of_ref_nodes = ref_node_id_vector_.size();
  ref_node_vector_.reserve(number_of_ref_nodes);
  for (const OsmIdType ref_node_id : ref_node_id_vector_) {
    auto iter = osm_node_dict.find(ref_node_id);
    if (iter == osm_node_dict.end()) {
      LOG(WARNING) << "unkown ref node " << ref_node_id << " in way " << osm_way_id_
                   << ", the way will not be imported";
      ref_node_vector_.clear();
      return;
    }
    ref_node_vector_.push_back(iter->second);
  }
  from_node_ = ref_node_vector_.at(0);
  to_node_ = ref_node_vector_.back();
}

const std::regex& getFloatNumMatchingPattern() {
  static const std::regex pattern(R"(\d+\.?\d*)");
  return pattern;
}

void OsmWay::configAttributes() {
  // lane info
  if (!lanes_raw_.empty()) {
    std::smatch match;
    if (std::regex_search(lanes_raw_, match, getFloatNumMatchingPattern())) {
      lanes_ = static_cast<int32_t>(std::round(std::stof(match.str())));
    }
  }
  if (!forward_lanes_raw_.empty()) {
    std::smatch match;
    if (std::regex_search(forward_lanes_raw_, match, getFloatNumMatchingPattern())) {
      forward_lanes_ = static_cast<int32_t>(std::round(std::stof(match.str())));
    }
  }
  if (!backward_lanes_raw_.empty()) {
    std::smatch match;
    if (std::regex_search(backward_lanes_raw_, match, getFloatNumMatchingPattern())) {
      backward_lanes_ = static_cast<int32_t>(std::round(std::stof(match.str())));
    }
  }

  // speed info
  if (!max_speed_raw_.empty()) {
    std::smatch match;
    if (std::regex_search(max_speed_raw_, match, getFloatNumMatchingPattern())) {
      max_speed_ = std::stof(match.str());
    }
  }

  // oneway info
  if (way_type_ == WayType::HIGHWAY) {
    if (!oneway_raw_.empty()) {
      if (oneway_raw_ == "yes" || oneway_raw_ == "1") {
        is_oneway_ = true;
      } else if (oneway_raw_ == "no" || oneway_raw_ == "0") {
        is_oneway_ = false;
      } else if (oneway_raw_ == "-1") {
        is_oneway_ = true;
        is_reversed_ = true;
      } else if (oneway_raw_ == "reversible" || oneway_raw_ == "alternating") {
        // todo: reversible, alternating: https://wiki.openstreetmap.org/wiki/Tag:oneway%3Dreversible
        is_oneway_ = false;
      } else {
        DLOG(WARNING) << "new oneway type detected at way " << osm_way_id_ << " " << oneway_raw_;
        if (junction_ == "circular" || junction_ == "roundabout") {
          is_oneway_ = true;
        }
      }
    }
    if (!is_oneway_.has_value()) {
      is_oneway_ = getDefaultOneWayFlag(highway_link_type_);
    }
  }
}

OsmRelation::OsmRelation(const osmium::Relation& relation)
    : osm_relation_id_(relation.id()),
      building_(getOSMTagValue(relation.tags(), "building")),
      amenity_(getOSMTagValue(relation.tags(), "amenity")),
      leisure_(getOSMTagValue(relation.tags(), "leisure")) {
  for (const osmium::RelationMember& member : relation.members()) {
    member_id_vector_.push_back(member.ref());
    member_type_vector_.push_back(member.type());
    member_role_vector_.emplace_back(member.role());
  }
}

void OsmRelation::initOsmRelation(const absl::flat_hash_map<OsmIdType, OsmWay*>& osm_way_dict) {
  if (member_id_vector_.empty()) {
    return;
  }
  const size_t number_of_members = member_id_vector_.size();
  member_way_vector_.reserve(number_of_members);
  for (size_t idx = 0; idx < number_of_members; ++idx) {
    if (member_type_vector_[idx] != osmium::item_type::way) {
      continue;
    }
    auto iter = osm_way_dict.find(member_id_vector_[idx]);
    if (iter == osm_way_dict.end()) {
      LOG(WARNING) << "unkown way member " << member_id_vector_[idx] << " in relation " << osm_relation_id_
                   << ", the relation will not be imported";
      member_way_vector_.clear();
      member_way_role_vector_.clear();
      return;
    }
    member_way_vector_.push_back(iter->second);
    member_way_role_vector_.push_back(member_role_vector_[idx]);
  }
  for (OsmWay* osm_way : member_way_vector_) {
    osm_way->setUsedByRelation(true);
  }
}

OsmIdType OsmRelation::osmRelationId() const { return osm_relation_id_; }
const std::string& OsmRelation::name() const { return name_; }
const std::vector<OsmWay*>& OsmRelation::memberWayVector() const { return member_way_vector_; }
const std::vector<std::string>& OsmRelation::memberWayRoleVector() const { return member_way_role_vector_; }
const std::string& OsmRelation::building() const { return building_; }
const std::string& OsmRelation::amenity() const { return amenity_; }
const std::string& OsmRelation::leisure() const { return leisure_; }

OsmNetwork::OsmNetwork(const std::filesystem::path& osm_filepath, absl::flat_hash_set<ModeType> mode_types,
                       absl::flat_hash_set<HighWayLinkType> link_types,
                       absl::flat_hash_set<HighWayLinkType> connector_link_types, bool POI, bool strict_boundary)
    : mode_types_(std::move(mode_types)),
      link_types_(std::move(link_types)),
      connector_link_types_(std::move(connector_link_types)),
      POI_(POI),
      strict_boundary_(strict_boundary) {
  if (!std::filesystem::exists(osm_filepath)) {
    LOG(FATAL) << "osm file " << osm_filepath << " does not exist";
    return;
  }

  factory_ = geos::geom::GeometryFactory::create();

  const auto time1 = std::chrono::high_resolution_clock::now();
  OsmHandler handler(mode_types_, link_types_, connector_link_types_, POI_);
  try {
    const osmium::io::File input_file{osm_filepath.string()};
    osmium::io::Reader reader{input_file};

    const osmium::Box& box = reader.header().box();
    if (reader.header().box().valid()) {
      boundary_ = factory_->createPolygon({geos::geom::Coordinate(box.bottom_left().lon(), box.bottom_left().lat()),
                                           geos::geom::Coordinate(box.top_right().lon(), box.bottom_left().lat()),
                                           geos::geom::Coordinate(box.top_right().lon(), box.top_right().lat()),
                                           geos::geom::Coordinate(box.bottom_left().lon(), box.top_right().lat()),
                                           geos::geom::Coordinate(box.bottom_left().lon(), box.bottom_left().lat())});
    } else {
      LOG(WARNING) << "no valid boundary information in the osm file";
      boundary_ =
          factory_->createPolygon({geos::geom::Coordinate(MIN_LON, MIN_LAT), geos::geom::Coordinate(MAX_LON, MIN_LAT),
                                   geos::geom::Coordinate(MAX_LON, MAX_LAT), geos::geom::Coordinate(MIN_LON, MAX_LAT),
                                   geos::geom::Coordinate(MIN_LON, MIN_LAT)});
    }

    osmium::apply(reader, handler);
    reader.close();
  } catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
  }
  const auto time2 = std::chrono::high_resolution_clock::now();
  DLOG(INFO) << "parse osm "
             << (std::chrono::duration_cast<std::chrono::microseconds>(time2 - time1) * MICROSECONDS_TO_SECOND).count()
             << "seconds";

  osm_node_vector_ = std::move(handler.osmNodeVector());
  osm_way_vector_ = std::move(handler.osmWayVector());
  osm_relation_vector_ = std::move(handler.osmRelationVector());
  LOG(INFO) << "nodes: " << osm_node_vector_.size() << " ways: " << osm_way_vector_.size()
            << " relations: " << osm_relation_vector_.size();
  for (OsmNode* osm_node : osm_node_vector_) {
    osm_node_dict_[osm_node->osmNodeId()] = osm_node;
  }
  for (OsmWay* osm_way : osm_way_vector_) {
    osm_way_dict_[osm_way->osmWayId()] = osm_way;
  }

  const auto time3 = std::chrono::high_resolution_clock::now();
  DLOG(INFO) << "pass osm "
             << (std::chrono::duration_cast<std::chrono::microseconds>(time3 - time2) * MICROSECONDS_TO_SECOND).count()
             << "seconds";

  processOsmData();

  const auto time4 = std::chrono::high_resolution_clock::now();
  DLOG(INFO) << "process osm "
             << (std::chrono::duration_cast<std::chrono::microseconds>(time4 - time3) * MICROSECONDS_TO_SECOND).count()
             << "seconds";
}

OsmNetwork::~OsmNetwork() {
  if (!osm_node_vector_.empty()) {
    const size_t number_of_osm_nodes = osm_node_vector_.size();
#pragma omp parallel for schedule(dynamic) default(none) shared(number_of_osm_nodes)
    for (int64_t idx = 0; idx < number_of_osm_nodes; ++idx) {
      delete osm_node_vector_[idx];
    }
  }
  if (!osm_way_vector_.empty()) {
    const size_t number_of_osm_ways = osm_way_vector_.size();
#pragma omp parallel for schedule(dynamic) default(none) shared(number_of_osm_ways)
    for (int64_t idx = 0; idx < number_of_osm_ways; ++idx) {
      delete osm_way_vector_[idx];
    }
  }
  if (!osm_relation_vector_.empty()) {
    const size_t number_of_osm_relations = osm_relation_vector_.size();
#pragma omp parallel for schedule(dynamic) default(none) shared(number_of_osm_relations)
    for (int64_t idx = 0; idx < number_of_osm_relations; ++idx) {
      delete osm_relation_vector_[idx];
    }
  }
}

const std::unique_ptr<geos::geom::Polygon>& OsmNetwork::boundary() const { return boundary_; }
const std::vector<OsmWay*>& OsmNetwork::osmWayVector() const { return osm_way_vector_; }
const std::vector<OsmRelation*>& OsmNetwork::osmRelationVector() const { return osm_relation_vector_; }

void OsmNetwork::processOsmData() {
  initializeElements();
  createWaySegments();
}

void OsmNetwork::initializeElements() {
  /*================= OsmNode =================*/
  const size_t number_of_osm_nodes = osm_node_vector_.size();
#pragma omp parallel for schedule(dynamic) default(none) shared(number_of_osm_nodes)
  for (int64_t idx = 0; idx < number_of_osm_nodes; ++idx) {
    osm_node_vector_[idx]->initOsmNode(factory_.get(), boundary_.get(), strict_boundary_);
  }

  /*================= OsmRelation =================*/
  const size_t number_of_osm_relations = osm_relation_vector_.size();
#pragma omp parallel for schedule(dynamic) default(none) shared(number_of_osm_relations)
  for (int64_t idx = 0; idx < number_of_osm_relations; ++idx) {
    osm_relation_vector_[idx]->initOsmRelation(osm_way_dict_);
  }

  /*================= OsmWay =================*/
  const size_t number_of_osm_ways = osm_way_vector_.size();
#pragma omp parallel for schedule(dynamic) default(none) shared(number_of_osm_ways)
  for (int64_t idx = 0; idx < number_of_osm_ways; ++idx) {
    osm_way_vector_[idx]->initOsmWay(osm_node_dict_);
  }
  osm_way_vector_.erase(remove_if(osm_way_vector_.begin(), osm_way_vector_.end(),
                                  [](OsmWay* osm_way) { return !osm_way->includeTheWay(); }),
                        osm_way_vector_.end());

  for (OsmWay* osm_way : osm_way_vector_) {
    if (osm_way->fromNode() != nullptr) {
      osm_way->fromNode()->addOutgoingWay(osm_way);
    }
    if (osm_way->toNode() != nullptr) {
      osm_way->toNode()->addIncomingWay(osm_way);
    }
  }
}

void OsmNetwork::createWaySegments() {
  // ToDo: run in parallel
  for (const OsmWay* osm_way : osm_way_vector_) {
    const std::vector<OsmNode*>& ref_node_vector = osm_way->refNodeVector();
    if (ref_node_vector.empty()) {
      continue;
    }
    for (OsmNode* ref_node : ref_node_vector) {
      ref_node->changeUsageCount();
    }
    ref_node_vector.at(0)->setIsEndingNode(true);
    ref_node_vector.back()->setIsEndingNode(true);
  }
  const size_t number_of_osm_nodes = osm_node_vector_.size();
#pragma omp parallel for schedule(dynamic) default(none) shared(number_of_osm_nodes)
  for (int64_t idx = 0; idx < number_of_osm_nodes; ++idx) {
    osm_node_vector_[idx]->setIsTypologyNode();
  }

  const size_t number_of_osm_ways = osm_way_vector_.size();
#pragma omp parallel for schedule(dynamic) default(none) shared(number_of_osm_ways)
  for (int64_t idx = 0; idx < number_of_osm_ways; ++idx) {
    osm_way_vector_[idx]->splitIntoSegments();
  }
}