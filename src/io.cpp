//
// Created by Jiawei Lu on 2/16/23.
//

#include "io.h"

#include <absl/container/flat_hash_map.h>
#include <absl/container/flat_hash_set.h>
#include <absl/log/log.h>
#include <absl/strings/match.h>
#include <geos/geom/Geometry.h>
#include <geos/geom/Point.h>
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

constexpr int COORDINATE_OUTPUT_PRECISION = 7;
constexpr int LENGTH_OUTPUT_PRECISION = 2;
constexpr int AREA_OUTPUT_PRECISION = 1;

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

int32_t getHighWayLinkTypeNo(HighWayLinkType highway_link_type) {
  static const absl::flat_hash_map<HighWayLinkType, int32_t> link_type_no_map = {
      {HighWayLinkType::MOTORWAY, 1},      {HighWayLinkType::TRUNK, 2},    {HighWayLinkType::PRIMARY, 3},
      {HighWayLinkType::SECONDARY, 4},     {HighWayLinkType::TERTIARY, 5}, {HighWayLinkType::RESIDENTIAL, 6},
      {HighWayLinkType::LIVING_STREET, 7}, {HighWayLinkType::SERVICE, 8},  {HighWayLinkType::CYCLEWAY, 9},
      {HighWayLinkType::FOOTWAY, 10},      {HighWayLinkType::TRACK, 11},   {HighWayLinkType::UNCLASSIFIED, 20},
      {HighWayLinkType::OTHER, 21}};

  auto iter = link_type_no_map.find(highway_link_type);
  if (iter != link_type_no_map.end()) {
    return iter->second;
  }
  return -1;
}

int32_t getRailwayLinkTypeNo() {
  static const int32_t railway_link_type_no = 30;
  return railway_link_type_no;
}

