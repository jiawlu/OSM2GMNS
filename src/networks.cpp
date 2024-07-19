//
// Created by Jiawei Lu on 2/16/23.
//

#include "networks.h"

#include <absl/container/flat_hash_map.h>
#include <absl/container/flat_hash_set.h>
#include <geos/geom/CoordinateSequence.h>
#include <geos/geom/Geometry.h>
#include <geos/geom/GeometryFactory.h>
#include <geos/geom/MultiPolygon.h>
#include <geos/geom/Point.h>
#include <geos/geom/Polygon.h>
#include <omp.h>

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iterator>
#include <memory>
#include <numeric>
#include <optional>
#include <string>
#include <utility>
#include <vector>

#include "osmconfig.h"
#include "osmnetwork.h"
#include "utils.h"

Node::Node(const OsmNode* osm_node, const geos::geom::GeometryFactory* factory)
    : osm_node_(osm_node), name_(osm_node->name()), osm_node_id_(osm_node->osmNodeId()) {
  geometry_ = factory->createPoint(*(osm_node_->geometry()->getCoordinate()));
}

void Node::setNodeId(NetIdType node_id) { node_id_ = node_id; }
void Node::setZoneId(NetIdType zone_id) { zone_id_ = zone_id; }

NetIdType Node::nodeId() const { return node_id_; };
OsmIdType Node::osmNodeId() const { return osm_node_id_; }
const std::string& Node::name() const { return name_; }
const std::unique_ptr<geos::geom::Point>& Node::geometry() const { return geometry_; }

