//
// Created by Jiawei Lu on 2/16/23.
//

#include "networks.h"

#include <absl/container/flat_hash_map.h>
#include <absl/container/flat_hash_set.h>
#include <absl/log/log.h>
#include <geos/geom/Coordinate.h>
#include <geos/geom/CoordinateSequence.h>
#include <geos/geom/Geometry.h>
#include <geos/geom/GeometryFactory.h>
#include <geos/geom/MultiPolygon.h>
#include <geos/geom/Point.h>
#include <geos/geom/Polygon.h>
#include <omp.h>

#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iterator>
#include <limits>
#include <memory>
#include <numeric>
#include <optional>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#include "osmconfig.h"
#include "osmnetwork.h"
#include "utils.h"

Node::Node(const OsmNode* osm_node, const geos::geom::GeometryFactory* factory)
    : osm_nodes_({osm_node}), name_(osm_node->name()), is_signalized_(osm_node->isSignalized()) {
  geometry_ = factory->createPoint(geos::geom::Coordinate(osm_node->getX(), osm_node->getY()));
}

Node::Node(NetIdType node_id, const std::vector<Node*>& nodes, NetIdType intersection_id,
           const geos::geom::GeometryFactory* factory)
    : node_id_(node_id), intersection_id_(intersection_id) {
  if (nodes.empty()) {
    return;
  }

  double sum_x = 0.0;
  double sum_y = 0.0;
  for (Node* node : nodes) {
    osm_nodes_.insert(osm_nodes_.end(), node->osmNodes().begin(), node->osmNodes().end());
    if (node->isSignalized()) {
      is_signalized_ = true;
    }
    const geos::geom::CoordinateXY* coord = node->geometry()->getCoordinate();
    sum_x += coord->x;
    sum_y += coord->y;
  }
  const double avg_x = sum_x / static_cast<double>(osm_nodes_.size());
  const double avg_y = sum_y / static_cast<double>(osm_nodes_.size());
  geometry_ = factory->createPoint(geos::geom::Coordinate(avg_x, avg_y));
}

void Node::setNodeId(NetIdType node_id) { node_id_ = node_id; }
void Node::setZoneId(NetIdType zone_id) { zone_id_ = zone_id; }
void Node::setBoundary(int16_t boundary) { boundary_ = boundary; }
void Node::setActivityType(HighWayLinkType activity_type) { activity_type_ = activity_type; }
void Node::setIntersectionId(NetIdType intersection_id) { intersection_id_ = intersection_id; }
// void Node::setIsValid(bool is_valid) { is_valid_ = is_valid; }
void Node::addIncomingLink(Link* link) { incoming_link_vector_.push_back(link); }
void Node::addOutgoingLink(Link* link) { outgoing_link_vector_.push_back(link); }

NetIdType Node::nodeId() const { return node_id_; };
const std::vector<const OsmNode*>& Node::osmNodes() const { return osm_nodes_; }
std::string Node::osmNodeId() const {
  if (osm_nodes_.empty()) {
    return "";
  }
  std::string osm_node_id = std::to_string(osm_nodes_.at(0)->osmNodeId());
  for (size_t idx = 1; idx < osm_nodes_.size(); ++idx) {
    osm_node_id += ";" + std::to_string(osm_nodes_.at(idx)->osmNodeId());
  }
  return osm_node_id;
}
const std::string& Node::name() const { return name_; }
bool Node::isSignalized() const { return is_signalized_; }
const std::unique_ptr<geos::geom::Point>& Node::geometry() const { return geometry_; }
std::optional<NetIdType> Node::zoneId() const { return zone_id_; }
std::optional<int16_t> Node::boundary() const { return boundary_; }
std::optional<HighWayLinkType> Node::activityType() const { return activity_type_; }
std::optional<NetIdType> Node::intersectionId() const { return intersection_id_; }
// bool Node::isValid() const { return is_valid_; }
const std::vector<Link*>& Node::incomingLinkVector() const { return incoming_link_vector_; }
const std::vector<Link*>& Node::outgoingLinkVector() const { return outgoing_link_vector_; }

