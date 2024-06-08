//
// Created by Jiawei Lu on 2/16/23.
//

#include "networks.h"

#include <cstddef>

#include "osmnetwork.h"

Node::Node(NetIdType node_id) : node_id_(node_id) {}

Link::Link(NetIdType link_id) : link_id_(link_id) {}

Network::Network(OsmNetwork* osmnet) : osmnet_(osmnet) {}

Network::~Network() {
  delete osmnet_;
  for (auto& [_, node] : node_dict_) {
    delete node;
  }
  for (auto& [_, link] : link_dict_) {
    delete link;
  }
}

size_t Network::numberOfNodes() const { return node_dict_.size(); }
size_t Network::numberOfLinks() const { return link_dict_.size(); }