Link::Link(Node* from_node, Node* to_node) : from_node_(from_node), to_node_(to_node) {}
Link::Link(const OsmWay* osm_way, const std::vector<OsmNode*>& osm_nodes, bool forward_direction,
           const geos::geom::GeometryFactory* factory)
    : osm_way_id_(osm_way->osmWayId()),
      name_(osm_way->name()),
      free_speed_(osm_way->maxSpeed()),
      toll_(osm_way->toll()) {
  if (osm_nodes.size() < 2) {
    return;
  }
  from_osm_node_ = forward_direction ? osm_nodes.at(0) : osm_nodes.back();
  to_osm_node_ = forward_direction ? osm_nodes.back() : osm_nodes.at(0);
  geos::geom::CoordinateSequence coord_seq;
  if (forward_direction) {
    for (const OsmNode* osm_node : osm_nodes) {
      coord_seq.add(*(osm_node->geometry()->getCoordinate()));
    }
  } else {
    for (auto rit = osm_nodes.rbegin(); rit != osm_nodes.rend(); ++rit) {
      coord_seq.add(*((*rit)->geometry()->getCoordinate()));
    }
  }
  geometry_ = factory->createLineString(coord_seq);
  highway_link_type_ = osm_way->highwayLinkType();

  if (osm_way->isOneway()) {
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
const std::string& Link::name() const { return name_; }
OsmNode* Link::fromOsmNode() const { return from_osm_node_; }
OsmNode* Link::toOsmNode() const { return to_osm_node_; }
Node* Link::fromNode() const { return from_node_; }
Node* Link::toNode() const { return to_node_; }
HighWayLinkType Link::highwayLinkType() const { return highway_link_type_; }
const std::unique_ptr<geos::geom::LineString>& Link::geometry() const { return geometry_; }
std::optional<int32_t> Link::lanes() const { return lanes_; }
std::optional<float> Link::freeSpeed() const { return free_speed_; }
const std::string& Link::toll() const { return toll_; }

void Link::setLinkId(NetIdType link_id) { link_id_ = link_id; }
void Link::setFromNode(Node* from_node) { from_node_ = from_node; }
void Link::setToNode(Node* to_node) { to_node_ = to_node; }

POI::POI(const OsmWay* osm_way, std::unique_ptr<geos::geom::Polygon> geometry)
    : name_(osm_way->name()),
      osm_way_id_(osm_way->osmWayId()),
      building_(osm_way->building()),
      amenity_(osm_way->amenity()),
      leisure_(osm_way->leisure()),
      geometry_(std::move(geometry)),
      centroid_geometry_(std::move(geometry_->getCentroid())) {
  // poi.way = way.way_poi

  // lon, lat = poi.geometry.centroid.x, poi.geometry.centroid.y
  // poi.centroid =
  // geometry.Point((round(lon,og_settings.lonlat_coord_precision),round(lat,og_settings.lonlat_coord_precision))) x, y
  // = poi.geometry_xy.centroid.x, poi.geometry_xy.centroid.y poi.centroid_xy =
  // geometry.Point((round(x,og_settings.local_coord_precision),round(y,og_settings.local_coord_precision)))
  // POI_list1.append(poi)
}

POI::POI(const OsmRelation* osm_relation, std::unique_ptr<geos::geom::MultiPolygon> geometry)
    : name_(osm_relation->name()),
      osm_relation_id_(osm_relation->osmRelationId()),
      building_(osm_relation->building()),
      amenity_(osm_relation->amenity()),
      leisure_(osm_relation->leisure()),
      geometry_(std::move(geometry)),
      centroid_geometry_(std::move(geometry_->getCentroid())) {
  // poi.osm_relation_id = relation.osm_relation_id
  // poi.name = relation.name
  // poi.building = relation.building
  // poi.amenity = relation.amenity
  // poi.leisure = relation.leisure
  // polygon_list = []
  // polygon_list_xy = []
  // number_of_members = len(relation.member_list)
  // m_ref_node_list = []
}

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

Network::Network(OsmNetwork* osmnet, absl::flat_hash_set<HighWayLinkType> link_types,
                 absl::flat_hash_set<HighWayLinkType> connector_link_types, bool POI)
    : osmnet_(osmnet),
      link_types_(std::move(link_types)),
      connector_link_types_(std::move(connector_link_types)),
      POI_(POI) {
  factory_ = geos::geom::GeometryFactory::create();

  createNodesAndLinksFromOsmNetwork();
  createPOIsFromOsmNetwork();
}

Network::~Network() {
  delete osmnet_;
  for (Node* node : node_vector_) {
    delete node;
  }
  for (Link* link : link_vector_) {
    delete link;
  }
}

size_t Network::numberOfNodes() const { return node_vector_.size(); }
size_t Network::numberOfLinks() const { return link_vector_.size(); }
const std::vector<Node*>& Network::nodeVector() const { return node_vector_; }
const std::vector<Link*>& Network::linkVector() const { return link_vector_; }
const std::vector<POI*>& Network::poiVector() const { return poi_vector_; }

void Network::generateNodeActivityInfo(const std::vector<Zone*>& zone_vector) {
  for (Node* node : node_vector_) {
    if (zone_vector.empty()) {
      node->setZoneId(node->nodeId());
      continue;
    }
  }
}

void Network::createNodesAndLinksFromOsmNetwork() {
  const size_t num_threads = omp_get_max_threads();
  std::vector<std::vector<Link*>> m_link_vector{num_threads};

  const std::vector<OsmWay*>& osm_way_vector = osmnet_->osmWayVector();
  const size_t number_of_osm_ways = osm_way_vector.size();
#pragma omp parallel for schedule(dynamic) default(none) shared(osm_way_vector, number_of_osm_ways, m_link_vector)
  for (int64_t idx = 0; idx < number_of_osm_ways; ++idx) {
    OsmWay* osm_way = osm_way_vector[idx];
    if (osm_way->wayType() == WayType::HIGHWAY && osm_way->isTargetLinkType()) {
      createNodesAndLinksFromOneWay(osm_way, m_link_vector);
    }
  }
  const std::vector<OsmWay*> connector_ways = identifyConnectorWays();
  const size_t number_of_connector_ways = connector_ways.size();
#pragma omp parallel for schedule(dynamic) default(none) shared(connector_ways, number_of_connector_ways, m_link_vector)
  for (int64_t idx = 0; idx < number_of_connector_ways; ++idx) {
    OsmWay* osm_way = connector_ways[idx];
    createNodesAndLinksFromOneWay(osm_way, m_link_vector);
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
  }

  NetIdType node_id = 0;
  for (Node* node : node_vector_) {
    node->setNodeId(node_id++);
  }
  NetIdType link_id = 0;
  for (Link* link : link_vector_) {
    link->setLinkId(link_id++);
  }
}

void Network::createNodesAndLinksFromOneWay(const OsmWay* osm_way, std::vector<std::vector<Link*>>& m_link_vector) {
  for (const std::vector<OsmNode*>& segment_nodes : osm_way->segmentNodesVector()) {
    if (segment_nodes.size() < 2) {
      continue;
    }
    Link* link = new Link(osm_way, segment_nodes, true, factory_.get());
    m_link_vector[omp_get_thread_num()].push_back(link);
    if (!osm_way->isOneway()) {
      link = new Link(osm_way, segment_nodes, false, factory_.get());
      m_link_vector[omp_get_thread_num()].push_back(link);
    }
  }
}

bool checkNodeConnecting(const std::vector<OsmWay*>& connecting_osm_ways) {
  return std::any_of(connecting_osm_ways.begin(), connecting_osm_ways.end(), [](const OsmWay* osm_way) {
    return osm_way->wayType() == WayType::HIGHWAY && osm_way->isTargetLinkType();
  });
}

bool checkConnectorNode(OsmNode* osm_node) {
  return checkNodeConnecting(osm_node->incomingWayVector()) || checkNodeConnecting(osm_node->outgoingWayVector());
}

std::vector<OsmWay*> Network::identifyConnectorWays() const {
  std::vector<OsmWay*> connector_ways;
  if (connector_link_types_.empty()) {
    return connector_ways;
  }

  for (OsmWay* osm_way : osmnet_->osmWayVector()) {
    if (connector_link_types_.find(osm_way->highwayLinkType()) == connector_link_types_.end()) {
      continue;
    }
    if (osm_way->refNodeVector().empty()) {
      continue;
    }
    if (osm_way->wayType() != WayType::HIGHWAY) {
      continue;
    }
    if (osm_way->isTargetLinkType()) {
      continue;
    }
    if (checkConnectorNode(osm_way->fromNode()) || checkConnectorNode(osm_way->toNode())) {
      connector_ways.push_back(osm_way);
    }
  }
  return connector_ways;
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
#pragma omp parallel for schedule(dynamic) default(none) shared(osm_way_vector, number_of_osm_ways, m_poi_vector)
  for (int64_t idx = 0; idx < number_of_osm_ways; ++idx) {
    createPOIsFromOneOsmWay(osm_way_vector[idx], m_poi_vector);
  }
}

void Network::createPOIsFromOneOsmWay(const OsmWay* osm_way, std::vector<std::vector<POI*>>& m_poi_vector) {
  if (osm_way->wayType() != WayType::POI || osm_way->refNodeVector().size() < 3) {
    return;
  }
  std::unique_ptr<geos::geom::Polygon> geometry = getPolygonFromOsmNodes(osm_way->refNodeVector(), factory_.get());
  if (geometry == nullptr || geometry->disjoint(osmnet_->boundary().get())) {
    return;
  }
  m_poi_vector[omp_get_thread_num()].push_back(new POI(osm_way, std::move(geometry)));
}

void Network::createPOIsFromOsmRelations(std::vector<std::vector<POI*>>& m_poi_vector) {
  const std::vector<OsmRelation*>& osm_relation_vector = osmnet_->osmRelationVector();
  const size_t number_of_osm_relations = osm_relation_vector.size();
#pragma omp parallel for schedule(dynamic) default(none) \
    shared(osm_relation_vector, number_of_osm_relations, m_poi_vector)
  for (int64_t idx = 0; idx < number_of_osm_relations; ++idx) {
    createPOIsFromOneOsmRelation(osm_relation_vector[idx], m_poi_vector);
  }
}

void Network::createPOIsFromOneOsmRelation(const OsmRelation* osm_relation,
                                           std::vector<std::vector<POI*>>& m_poi_vector) {
  if (osm_relation->building().empty() && osm_relation->amenity().empty() && osm_relation->leisure().empty()) {
    return;
  }
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
  bool disjoint = true;
  for (const auto& polygon : polygon_vector) {
    if (!polygon->disjoint(osmnet_->boundary().get())) {
      disjoint = false;
      break;
    }
  }
  if (disjoint) {
    return;
  }
  std::unique_ptr<geos::geom::MultiPolygon> poi_geometry = factory_->createMultiPolygon(std::move(polygon_vector));
  m_poi_vector[omp_get_thread_num()].push_back(new POI(osm_relation, std::move(poi_geometry)));
}