Link::Link(Node* from_node, Node* to_node) : from_node_(from_node), to_node_(to_node) {}
Link::Link(const OsmWay* osm_way, const std::vector<OsmNode*>& osm_nodes, bool forward_direction, size_t osm_way_seq_,
           const geos::geom::GeometryFactory* factory)
    : osm_way_id_(osm_way->osmWayId()),
      osm_way_seq_(osm_way_seq_),
      name_(osm_way->name()),
      free_speed_(osm_way->maxSpeed()),
      free_speed_raw_(osm_way->maxSpeedRaw()),
      allowed_mode_types_(osm_way->allowedModeTypes()),
      toll_(osm_way->toll()) {
  if (osm_nodes.size() < 2) {
    return;
  }
  from_osm_node_ = forward_direction ? osm_nodes.at(0) : osm_nodes.back();
  to_osm_node_ = forward_direction ? osm_nodes.back() : osm_nodes.at(0);
  geos::geom::CoordinateSequence coord_seq;
  if (forward_direction) {
    for (const OsmNode* osm_node : osm_nodes) {
      // coord_seq.add(*(osm_node->geometry()->getCoordinate()));
      coord_seq.add(osm_node->getX(), osm_node->getY());
    }
  } else {
    for (auto rit = osm_nodes.rbegin(); rit != osm_nodes.rend(); ++rit) {
      // coord_seq.add(*((*rit)->geometry()->getCoordinate()));
      coord_seq.add((*rit)->getX(), (*rit)->getY());
    }
  }
  geometry_ = factory->createLineString(coord_seq);
  length_ = calculateLineStringLength(geometry_.get());
  way_type_ = osm_way->wayType();
  if (way_type_ == WayType::HIGHWAY) {
    highway_link_type_ = osm_way->highwayLinkType();
  } else if (way_type_ == WayType::RAILWAY) {
    railway_link_type_ = osm_way->railway();
  } else if (way_type_ == WayType::AEROWAY) {
    aeroway_link_type_ = osm_way->aeroway();
  }

  if (osm_way->isOneway().value()) {  // NOLINT
    if (osm_way->lanes().has_value()) {
      lanes_ = osm_way->lanes().value();  // NOLINT
    }
  } else {
    if (forward_direction) {
      if (osm_way->forward_lanes().has_value()) {
        lanes_ = osm_way->forward_lanes().value();  // NOLINT
      } else if (osm_way->lanes().has_value()) {
        lanes_ = static_cast<int32_t>(std::floor(osm_way->lanes().value() / 2.0));  // NOLINT
      }
    } else {
      if (osm_way->backward_lanes().has_value()) {
        lanes_ = osm_way->backward_lanes().value();  // NOLINT
      } else if (osm_way->lanes().has_value()) {
        lanes_ = static_cast<int32_t>(std::floor(osm_way->lanes().value() / 2.0));  // NOLINT
      }
    }
  }
}

NetIdType Link::linkId() const { return link_id_; }
OsmIdType Link::osmWayId() const { return osm_way_id_; }
size_t Link::osmWaySeq() const { return osm_way_seq_; }
const std::string& Link::name() const { return name_; }
OsmNode* Link::fromOsmNode() const { return from_osm_node_; }
OsmNode* Link::toOsmNode() const { return to_osm_node_; }
Node* Link::fromNode() const { return from_node_; }
Node* Link::toNode() const { return to_node_; }
WayType Link::wayType() const { return way_type_; }
HighWayLinkType Link::highwayLinkType() const { return highway_link_type_; }
const std::string& Link::railwayLinkType() const { return railway_link_type_; }
const std::string& Link::aerowayLinkType() const { return aeroway_link_type_; }
const std::unique_ptr<geos::geom::LineString>& Link::geometry() const { return geometry_; }
double Link::length() const { return length_; }
// bool Link::isValid() const { return is_valid_; }
std::optional<int32_t> Link::lanes() const { return lanes_; }
std::optional<float> Link::freeSpeed() const { return free_speed_; }
std::string Link::freeSpeedRaw() const { return free_speed_raw_; }
std::optional<int32_t> Link::capacity() const { return capacity_; }
const std::vector<ModeType>& Link::allowedModeTypes() const { return allowed_mode_types_; }
const std::string& Link::toll() const { return toll_; }

void Link::setLinkId(NetIdType link_id) { link_id_ = link_id; }
void Link::setFromNode(Node* from_node) { from_node_ = from_node; }
void Link::setToNode(Node* to_node) { to_node_ = to_node; }
void Link::setLanes(int32_t lanes) { lanes_ = lanes; }
void Link::setFreeSpeed(float free_speed) { free_speed_ = free_speed; }
void Link::setCapacity(int32_t capacity) { capacity_ = capacity; }
// void Link::setIsValid(bool is_valid) { is_valid_ = is_valid; }

