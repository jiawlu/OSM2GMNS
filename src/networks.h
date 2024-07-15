//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_NETWORKS_H
#define OSM2GMNS_NETWORKS_H

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

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
  explicit Node(const OsmNode* osm_node);

  void setNodeId(NetIdType node_id);

  [[nodiscard]] NetIdType nodeId() const;

 private:
  const OsmNode* osm_node_;
  NetIdType node_id_{-1};
  std::string name_;
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

  void setLinkId(NetIdType link_id);

  [[nodiscard]] NetIdType linkId() const;
  [[nodiscard]] Node* fromNode() const;
  [[nodiscard]] Node* toNode() const;

 private:
  NetIdType link_id_{-1};
  //  unsigned long osm_way_id{};

  Node* from_node_{nullptr};
  Node* to_node_{nullptr};
  //  Geometry* geometry{};

  //  void buildFromOSMWay(Way* way, std::vector<OSMNode*>& /*ref_node_vector*/) {
  //    osm_way_id = way->getOsmWayId();
  //           from_node = ref_node_vector[0]->node;
  //           to_node = ref_node_vector[ref_node_vector.size()-1]->node;
  //    from_node->outgoing_link_vector.push_back(this);
  //    to_node->incoming_link_vector.push_back(this);
  //  }
};

class Network {
 public:
  explicit Network(OsmNetwork* osmnet);
  ~Network();
  Network(const Network&) = delete;
  Network& operator=(const Network&) = delete;
  Network(Network&&) = delete;
  Network& operator=(Network&&) = delete;

  [[nodiscard]] size_t numberOfNodes() const;
  [[nodiscard]] size_t numberOfLinks() const;
  [[nodiscard]] const std::vector<Node*>& nodeVector() const;
  [[nodiscard]] const std::vector<Link*>& linkVector() const;

 private:
  void createNodesAndLinksFromOsmNetwork();

  OsmNetwork* osmnet_;

  // absl::flat_hash_map<NetIdType, Node*> node_dict_;
  // absl::flat_hash_map<NetIdType, Link*> link_dict_;
  std::vector<Node*> node_vector_;
  std::vector<Link*> link_vector_;

  NetIdType max_node_id_{0};
  NetIdType max_link_id_{0};
};

#endif  // OSM2GMNS_NETWORKS_H
