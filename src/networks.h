//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_NETWORKS_H
#define OSM2GMNS_NETWORKS_H

#include <map>
#include <string>
#include <vector>

#include "geos/geom/Geometry.h"
#include "osmnetwork.h"

class Node;
class Link;

class Node {
 public:
  explicit Node(unsigned int node_id_) : node_id(node_id_) {}
  unsigned int node_id;
  std::string name{};
  unsigned long osm_node_id{};
  std::string osm_highway{};
  std::string ctrl_type{};
  Geometry* geometry{};
  double x{}, y{};
  std::string notes{};

  std::vector<Link*> outgoing_link_vector{}, incoming_link_vector{};

  void buildFromOSMNode(OSMNode* osmnode) {
    name = osmnode->name;
    osm_node_id = osmnode->osm_node_id;
    osm_highway = osmnode->osm_highway;
    ctrl_type = osmnode->ctrl_type;
    geometry = osmnode->geometry;
    x = osmnode->x;
    y = osmnode->y;
    //        self.geometry_xy = osmnode.geometry_xy
    notes = osmnode->notes;
  }
};

class Link {
 public:
  explicit Link(unsigned int link_id_) : link_id(link_id_) {}
  unsigned int link_id;
  unsigned long osm_way_id{};

  Node *from_node{}, *to_node{};
  Geometry* geometry{};

  void buildFromOSMWay(Way* way, std::vector<OSMNode*>& /*ref_node_vector*/) {
    osm_way_id = way->osm_way_id;
    //        from_node = ref_node_vector[0]->node;
    //        to_node = ref_node_vector[ref_node_vector.size()-1]->node;
    from_node->outgoing_link_vector.push_back(this);
    to_node->incoming_link_vector.push_back(this);
  }
};

class Network {
 public:
  Network() = default;

  std::map<unsigned int, Node*> node_dict{};
  std::map<unsigned int, Link*> link_dict{};

  unsigned int max_node_id{0};
  unsigned int max_link_id{0};
};

#endif  // OSM2GMNS_NETWORKS_H
