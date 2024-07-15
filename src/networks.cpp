//
// Created by Jiawei Lu on 2/16/23.
//

#include "networks.h"

#include <absl/container/flat_hash_map.h>
#include <absl/container/flat_hash_set.h>

#include <cstddef>
#include <cstdint>
#include <vector>

#include "osmconfig.h"
#include "osmnetwork.h"

Node::Node(const OsmNode* osm_node) : osm_node_(osm_node) {}

void Node::setNodeId(NetIdType node_id) { node_id_ = node_id; }

NetIdType Node::nodeId() const { return node_id_; };

Link::Link(Node* from_node, Node* to_node) : from_node_(from_node), to_node_(to_node) {}

void Link::setLinkId(NetIdType link_id) { link_id_ = link_id; }

NetIdType Link::linkId() const { return link_id_; }
Node* Link::fromNode() const { return from_node_; }
Node* Link::toNode() const { return to_node_; }

Network::Network(OsmNetwork* osmnet) : osmnet_(osmnet) { createNodesAndLinksFromOsmNetwork(); }

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
  // implementation here ensures node and link ids do not change between different runs
  const std::vector<OsmWay*>& osm_way_vector = osmnet_->osmWayVector();
  const size_t number_of_osm_ways = osm_way_vector.size();
  absl::flat_hash_map<OsmNode*, Node*> osm_node_to_node_dict;
  // #pragma omp parallel for schedule(dynamic) default(none) \
//     shared(osm_way_vector, number_of_osm_ways, osm_node_to_node_dict)
  for (int64_t idx = 0; idx < number_of_osm_ways; ++idx) {
    OsmWay* osm_way = osm_way_vector[idx];
    if (osm_way->wayType() != WayType::HIGHWAY) {
      continue;
    }
    for (const std::vector<OsmNode*>& segment_nodes : osm_way->segmentNodesVector()) {
      if (segment_nodes.size() < 2) {
        continue;
      }
      Node* from_node = nullptr;
      Node* to_node = nullptr;
      // #pragma omp critical
      {
        auto iter_from_node = osm_node_to_node_dict.find(segment_nodes.at(0));
        if (iter_from_node != osm_node_to_node_dict.end()) {
          from_node = iter_from_node->second;
        } else {
          from_node = new Node(segment_nodes.at(0));
          osm_node_to_node_dict[segment_nodes.at(0)] = from_node;
        }
        auto iter_to_node = osm_node_to_node_dict.find(segment_nodes.back());
        if (iter_to_node != osm_node_to_node_dict.end()) {
          to_node = iter_to_node->second;
        } else {
          to_node = new Node(segment_nodes.back());
          osm_node_to_node_dict[segment_nodes.back()] = to_node;
        }
      }
      Link* link = new Link(from_node, to_node);
      link_vector_.push_back(link);
    }
  }
  node_vector_.reserve(osm_node_to_node_dict.size());
  for (auto& [_, node] : osm_node_to_node_dict) {
    node_vector_.push_back(node);
  }

  NetIdType node_id = 0;
  NetIdType link_id = 0;
  for (Link* link : link_vector_) {
    link->setLinkId(link_id++);
    if (link->fromNode()->nodeId() < 0) {
      link->fromNode()->setNodeId(node_id++);
    }
    if (link->toNode()->nodeId() < 0) {
      link->toNode()->setNodeId(node_id++);
    }
  }
}