POI::POI(const OsmWay* osm_way, std::unique_ptr<geos::geom::Polygon> geometry)
    : name_(osm_way->name()),
      osm_way_id_(osm_way->osmWayId()),
      building_(osm_way->building()),
      amenity_(osm_way->amenity()),
      leisure_(osm_way->leisure()),
      geometry_(std::move(geometry)),
      centroid_geometry_(std::move(geometry_->getCentroid())) {}

POI::POI(const OsmRelation* osm_relation, std::unique_ptr<geos::geom::MultiPolygon> geometry)
    : name_(osm_relation->name()),
      osm_relation_id_(osm_relation->osmRelationId()),
      building_(osm_relation->building()),
      amenity_(osm_relation->amenity()),
      leisure_(osm_relation->leisure()),
      geometry_(std::move(geometry)),
      centroid_geometry_(std::move(geometry_->getCentroid())) {}

NetIdType POI::poiId() const { return poi_id_; }
const std::string& POI::name() const { return name_; }
std::optional<OsmIdType> POI::osmWayId() const { return osm_way_id_; }
std::optional<OsmIdType> POI::osmRelationId() const { return osm_relation_id_; }
const std::string& POI::building() const { return building_; }
const std::string& POI::amenity() const { return amenity_; }
const std::string& POI::leisure() const { return leisure_; }
const std::unique_ptr<geos::geom::Geometry>& POI::geometry() const { return geometry_; }
const std::unique_ptr<geos::geom::Point>& POI::centroidGeometry() const { return centroid_geometry_; }

void POI::setPOIId(NetIdType poi_id) { poi_id_ = poi_id; }

Zone::Zone(NetIdType zone_id, std::unique_ptr<geos::geom::Geometry> geometry)
    : zone_id_(zone_id), geometry_(std::move(geometry)) {}

NetIdType Zone::zoneId() const { return zone_id_; }
const std::unique_ptr<geos::geom::Geometry>& Zone::geometry() const { return geometry_; }

Intersection::Intersection() = default;

Network::Network(OsmNetwork* osmnet, absl::flat_hash_set<HighWayLinkType> link_types,
                 absl::flat_hash_set<HighWayLinkType> connector_link_types, bool POI, float POI_sampling_ratio)
    : osmnet_(osmnet),
      link_types_(std::move(link_types)),
      connector_link_types_(std::move(connector_link_types)),
      POI_(POI),
      POI_sampling_ratio_(POI_sampling_ratio) {
  factory_ = geos::geom::GeometryFactory::create();
  if (osmnet_->boundary().has_value()) {
    boundary_ = static_cast<std::unique_ptr<geos::geom::Polygon>>(osmnet_->boundary().value()->clone());  // NOLINT
  }
  createNodesAndLinksFromOsmNetwork();
  createPOIsFromOsmNetwork();
}

Network::~Network() {
  LOG(INFO) << "releasing network memory";
  delete osmnet_;
  if (!node_vector_.empty()) {
    const size_t number_of_nodes = node_vector_.size();
#pragma omp parallel for schedule(dynamic) default(none) shared(number_of_nodes)
    for (int64_t idx = 0; idx < number_of_nodes; ++idx) {
      delete node_vector_[idx];
    }
  }
  if (!link_vector_.empty()) {
    const size_t number_of_links = link_vector_.size();
#pragma omp parallel for schedule(dynamic) default(none) shared(number_of_links)
    for (int64_t idx = 0; idx < number_of_links; ++idx) {
      delete link_vector_[idx];
    }
  }
  if (!poi_vector_.empty()) {
    const size_t number_of_pois = poi_vector_.size();
#pragma omp parallel for schedule(dynamic) default(none) shared(number_of_pois)
    for (int64_t idx = 0; idx < number_of_pois; ++idx) {
      delete poi_vector_[idx];
    }
  }
  LOG(INFO) << "network memory released";
}

bool Network::poi() const { return POI_; }
size_t Network::numberOfNodes() const { return node_vector_.size(); }
size_t Network::numberOfLinks() const { return link_vector_.size(); }
const std::vector<Node*>& Network::nodeVector() const { return node_vector_; }
const std::vector<Link*>& Network::linkVector() const { return link_vector_; }
const std::vector<POI*>& Network::poiVector() const { return poi_vector_; }

