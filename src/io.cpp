//
// Created by Jiawei Lu on 2/16/23.
//

#include "io.h"

#include <absl/container/flat_hash_map.h>
#include <absl/log/log.h>
#include <geos/geom/Geometry.h>
#include <geos/io/WKTReader.h>

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <ios>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include "csv.h"
#include "networks.h"
#include "osmconfig.h"

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

std::string getModeTypeStr(const ModeType& mode_type) {
  static const absl::flat_hash_map<ModeType, std::string> mode_type_dict = {{ModeType::AUTO, "auto"},
                                                                            {ModeType::BIKE, "bike"},
                                                                            {ModeType::WALK, "walk"},
                                                                            {ModeType::RAILWAY, "railway"},
                                                                            {ModeType::AEROWAY, "aeroway"}};
  auto iter = mode_type_dict.find(mode_type);
  return iter != mode_type_dict.end() ? iter->second : "";
}

void outputNetToCSV(const Network* network, const std::filesystem::path& output_folder) {
  LOG(INFO) << "writing network to csv files";

  const std::filesystem::path node_filepath = output_folder / "node.csv";
  std::ofstream node_file(node_filepath);
  if (!node_file) {
    LOG(ERROR) << "Cannot open file " << node_filepath;
    return;
  }
  node_file << "name,node_id,osm_node_id,ctrl_type,x_coord,y_coord,boundary,zone_id,notes\n";
  for (const Node* node : network->nodeVector()) {
    const std::string ctrl_type = node->isSignalized() ? "signal" : "";
    const std::string zone_id = node->zoneId().has_value() ? std::to_string(node->zoneId().value()) : "";  // NOLINT
    const std::string boundary =
        node->boundary().has_value() ? std::to_string(node->boundary().value()) : "";  // NOLINT
    node_file << node->name() << "," << node->nodeId() << "," << node->osmNodeId() << "," << ctrl_type << ","
              << std::fixed << std::setprecision(COORDINATE_OUTPUT_PRECISION) << node->geometry()->getX() << ","
              << node->geometry()->getY() << std::defaultfloat << "," << boundary << "," << zone_id << ",\n";
  }
  node_file.close();

  const std::filesystem::path link_filepath = output_folder / "link.csv";
  std::ofstream link_file(link_filepath);
  if (!link_file) {
    std::cout << "Cannot open file " << link_filepath;
    return;
  }
  link_file << "link_id,name,osm_way_id,from_node_id,to_node_id,directed,geometry,dir_flag,length,facility_type,free_"
               "speed,free_speed_raw,lanes,capacity,allowed_uses,toll,notes\n";
  for (const Link* link : network->linkVector()) {
    const std::string lanes = link->lanes().has_value() ? std::to_string(link->lanes().value()) : "";  // NOLINT
    std::string free_speed;
    if (link->freeSpeed().has_value()) {
      std::ostringstream oss;
      oss << std::fixed << std::setprecision(0) << link->freeSpeed().value();  // NOLINT
      free_speed = oss.str();
    }
    const std::string capacity =
        link->capacity().has_value() ? std::to_string(link->capacity().value()) : "";  // NOLINT
    std::string allowed_uses = getModeTypeStr(link->allowedModeTypes().at(0));
    for (size_t idx = 1; idx < link->allowedModeTypes().size(); ++idx) {
      allowed_uses += ";" + getModeTypeStr(link->allowedModeTypes().at(idx));
    }
    link_file << link->linkId() << "," << link->name() << "," << link->osmWayId() << "," << link->fromNode()->nodeId()
              << "," << link->toNode()->nodeId() << ",1,\"" << link->geometry()->toString() << "\",1," << std::fixed
              << std::setprecision(LENGTH_OUTPUT_PRECISION) << link->length() << ","
              << getHighWayLinkTypeStr(link->highwayLinkType()) << "," << free_speed << "," << link->freeSpeedRaw()
              << "," << lanes << "," << capacity << "," << allowed_uses << "," << link->toll() << ",\n";
  }
  link_file.close();

  if (!network->poi()) {
    return;
  }
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

  LOG(INFO) << "write network done";
}

std::vector<Zone*> readZoneFile(const std::filesystem::path& zone_file) {
  if (!std::filesystem::exists(zone_file)) {
    LOG(ERROR) << "zone file " << zone_file << " does not exist";
    return {};
  }

  constexpr int16_t number_of_columns = 4;
  io::CSVReader<number_of_columns, io::trim_chars<' '>, io::double_quote_escape<',', '\"'>> in_file(
      zone_file.string().c_str());
  bool has_geometry_info = false;
  bool has_coord_info = false;
  in_file.read_header(io::ignore_missing_column, "zone_id", "x_coord", "y_coord", "geometry");
  if (in_file.has_column("geometry")) {
    has_geometry_info = true;
  }
  if (in_file.has_column("x_coord") && in_file.has_column("y_coord")) {
    has_coord_info = true;
  }
  if (!has_geometry_info && !has_coord_info) {
    LOG(ERROR) << "zone file should have either x_coord y_coord or geometry information. zone file will not be loaded";
    return {};
  }

  std::vector<Zone*> zone_vector;
  NetIdType zone_id = 0;
  double x_coord = 0.0;
  double y_coord = 0.0;
  std::string geometry_str;
  geos::geom::GeometryFactory::Ptr factory = geos::geom::GeometryFactory::create();
  const geos::io::WKTReader reader(factory.get());
  while (in_file.read_row(zone_id, x_coord, y_coord, geometry_str)) {
    std::unique_ptr<geos::geom::Geometry> geometry;
    if (has_geometry_info) {
      geometry = reader.read(geometry_str);
      if (geometry->getGeometryTypeId() != geos::geom::GEOS_POINT &&
          geometry->getGeometryTypeId() != geos::geom::GEOS_POLYGON &&
          geometry->getGeometryTypeId() != geos::geom::GEOS_MULTIPOLYGON) {
        LOG(WARNING) << "unsupported geometry type in the zone file. values in the geometry column should have a type "
                        "of POINT, POLYGON, or MULTIPOLYGON";
        continue;
      }
    } else if (has_coord_info) {
      geometry = factory->createPoint(geos::geom::Coordinate(x_coord, y_coord));
    }
    zone_vector.push_back(new Zone(zone_id, std::move(geometry)));
  }
  return zone_vector;
}

std::vector<Intersection*> readIntersectionFile(const std::filesystem::path& /*intersection_file*/) { return {}; }