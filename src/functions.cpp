#include "functions.h"

#include <absl/log/log.h>

#include <filesystem>

#include "networks.h"
#include "osmnetwork.h"

// void processWays(OSMNetwork* osmnet) {
//   for (auto& [osm_way_id, way] : osmnet->osm_way_dict) {
//     if (way->ref_node_vector.size() < 2) continue;
//
//     way->ref_node_vector[0]->is_crossing = true;
//     way->ref_node_vector[way->ref_node_vector.size() - 1]->is_crossing = true;
//     for (OSMNode* osmnode : way->ref_node_vector) osmnode->usage_count++;
//
//     way->oneway = true;
//
//     osmnet->link_way_vector.push_back(way);
//   }
// }
//

//
// void createNodeFromOSMNode(Network* network, OSMNode* osmnode) {
//   if (!osmnode->node_assigned) {
//     Node* node = new Node(network->max_node_id);
//     node->buildFromOSMNode(osmnode);
//     //        osmnode->node = node;
//     osmnode->node_assigned = true;
//     network->node_dict[node->node_id] = node;
//     network->max_node_id++;
//   }
// }
//
// void createNodesAndLinks(OSMNetwork* osmnet, Network* network) {
//   for (Way* way : osmnet->link_way_vector) {
//     way->getNodeListForSegments();
//     for (int segment_no = 0; segment_no < way->number_of_segments; segment_no++) {
//       std::vector<std::vector<OSMNode*>> m_segment_node_list_group = {way->segment_node_vector[segment_no]};
//       for (std::vector<OSMNode*>& m_segment_node_vector : m_segment_node_list_group) {
//         if (m_segment_node_vector.size() < 2) continue;
//
//         createNodeFromOSMNode(network, m_segment_node_vector[0]);
//         createNodeFromOSMNode(network, m_segment_node_vector[m_segment_node_vector.size() - 1]);
//
//         Link* link = new Link(network->max_link_id++);
//         link->buildFromOSMWay(way, m_segment_node_vector);
//         network->link_dict[link->link_id] = link;
//       }
//     }
//   }
// }
//
// void creatNLPs(OSMNetwork* osmnet, Network* network, bool POI) {
//   processWays(osmnet);
//   identifyCrossingOSMNodes(osmnet);
//   createNodesAndLinks(osmnet, network);
// }
//

Network* buildNet(OsmNetwork* osmnet, bool /*POI*/) {
  auto* network = new Network(osmnet);
  //   creatNLPs(osmnet, network, POI);
  return network;
}

Network* getNetFromFile(const std::filesystem::path& osm_filepath, bool POI) {
  LOG(INFO) << "loading data from osm file";
  auto* osmnet = new OsmNetwork(osm_filepath, POI, true);

  LOG(INFO) << "building network";
  return buildNet(osmnet, POI);
};