int32_t getAerowayLinkTypeNo() {
  static const int32_t aeroway_link_type_no = 40;
  return aeroway_link_type_no;
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
  node_file << "name,node_id,osm_node_id,ctrl_type,x_coord,y_coord";
  for (const std::string& attr_name : network->osmParsingConfig()->osm_node_attributes) {
    node_file << "," << attr_name;
  }
  node_file << ",is_boundary,activity_type,poi_id,zone_id,notes\n";

  for (const Node* node : network->nodeVector()) {
    const std::string& name = absl::StrContains(node->name(), ',') ? "\"" + node->name() + "\"" : node->name();
    const std::string& ctrl_type = node->isSignalized() ? "signal" : "";
    const std::string& zone_id = node->zoneId().has_value() ? std::to_string(node->zoneId().value()) : "";  // NOLINT
    const std::string& boundary =
        node->boundary().has_value() ? std::to_string(node->boundary().value()) : "";  // NOLINT
    const std::string& activity_type =
        node->activityType().has_value() ? getHighWayLinkTypeStr(node->activityType().value()) : "";  // NOLINT
    node_file << name << "," << node->nodeId() << "," << node->osmNodeId() << "," << ctrl_type << "," << std::fixed
              << std::setprecision(COORDINATE_OUTPUT_PRECISION) << node->geometry()->getX() << ","
              << node->geometry()->getY() << std::defaultfloat;
    for (const std::string& attr_value : node->osmAttributes()) {
      node_file << "," << (absl::StrContains(attr_value, ',') ? "\"" + attr_value + "\"" : attr_value);
    }
    node_file << "," << boundary << "," << activity_type << ",," << zone_id << ",\n";
  }
  node_file.close();

  const std::filesystem::path link_filepath = output_folder / "link.csv";
  std::ofstream link_file(link_filepath);
  if (!link_file) {
    std::cout << "Cannot open file " << link_filepath;
    return;
  }
  link_file << "link_id,name,osm_way_id,from_node_id,to_node_id,directed,geometry,dir_flag,length,facility_type,link_"
               "type,free_speed,lanes,capacity,allowed_uses";
  for (const std::string& attr_name : network->osmParsingConfig()->osm_link_attributes) {
    link_file << "," << attr_name;
  }
  link_file << ",notes\n";
  for (const Link* link : network->linkVector()) {
    const std::string& name = absl::StrContains(link->name(), ',') ? "\"" + link->name() + "\"" : link->name();
    const std::string& facility_type =
        link->wayType() == WayType::HIGHWAY
            ? getHighWayLinkTypeStr(link->highwayLinkType())
            : (link->wayType() == WayType::RAILWAY
                   ? link->railwayLinkType()
                   : (link->wayType() == WayType::AEROWAY ? link->aerowayLinkType() : ""));
    const std::string& type_no =
        link->wayType() == WayType::HIGHWAY
            ? std::to_string(getHighWayLinkTypeNo(link->highwayLinkType()))
            : (link->wayType() == WayType::RAILWAY
                   ? std::to_string(getRailwayLinkTypeNo())
                   : (link->wayType() == WayType::AEROWAY ? std::to_string(getAerowayLinkTypeNo()) : ""));
    const std::string& lanes = link->lanes().has_value() ? std::to_string(link->lanes().value()) : "";  // NOLINT
    std::string free_speed;
    if (link->freeSpeed().has_value()) {
      std::ostringstream oss;
      oss << std::fixed << std::setprecision(0) << link->freeSpeed().value();  // NOLINT
      free_speed = oss.str();
    }
    const std::string& capacity =
        link->capacity().has_value() ? std::to_string(link->capacity().value()) : "";  // NOLINT
    std::string allowed_uses = getModeTypeStr(link->allowedModeTypes().at(0));
    for (size_t idx = 1; idx < link->allowedModeTypes().size(); ++idx) {
      allowed_uses += ";" + getModeTypeStr(link->allowedModeTypes().at(idx));
    }

    link_file << link->linkId() << "," << name << "," << link->osmWayId() << "," << link->fromNode()->nodeId() << ","
              << link->toNode()->nodeId() << ",1,\"" << link->geometry()->toString() << "\",1," << std::fixed
              << std::setprecision(LENGTH_OUTPUT_PRECISION) << link->length() << "," << facility_type << "," << type_no
              << "," << free_speed << "," << lanes << "," << capacity << "," << allowed_uses;
    for (const std::string& attr_value : link->osmAttributes()) {
      link_file << "," << (absl::StrContains(attr_value, ',') ? "\"" + attr_value + "\"" : attr_value);
    }
    link_file << ",\n";
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
  poi_file << "name,poi_id,osm_way_id,osm_relation_id,building,amenity,leisure,way,geometry,centroid,area,area_ft2";
  for (const std::string& attr_name : network->osmParsingConfig()->osm_poi_attributes) {
    poi_file << "," << attr_name;
  }
  poi_file << "\n";
  for (const POI* poi : network->poiVector()) {
    const std::string& name = absl::StrContains(poi->name(), ',') ? "\"" + poi->name() + "\"" : poi->name();
    const std::string osm_way_id =
        poi->osmWayId().has_value() ? std::to_string(poi->osmWayId().value()) : "";  // NOLINT
    const std::string osm_relation_id =
        poi->osmRelationId().has_value() ? std::to_string(poi->osmRelationId().value()) : "";  // NOLINT
    const std::string& building =
        absl::StrContains(poi->building(), ',') ? "\"" + poi->building() + "\"" : poi->building();
    const std::string& amenity = absl::StrContains(poi->amenity(), ',') ? "\"" + poi->amenity() + "\"" : poi->amenity();
    const std::string& leisure = absl::StrContains(poi->leisure(), ',') ? "\"" + poi->leisure() + "\"" : poi->leisure();
    poi_file << name << "," << poi->poiId() << "," << osm_way_id << "," << osm_relation_id << "," << building << ","
             << amenity << "," << leisure << ",,\"" << poi->geometry()->toString() << "\",\""
             << poi->centroidGeometry()->toString() << "\"," << std::fixed << std::setprecision(AREA_OUTPUT_PRECISION)
             << poi->area() << ",";
    for (const std::string& attr_value : poi->osmAttributes()) {
      poi_file << "," << (absl::StrContains(attr_value, ',') ? "\"" + attr_value + "\"" : attr_value);
    }
    poi_file << "\n";
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

std::vector<Intersection*> readIntersectionFile(const std::filesystem::path& intersection_file) {
  if (!std::filesystem::exists(intersection_file)) {
    LOG(ERROR) << "intersection file " << intersection_file << " does not exist";
    return {};
  }

  constexpr int16_t number_of_columns = 4;
  io::CSVReader<number_of_columns, io::trim_chars<' '>, io::double_quote_escape<',', '\"'>> in_file(
      intersection_file.string().c_str());
  in_file.read_header(io::ignore_extra_column, "intersection_id", "x_coord", "y_coord", "int_buffer");
  if (!(in_file.has_column("intersection_id") && in_file.has_column("x_coord") && in_file.has_column("y_coord") &&
        in_file.has_column("int_buffer"))) {
    LOG(ERROR)
        << "intersection file should have intersection_id, x_coord and y_coord columns. the file will be not loaded";
    return {};
  }

  std::vector<Intersection*> int_vector;
  NetIdType int_id = 0;
  double x_coord = 0.0;
  double y_coord = 0.0;
  float int_buffer = 0.0;
  geos::geom::GeometryFactory::Ptr factory = geos::geom::GeometryFactory::create();
  absl::flat_hash_set<NetIdType> loaded_int_ids;
  while (in_file.read_row(int_id, x_coord, y_coord, int_buffer)) {
    if (loaded_int_ids.contains(int_id)) {
      LOG(WARNING) << "intersection id " << int_id << " is duplicated in the intersection file";
      continue;
    }
    std::unique_ptr<geos::geom::Point> geometry = factory->createPoint(geos::geom::Coordinate(x_coord, y_coord));
    int_vector.push_back(int_buffer > 0 ? new Intersection(int_id, std::move(geometry), int_buffer)
                                        : new Intersection(int_id, std::move(geometry)));
    loaded_int_ids.insert(int_id);
  }
  LOG(INFO) << "intersection file loaded. " << int_vector.size() << " intersections";
  return int_vector;
}