void Network::generateNodeActivityInfo(const std::vector<Zone*>& zone_vector) {
  // ========== Acitvity_info ========== //
  std::map<HighWayLinkType, int> count_map;
  for (Node* node : node_vector_) {
    for (int idx = 0; idx <= static_cast<int>(HighWayLinkType::OTHER); ++idx) {
      count_map[static_cast<HighWayLinkType>(idx)] = 0;
    }
    for (Link* link : node->outgoingLinkVector()) {
      if (link->wayType() == WayType::HIGHWAY) {
        ++count_map.at(link->highwayLinkType());  // ToDo: check way_type
      }
    }
    for (Link* link : node->incomingLinkVector()) {
      if (link->wayType() == WayType::HIGHWAY) {
        ++count_map.at(link->highwayLinkType());  // ToDo: check way_type
      }
    }

    auto max_element = std::max_element(count_map.begin(), count_map.end(), [](const auto& pair1, const auto& pair2) {
      return pair1.second < pair2.second;
    });
    if (max_element->second > 0) {
      node->setActivityType(max_element->first);
    }
  }

  // ========== Boundary ========== //
  for (Node* node : node_vector_) {
    if (node->outgoingLinkVector().empty() && !node->incomingLinkVector().empty()) {
      node->setBoundary(-1);
    } else if (node->incomingLinkVector().empty() && !node->outgoingLinkVector().empty()) {
      node->setBoundary(1);
    } else if (node->incomingLinkVector().size() == 1 && node->outgoingLinkVector().size() == 1 &&
               node->incomingLinkVector().at(0)->fromNode() == node->outgoingLinkVector().at(0)->toNode()) {
      node->setBoundary(2);
    } else {
      node->setBoundary(0);
    }
  }

  // ========== Zone_id ========== //
  absl::flat_hash_map<geos::geom::Geometry*, NetIdType> point_zone_dict;
  absl::flat_hash_map<geos::geom::Geometry*, NetIdType> polygon_zone_dict;
  for (const Zone* zone : zone_vector) {
    if (zone->geometry()->getGeometryTypeId() == geos::geom::GEOS_POINT) {
      point_zone_dict[zone->geometry().get()] = zone->zoneId();
    } else if (zone->geometry()->getGeometryTypeId() == geos::geom::GEOS_POLYGON ||
               zone->geometry()->getGeometryTypeId() == geos::geom::GEOS_MULTIPOLYGON) {
      polygon_zone_dict[zone->geometry().get()] = zone->zoneId();
    } else {
      LOG(WARNING) << "unsupported geometry type";
    }
  }

  for (Node* node : node_vector_) {
    if (node->boundary() == 0) {
      continue;
    }
    if (zone_vector.empty()) {
      node->setZoneId(node->nodeId());
      continue;
    }
    bool polygon_zone_found = false;
    for (const auto& [polygon_geometry, zone_id] : polygon_zone_dict) {
      if (polygon_geometry->covers(node->geometry().get())) {
        polygon_zone_found = true;
        node->setZoneId(zone_id);
        break;
      }
    }
    if (polygon_zone_found) {
      continue;
    }
    double min_distance = std::numeric_limits<double>::max();
    std::optional<NetIdType> nearest_zone_id;
    for (const auto& [point_geometry, zone_id] : point_zone_dict) {
      const double distance = point_geometry->distance(node->geometry().get());
      if (distance < min_distance) {
        min_distance = distance;
        nearest_zone_id = zone_id;
      }
    }
    if (nearest_zone_id.has_value()) {
      node->setZoneId(nearest_zone_id.value());
    }
  }
  LOG(INFO) << "Node activity info generated";
}

void Network::fillLinkAttributesWithDefaultValues(
    const absl::flat_hash_map<HighWayLinkType, int32_t>& default_lanes_dict,
    const absl::flat_hash_map<HighWayLinkType, float>& default_speed_dict,
    const absl::flat_hash_map<HighWayLinkType, int32_t>& default_capacity_dict) {
  const size_t number_of_links = link_vector_.size();
#pragma omp parallel for schedule(dynamic) default(none) \
    shared(number_of_links, default_lanes_dict, default_speed_dict, default_capacity_dict)
  for (int64_t idx = 0; idx < number_of_links; ++idx) {
    Link* link = link_vector_[idx];
    if (link->wayType() != WayType::HIGHWAY) {
      continue;
    }
    const HighWayLinkType link_type = link->highwayLinkType();
    if (!default_lanes_dict.empty()) {
      if (!link->lanes().has_value()) {
        link->setLanes(default_lanes_dict.at(link_type));
      }
    }
    if (!default_speed_dict.empty()) {
      if (!link->freeSpeed().has_value()) {
        link->setFreeSpeed(default_speed_dict.at(link_type));
      }
    }
    if (!default_capacity_dict.empty()) {
      if (!link->capacity().has_value()) {
        const int32_t lanes = link->lanes().has_value() ? link->lanes().value()  // NOLINT
                                                        : getPresetDefaultLanesDict().at(link_type);
        link->setCapacity(lanes * default_capacity_dict.at(link_type));
      }
    }
  }
}

