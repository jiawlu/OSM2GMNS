//
// Created by Jiawei Lu on 2/16/23.
//

#include "io.h"

#include <absl/container/flat_hash_map.h>
#include <absl/log/log.h>

#include <filesystem>
#include <fstream>
#include <iomanip>
#include <ios>
#include <iostream>
#include <sstream>
#include <string>

#include "networks.h"
#include "osmconfig.h"
#include "utils.h"

constexpr int COORDINATE_OUTPUT_PRECISION = 6;
constexpr int LENGTH_OUTPUT_PRECISION = 2;

std::string getHighWayLinkTypeStr(const HighWayLinkType& highway_link_type) {
  static const absl::flat_hash_map<HighWayLinkType, std::string> highway_link_type_dict = {
      {HighWayLinkType::MOTORWAY, "motorway"},
      {HighWayLinkType::TRUNK, "trunk"},
      {HighWayLinkType::PRIMARY, "primary"},
      {HighWayLinkType::SECONDARY, "secondary"},
      {HighWayLinkType::TERTIARY, "tertiary"},
      {HighWayLinkType::RESIDENTIAL, "residential"},
      {HighWayLinkType::LIVING_STREET, "living_street"},
      {HighWayLinkType::SERVICE, "service"},
      {HighWayLinkType::CYCLEWAY, "cycleway"},
      {HighWayLinkType::FOOTWAY, "footway"},
      {HighWayLinkType::TRACK, "track"},
      {HighWayLinkType::UNCLASSIFIED, "unclassified"},
      {HighWayLinkType::OTHER, "other"}};
  auto iter = highway_link_type_dict.find(highway_link_type);
  return iter != highway_link_type_dict.end() ? iter->second : "";
}
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
    node_file << node->name() << "," << node->nodeId() << "," << node->osmNodeId() << ",," << std::fixed
              << std::setprecision(COORDINATE_OUTPUT_PRECISION) << node->geometry()->getX() << ","
              << node->geometry()->getY() << std::defaultfloat << ",\n";
  }
  node_file.close();

  const std::filesystem::path link_filepath = output_folder / "link.csv";
  std::ofstream link_file(link_filepath);
  if (!link_file) {
    std::cout << "Cannot open file " << link_filepath;
    return;
  }
  link_file << "link_id,name,osm_way_id,from_node_id,to_node_id,directed,geometry,dir_flag,length,facility_type,free_"
               "speed,lanes,allowed_uses,toll,notes\n";
  for (const Link* link : network->linkVector()) {
    const std::string lanes = link->lanes().has_value() ? std::to_string(link->lanes().value()) : "";  // NOLINT
    std::string free_speed;
    if (link->freeSpeed().has_value()) {
      std::ostringstream oss;
      oss << std::fixed << std::setprecision(0) << link->freeSpeed().value();  // NOLINT
      free_speed = oss.str();
    }
    link_file << link->linkId() << "," << link->name() << "," << link->osmWayId() << "," << link->fromNode()->nodeId()
              << "," << link->toNode()->nodeId() << ",1,\"" << link->geometry()->toString() << "\",1," << std::fixed
              << std::setprecision(LENGTH_OUTPUT_PRECISION) << calculateLineStringLength(link->geometry().get()) << ","
              << getHighWayLinkTypeStr(link->highwayLinkType()) << "," << free_speed << "," << lanes << ",,"
              << link->toll() << ",\n";
  }
  link_file.close();

  const std::filesystem::path poi_filepath = output_folder / "poi.csv";
  std::ofstream poi_file(poi_filepath);
  if (!poi_file) {
    std::cout << "Cannot open file " << poi_filepath;
    return;
  }
  poi_file << "name,poi_id,osm_way_id,osm_relation_id,building,amenity,leisure,way,geometry,centroid,area,area_ft2\n";
  for (const POI* poi : network->poiVector()) {
    const std::string osm_way_id =
        poi->osmWayId().has_value() ? std::to_string(poi->osmWayId().value()) : "";  // NOLINT
    const std::string osm_relation_id =
        poi->osmRelationId().has_value() ? std::to_string(poi->osmRelationId().value()) : "";  // NOLINT
    poi_file << poi->name() << "," << poi->poiId() << "," << osm_way_id << "," << osm_relation_id << ","
             << poi->building() << "," << poi->amenity() << "," << poi->leisure() << ",,\""
             << poi->geometry()->toString() << "\",\"" << poi->centroidGeometry()->toString() << "\",,1\n";
  }
  poi_file.close();

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
