#include "functions.h"

#include <absl/container/flat_hash_set.h>
#include <absl/log/log.h>

#include <filesystem>
#include <vector>

#include "io.h"
#include "networks.h"
#include "osmconfig.h"
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

// Network* buildNet(OsmNetwork* osmnet, bool /*POI*/) {
//   auto* network = new Network(osmnet);
//   return network;
// }

Network* getNetFromFile(const std::filesystem::path& osm_filepath,
                        const absl::flat_hash_set<HighWayLinkType>& link_types,
                        const absl::flat_hash_set<HighWayLinkType>& connector_link_types, bool POI,
                        float POI_sampling_ratio, bool strict_boundary) {
  LOG(INFO) << "loading data from osm file";
  auto* osmnet = new OsmNetwork(osm_filepath, link_types, connector_link_types, POI, strict_boundary);

  LOG(INFO) << "building network";
  return new Network(osmnet, link_types, connector_link_types, POI, POI_sampling_ratio);
};

void consolidateComplexIntersections(Network* network, bool auto_identify,
                                     const std::filesystem::path& intersection_file, float int_buffer) {
  if (!intersection_file.empty() && !std::filesystem::exists(intersection_file)) {
    LOG(ERROR) << "intersection file " << intersection_file
               << " does not exist. consolidateComplexIntersections() skipped";
    return;
  }
  if (intersection_file.empty()) {
    network->consolidateComplexIntersections(auto_identify, {}, int_buffer);
  } else {
    const std::vector<Intersection*> intersection_vector = readIntersectionFile(intersection_file);
    network->consolidateComplexIntersections(auto_identify, intersection_vector, int_buffer);
  }
}

void generateNodeActivityInfo(Network* network, const std::filesystem::path& zone_file) {
  if (!zone_file.empty() && !std::filesystem::exists(zone_file)) {
    LOG(ERROR) << "zone file " << zone_file << " does not exist. generateNodeActivityInfo() skipped";
    return;
  }
  if (zone_file.empty()) {
    network->generateNodeActivityInfo();
  } else {
    const std::vector<Zone*> zone_vector = readZoneFile(zone_file);
    network->generateNodeActivityInfo(zone_vector);
  }
}