void Network::consolidateComplexIntersections(bool auto_identify, const std::vector<Intersection*>& intersection_vector,
                                              float int_buffer) {
  if (!intersection_vector.empty()) {
    // _designateComplexIntersectionsFromIntFile(network, intersection_file, int_buffer)
  }
  if (auto_identify) {
    identifyComplexIntersections(int_buffer);
  }

  absl::flat_hash_map<NetIdType, std::vector<Node*>> node_group_dict;
  for (Node* node : node_vector_) {
    if (!node->intersectionId().has_value()) {
      continue;
    }
    auto iter = node_group_dict.find(node->intersectionId().value());  // NOLINT
    if (iter != node_group_dict.end()) {
      iter->second.push_back(node);
    } else {
      node_group_dict[node->intersectionId().value()] = {node};  // NOLINT
    }
  }

  size_t number_of_intersections_consolidated = 0;
  absl::flat_hash_set<Node*> nodes_to_remove;
  absl::flat_hash_set<Link*> links_to_remove;
  for (auto& [intersection_id, node_group] : node_group_dict) {
    if (node_group.size() < 2) {
      continue;
    }
    Node* new_node = new Node(max_node_id_++, node_group, intersection_id, factory_.get());
    for (Node* node : node_group) {
      nodes_to_remove.insert(node);
      // node->setIsValid(false);
      for (Link* link : node->incomingLinkVector()) {
        if (std::find(node_group.begin(), node_group.end(), link->fromNode()) != node_group.end()) {
          links_to_remove.insert(link);
          // link->setIsValid(false);
        } else {
          link->setToNode(new_node);
          new_node->addIncomingLink(link);
        }
      }
      for (Link* link : node->outgoingLinkVector()) {
        if (std::find(node_group.begin(), node_group.end(), link->toNode()) != node_group.end()) {
          links_to_remove.insert(link);
          // link->setIsValid(false);
        } else {
          link->setFromNode(new_node);
          new_node->addOutgoingLink(link);
        }
      }
    }
    node_vector_.push_back(new_node);
    ++number_of_intersections_consolidated;
  }
  LOG(INFO) << number_of_intersections_consolidated << " intersections consolidated";

  for (Node* node : nodes_to_remove) {
    delete node;
  }
  for (Link* link : links_to_remove) {
    delete link;
  }
  node_vector_.erase(
      remove_if(node_vector_.begin(), node_vector_.end(),
                [nodes_to_remove](Node* node) { return nodes_to_remove.find(node) != nodes_to_remove.end(); }),
      node_vector_.end());
  link_vector_.erase(
      remove_if(link_vector_.begin(), link_vector_.end(),
                [links_to_remove](Link* link) { return links_to_remove.find(link) != links_to_remove.end(); }),
      link_vector_.end());
}

