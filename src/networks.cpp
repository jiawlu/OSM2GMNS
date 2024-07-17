//
// Created by Jiawei Lu on 2/16/23.
//

#include "networks.h"

#include <absl/container/flat_hash_map.h>
#include <absl/container/flat_hash_set.h>
#include <geos/geom/CoordinateSequence.h>
#include <geos/geom/GeometryFactory.h>
#include <geos/geom/Point.h>
#include <omp.h>

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <iterator>
#include <memory>
#include <numeric>
#include <utility>
#include <vector>

#include "osmconfig.h"
#include "osmnetwork.h"

Node::Node(const OsmNode* osm_node, const geos::geom::GeometryFactory* factory) : osm_node_(osm_node) {
  geometry_ = factory->createPoint(*osm_node_->geometry()->getCoordinate());
}

void Node::setNodeId(NetIdType node_id) { node_id_ = node_id; }

NetIdType Node::nodeId() const { return node_id_; };
const std::unique_ptr<geos::geom::Point>& Node::geometry() const { return geometry_; }

Link::Link(Node* from_node, Node* to_node) : from_node_(from_node), to_node_(to_node) {}
Link::Link(const std::vector<OsmNode*>& osm_nodes, bool forward_direction, const geos::geom::GeometryFactory* factory) {
  if (osm_nodes.size() < 2) {
    return;
  }
  from_osm_node_ = forward_direction ? osm_nodes.at(0) : osm_nodes.back();
  to_osm_node_ = forward_direction ? osm_nodes.back() : osm_nodes.at(0);
  geos::geom::CoordinateSequence coord_seq;
  if (forward_direction) {
    for (const OsmNode* osm_node : osm_nodes) {
      coord_seq.add(*osm_node->geometry()->getCoordinate());
    }
  } else {
    for (auto rit = osm_nodes.rbegin(); rit != osm_nodes.rend(); ++rit) {
      coord_seq.add(*(*rit)->geometry()->getCoordinate());
    }
  }
  geometry_ = factory->createLineString(coord_seq);
}

NetIdType Link::linkId() const { return link_id_; }
OsmNode* Link::fromOsmNode() const { return from_osm_node_; }
OsmNode* Link::toOsmNode() const { return to_osm_node_; }
Node* Link::fromNode() const { return from_node_; }
Node* Link::toNode() const { return to_node_; }
const std::unique_ptr<geos::geom::LineString>& Link::geometry() const { return geometry_; }

void Link::setLinkId(NetIdType link_id) { link_id_ = link_id; }
void Link::setFromNode(Node* from_node) { from_node_ = from_node; }
void Link::setToNode(Node* to_node) { to_node_ = to_node; }

Network::Network(OsmNetwork* osmnet, absl::flat_hash_set<HighWayLinkType> link_types,
                 absl::flat_hash_set<HighWayLinkType> connector_link_types)
    : osmnet_(osmnet), link_types_(std::move(link_types)), connector_link_types_(std::move(connector_link_types)) {
  factory_ = geos::geom::GeometryFactory::create();

  createNodesAndLinksFromOsmNetwork();
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
    Link* link = new Link(segment_nodes, false, factory_.get());
    m_link_vector[omp_get_thread_num()].push_back(link);
    if (!osm_way->isOneway()) {
      link = new Link(segment_nodes, true, factory_.get());
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
