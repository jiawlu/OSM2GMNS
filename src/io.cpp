//
// Created by Jiawei Lu on 2/16/23.
//

#include "io.h"

#include <absl/log/log.h>

#include <filesystem>
#include <fstream>
#include <iostream>

#include "networks.h"

// static void geos_message_handler(const char* fmt, ...) {
//   va_list ap = nullptr;
//   va_start(ap, fmt);
//   vprintf(fmt, ap);
//   va_end(ap);
// }

// void getBounds(OsmNetwork* osmnet, const std::string& filename) {}
/*
void processNWR(OSMNetwork* osmnet, OsmHandler* handler) {

    // ==============  Node ================ //
    osmnet->osm_node_dict = handler->osm_node_dict;

    // ==============  Way ================ //
    for (auto &iter : handler->osm_way_dict)
    {
        bool valid = true;
        for (unsigned long ref_node_id: iter.second->ref_node_id_vector)
        {
            if (handler->osm_node_dict.find(ref_node_id) == handler->osm_node_dict.end())
            {
                valid = false;
                std::cout << "  warning: ref node " << ref_node_id << " in way " << iter.first << " is not defined, way
"
    << iter.first << "will be skipped\n"; break;
            }
            iter.second->ref_node_vector.push_back(handler->osm_node_dict[ref_node_id]);
        }

        if (valid)
            osmnet->osm_way_dict[iter.first] = iter.second;
    }

    // ==============  Relation ================ //

}
*/

void outputNetToCSV(const Network* network, const std::filesystem::path& output_folder) {
  LOG(INFO) << "writing network to csv files";

  const std::filesystem::path node_filepath = output_folder / "node.csv";
  std::ofstream node_file(node_filepath);
  if (!node_file) {
    LOG(ERROR) << "Cannot open file " << node_filepath;
    return;
  }
  node_file << "name,node_id,osm_node_id,ctrl_type,x_coord,y_coord,notes\n";
  for (const Node* node : network->nodeVector()) {
    node_file << "," << node->nodeId() << ",,,,,1\n";
  }
  node_file.close();

  const std::filesystem::path link_filepath = output_folder / "link.csv";
  std::ofstream link_file(link_filepath);
  if (!link_file) {
    std::cout << "Cannot open file " << link_filepath;
    return;
  }
  link_file << "link_id,osm_way_id,from_node_id,to_node_id,length,geometry\n";
  for (const Link* link : network->linkVector()) {
    link_file << link->linkId() << ",," << link->fromNode()->nodeId() << "," << link->toNode()->nodeId() << ",,1\n";
  }
  link_file.close();

  //  const std::string node_filepath = output_folder.empty() ? "node.csv" : output_folder + "/node.csv";
  //  std::ofstream node_file(node_filepath);
  //  if (!node_file) {
  //    std::cout << "\nError: Cannot open file " << node_filepath << '\n';
  //    exit(0);
  //  }
  //
  //  node_file << "name,node_id,osm_node_id,ctrl_type,x_coord,y_coord,notes\n";
  //
  //  for (auto& [node_id, node] : network->node_dict) {
  //    node_file << node->name << "," << node_id << "," << node->osm_node_id << "," << node->ctrl_type << ","
  //              << std::to_string(node->x) << "," << std::to_string(node->y) << "," << node->notes << "\n";
  //  }
  //  node_file.close();
  //
  //  const std::string link_filepath = output_folder.empty() ? "link.csv" : output_folder + "/link.csv";
  //  std::ofstream link_file(link_filepath);
  //  if (!link_file) {
  //    std::cout << "\nError: Cannot open file " << link_filepath << '\n';
  //    exit(0);
  //  }
  //
  //  link_file << "link_id,osm_way_id,from_node_id,to_node_id,length,geometry\n";
  //  std::string link_geo;
  //  for (auto& [link_id, link] : network->link_dict) {
  //    link_geo = "\"LINESTRING (" + std::to_string(link->from_node->x) + " " + std::to_string(link->from_node->y) + ",
  //    " +
  //               std::to_string(link->to_node->x) + " " + std::to_string(link->to_node->y) + ")\"";
  //
  //    link_file << link_id << "," << link->osm_way_id << "," << link->from_node->node_id << "," <<
  //    link->to_node->node_id
  //              << ",," << link_geo << "\n";
  //  }
  //  link_file.close();
}