void Network::createNodesAndLinksFromOsmNetwork() {
  const size_t num_threads = omp_get_max_threads();
  std::vector<std::vector<Link*>> m_link_vector{num_threads};

  const std::vector<OsmWay*>& osm_way_vector = osmnet_->osmWayVector();
  const size_t number_of_osm_ways = osm_way_vector.size();
#pragma omp parallel for schedule(dynamic) default(none) shared(osm_way_vector, number_of_osm_ways, m_link_vector)
  for (int64_t idx = 0; idx < number_of_osm_ways; ++idx) {
    OsmWay* osm_way = osm_way_vector[idx];
    if (osm_way->wayType() == WayType::HIGHWAY) {
      if (osm_way->isTargetLinkType() || osm_way->isTargetConnector()) {
        createLinksFromWay(osm_way, m_link_vector);
      }
    } else if (osm_way->wayType() == WayType::RAILWAY || osm_way->wayType() == WayType::AEROWAY) {
      createLinksFromWay(osm_way, m_link_vector);
    }
  }
  const size_t total_links =
      std::accumulate(m_link_vector.begin(), m_link_vector.end(), 0,
                      [](size_t sum, const std::vector<Link*>& vec) { return sum + vec.size(); });
  link_vector_.reserve(total_links);
  for (auto& links : m_link_vector) {
    link_vector_.insert(link_vector_.end(), std::make_move_iterator(links.begin()),
                        std::make_move_iterator(links.end()));
    links.clear();
  }

  // We need sort here to ensure a fixed link sequence in the link_vector_
  std::sort(link_vector_.begin(), link_vector_.end(), [](const Link* link_a, const Link* link_b) {
    if (link_a->osmWayId() != link_b->osmWayId()) {
      return link_a->osmWayId() < link_b->osmWayId();
    }
    return link_a->osmWaySeq() < link_b->osmWaySeq();
  });

  absl::flat_hash_map<OsmNode*, Node*> osm_node_to_node_dict;
  for (Link* link : link_vector_) {
    Node* from_node = nullptr;
    auto iter_from = osm_node_to_node_dict.find(link->fromOsmNode());
    if (iter_from == osm_node_to_node_dict.end()) {
      from_node = new Node(link->fromOsmNode(), factory_.get());
      node_vector_.push_back(from_node);
      osm_node_to_node_dict[link->fromOsmNode()] = from_node;
    } else {
      from_node = iter_from->second;
    }
    link->setFromNode(from_node);
    from_node->addOutgoingLink(link);

    Node* to_node = nullptr;
    auto iter_to = osm_node_to_node_dict.find(link->toOsmNode());
    if (iter_to == osm_node_to_node_dict.end()) {
      to_node = new Node(link->toOsmNode(), factory_.get());
      node_vector_.push_back(to_node);
      osm_node_to_node_dict[link->toOsmNode()] = to_node;
    } else {
      to_node = iter_to->second;
    }
    link->setToNode(to_node);
    to_node->addIncomingLink(link);
  }

  for (Node* node : node_vector_) {
    node->setNodeId(max_node_id_++);
  }
  for (Link* link : link_vector_) {
    link->setLinkId(max_link_id_++);
  }
}

void Network::createLinksFromWay(const OsmWay* osm_way, std::vector<std::vector<Link*>>& m_link_vector) {
  for (const std::vector<OsmNode*>& segment_nodes : osm_way->segmentNodesVector()) {
    if (segment_nodes.size() < 2) {
      continue;
    }
    assert(osm_way->isOneway().has_value());
    size_t osm_way_seq = 0;
    Link* link = new Link(osm_way, segment_nodes, true, osm_way_seq++, factory_.get());
    m_link_vector[omp_get_thread_num()].push_back(link);
    if (!osm_way->isOneway().value()) {  // NOLINT
      link = new Link(osm_way, segment_nodes, false, osm_way_seq++, factory_.get());
      m_link_vector[omp_get_thread_num()].push_back(link);
    }
  }
}

void Network::createPOIsFromOsmNetwork() {
  if (!POI_) {
    return;
  }
  const size_t num_threads = omp_get_max_threads();
  std::vector<std::vector<POI*>> m_poi_vector{num_threads};
  createPOIsFromOsmWays(m_poi_vector);
  createPOIsFromOsmRelations(m_poi_vector);

  const size_t total_pois = std::accumulate(m_poi_vector.begin(), m_poi_vector.end(), 0,
                                            [](size_t sum, const std::vector<POI*>& vec) { return sum + vec.size(); });
  poi_vector_.reserve(total_pois);
  for (auto& pois : m_poi_vector) {
    poi_vector_.insert(poi_vector_.end(), std::make_move_iterator(pois.begin()), std::make_move_iterator(pois.end()));
    pois.clear();
  }

  NetIdType poi_id = 0;
  for (POI* poi : poi_vector_) {
    poi->setPOIId(poi_id++);
  }
}

void Network::createPOIsFromOsmWays(std::vector<std::vector<POI*>>& m_poi_vector) {
  const std::vector<OsmWay*>& osm_way_vector = osmnet_->osmWayVector();
  const size_t number_of_osm_ways = osm_way_vector.size();
  const int freq = std::max(static_cast<int>(std::round(1.0 / POI_sampling_ratio_)), 1);
#pragma omp parallel for schedule(dynamic) default(none) shared(osm_way_vector, number_of_osm_ways, freq, m_poi_vector)
  for (int64_t idx = 0; idx < number_of_osm_ways; ++idx) {
    if (idx % freq != 0) {
      continue;
    }
    createPOIsFromOneOsmWay(osm_way_vector[idx], m_poi_vector);
  }
}

std::unique_ptr<geos::geom::Polygon> getPolygonFromOsmNodes(const std::vector<OsmNode*>& osm_nodes,
                                                            const geos::geom::GeometryFactory* factory) {
  geos::geom::CoordinateSequence coord_seq;
  if (osm_nodes.size() < 3) {
    return nullptr;
  }
  for (const OsmNode* osm_node : osm_nodes) {
    // coord_seq.add(*(osm_node->geometry()->getCoordinate()));
    coord_seq.add(osm_node->getX(), osm_node->getY());
  }
  if (osm_nodes.at(0)->osmNodeId() != osm_nodes.back()->osmNodeId()) {
    // coord_seq.add(*(osm_nodes.at(0)->geometry()->getCoordinate()));
    coord_seq.add(osm_nodes.at(0)->getX(), osm_nodes.at(0)->getY());
  }
  return factory->createPolygon(std::move(coord_seq));
}

void Network::createPOIsFromOneOsmWay(const OsmWay* osm_way, std::vector<std::vector<POI*>>& m_poi_vector) {
  if (osm_way->wayType() != WayType::POI || osm_way->refNodeVector().size() < 3) {
    return;
  }
  std::unique_ptr<geos::geom::Polygon> geometry = getPolygonFromOsmNodes(osm_way->refNodeVector(), factory_.get());
  if (geometry == nullptr) {
    return;
  }
  if (boundary_.has_value() && geometry->disjoint(boundary_.value().get())) {  // NOLINT
    return;
  }
  m_poi_vector[omp_get_thread_num()].push_back(new POI(osm_way, std::move(geometry)));
}

void Network::createPOIsFromOsmRelations(std::vector<std::vector<POI*>>& m_poi_vector) {
  const std::vector<OsmRelation*>& osm_relation_vector = osmnet_->osmRelationVector();
  const size_t number_of_osm_relations = osm_relation_vector.size();
  const int freq = std::max(static_cast<int>(std::round(1.0 / POI_sampling_ratio_)), 1);
#pragma omp parallel for schedule(dynamic) default(none) \
    shared(osm_relation_vector, number_of_osm_relations, freq, m_poi_vector)
  for (int64_t idx = 0; idx < number_of_osm_relations; ++idx) {
    if (idx % freq != 0) {
      continue;
    }
    createPOIsFromOneOsmRelation(osm_relation_vector[idx], m_poi_vector);
  }
}

void Network::createPOIsFromOneOsmRelation(const OsmRelation* osm_relation,
                                           std::vector<std::vector<POI*>>& m_poi_vector) {
  const size_t number_of_way_members = osm_relation->memberWayVector().size();
  if (number_of_way_members < 1) {
    return;
  }

  std::vector<OsmNode*> partial_node_sequence;
  std::vector<std::unique_ptr<geos::geom::Polygon>> polygon_vector;
  for (size_t idx = 0; idx < number_of_way_members; ++idx) {
    if (osm_relation->memberWayRoleVector().at(idx) != "outer") {
      continue;
    }
    const OsmWay* member = osm_relation->memberWayVector().at(idx);
    if (member->refNodeVector().size() < 2) {
      continue;
    }
    if (partial_node_sequence.empty()) {
      if (member->refNodeVector().at(0)->osmNodeId() == member->refNodeVector().back()->osmNodeId()) {
        std::unique_ptr<geos::geom::Polygon> geometry = getPolygonFromOsmNodes(member->refNodeVector(), factory_.get());
        if (geometry != nullptr) {
          polygon_vector.push_back(std::move(geometry));
        }
      } else {
        partial_node_sequence.insert(partial_node_sequence.end(), member->refNodeVector().begin(),
                                     member->refNodeVector().end());
      }
    } else {
      std::vector<OsmNode*> m_node_sequence;
      m_node_sequence.reserve(partial_node_sequence.size() + member->refNodeVector().size());
      if (partial_node_sequence.back() == member->refNodeVector().at(0)) {
        m_node_sequence.insert(m_node_sequence.end(), partial_node_sequence.begin(), partial_node_sequence.end());
        m_node_sequence.insert(m_node_sequence.end(), member->refNodeVector().begin(), member->refNodeVector().end());
      } else if (partial_node_sequence.back() == member->refNodeVector().back()) {
        m_node_sequence.insert(m_node_sequence.end(), partial_node_sequence.begin(), partial_node_sequence.end());
        m_node_sequence.insert(m_node_sequence.end(), member->refNodeVector().rbegin(), member->refNodeVector().rend());
      } else if (partial_node_sequence.at(0) == member->refNodeVector().at(0)) {
        m_node_sequence.insert(m_node_sequence.end(), partial_node_sequence.rbegin(), partial_node_sequence.rend());
        m_node_sequence.insert(m_node_sequence.end(), member->refNodeVector().begin(), member->refNodeVector().end());
      } else if (partial_node_sequence.at(0) == member->refNodeVector().back()) {
        m_node_sequence.insert(m_node_sequence.end(), partial_node_sequence.rbegin(), partial_node_sequence.rend());
        m_node_sequence.insert(m_node_sequence.end(), member->refNodeVector().rbegin(), member->refNodeVector().rend());
      }
      if (m_node_sequence.empty()) {
        std::unique_ptr<geos::geom::Polygon> geometry = getPolygonFromOsmNodes(partial_node_sequence, factory_.get());
        if (geometry != nullptr) {
          polygon_vector.push_back(std::move(geometry));
        }
        if (member->refNodeVector().at(0)->osmNodeId() == member->refNodeVector().back()->osmNodeId()) {
          geometry = getPolygonFromOsmNodes(member->refNodeVector(), factory_.get());
          if (geometry != nullptr) {
            polygon_vector.push_back(std::move(geometry));
          }
          partial_node_sequence.clear();
        } else {
          partial_node_sequence.assign(member->refNodeVector().begin(), member->refNodeVector().end());
        }
      } else {
        if (m_node_sequence.at(0)->osmNodeId() == m_node_sequence.back()->osmNodeId()) {
          std::unique_ptr<geos::geom::Polygon> geometry = getPolygonFromOsmNodes(m_node_sequence, factory_.get());
          if (geometry != nullptr) {
            polygon_vector.push_back(std::move(geometry));
          }
          partial_node_sequence.clear();
        } else {
          partial_node_sequence.assign(m_node_sequence.begin(), m_node_sequence.end());
        }
      }
    }
  }

  if (!partial_node_sequence.empty()) {
    std::unique_ptr<geos::geom::Polygon> geometry = getPolygonFromOsmNodes(partial_node_sequence, factory_.get());
    if (geometry != nullptr) {
      polygon_vector.push_back(std::move(geometry));
    }
  }

  if (polygon_vector.empty()) {
    return;
  }
  if (boundary_.has_value()) {
    const geos::geom::Polygon* boundary = boundary_.value().get();  // NOLINT
    bool disjoint = true;
    for (const auto& polygon : polygon_vector) {
      if (!polygon->disjoint(boundary)) {
        disjoint = false;
        break;
      }
    }
    if (disjoint) {
      return;
    }
  }
  std::unique_ptr<geos::geom::MultiPolygon> poi_geometry = factory_->createMultiPolygon(std::move(polygon_vector));
  m_poi_vector[omp_get_thread_num()].push_back(new POI(osm_relation, std::move(poi_geometry)));
}

void Network::identifyComplexIntersections(float int_buffer) {
  std::vector<absl::flat_hash_set<Node*>> group_vector;
  for (Link* link : link_vector_) {
    if (link->length() > int_buffer) {
      continue;
    }
    if (link->fromNode()->intersectionId().has_value() || link->toNode()->intersectionId().has_value()) {
      continue;
    }
    if (!(link->fromNode()->isSignalized() && link->toNode()->isSignalized())) {
      continue;
    }
    group_vector.push_back({link->fromNode(), link->toNode()});
  }
  bool updated = false;
  while (true) {
    updated = false;
    for (size_t idx1 = 0; idx1 < group_vector.size(); ++idx1) {
      absl::flat_hash_set<Node*>& group1 = group_vector[idx1];
      if (group1.empty()) {
        continue;
      }
      for (size_t idx2 = idx1 + 1; idx2 < group_vector.size(); ++idx2) {
        absl::flat_hash_set<Node*>& group2 = group_vector[idx2];
        if (group2.empty()) {
          continue;
        }
        if (std::find_first_of(group1.begin(), group1.end(), group2.begin(), group2.end()) != group1.end()) {
          group1.merge(group2);
          group2.clear();
          updated = true;
        }
      }
    }
    if (!updated) {
      break;
    }
  }

  for (const absl::flat_hash_set<Node*>& group : group_vector) {
    if (group.empty()) {
      continue;
    }
    for (Node* node : group) {
      node->setIntersectionId(max_intersection_id_);
    }
    ++max_intersection_id_;
  }
}