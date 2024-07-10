//
// Created by Lu, Jiawei on 6/3/24.
//

#include "osmconfig.h"

#include <absl/container/flat_hash_map.h>
#include <absl/container/flat_hash_set.h>

#include <string>

HighWayLinkType highwayStringToLinkType(const std::string& highway_type_str) {
  static const absl::flat_hash_map<std::string, HighWayLinkType> link_type_map = {
      {"motorway", HighWayLinkType::MOTORWAY},
      {"motorway_link", HighWayLinkType::MOTORWAY},
      {"trunk", HighWayLinkType::TRUNK},
      {"trunk_link", HighWayLinkType::TRUNK},
      {"primary", HighWayLinkType::PRIMARY},
      {"primary_link", HighWayLinkType::PRIMARY},
      {"secondary", HighWayLinkType::SECONDARY},
      {"secondary_link", HighWayLinkType::SECONDARY},
      {"tertiary", HighWayLinkType::TERTIARY},
      {"tertiary_link", HighWayLinkType::TERTIARY},
      {"residential", HighWayLinkType::RESIDENTIAL},
      {"residential_link", HighWayLinkType::RESIDENTIAL},
      {"living_street", HighWayLinkType::LIVING_STREET},
      {"service", HighWayLinkType::SERVICE},
      {"services", HighWayLinkType::SERVICE},
      {"cycleway", HighWayLinkType::CYCLEWAY},
      {"footway", HighWayLinkType::FOOTWAY},
      {"pedestrian", HighWayLinkType::FOOTWAY},
      {"steps", HighWayLinkType::FOOTWAY},
      {"track", HighWayLinkType::TRACK},
      {"unclassified", HighWayLinkType::UNCLASSIFIED}};

  auto iter = link_type_map.find(highway_type_str);
  if (iter != link_type_map.end()) {
    return iter->second;
  }
  return HighWayLinkType::OTHER;
}

bool isHighwayPoiType(const std::string& highway) {
  static const absl::flat_hash_set<std::string> highway_poi_set = {"bus_stop", "platform"};
  return highway_poi_set.find(highway) != highway_poi_set.end();
}
bool isRailwayPoiType(const std::string& railway) {
  static const absl::flat_hash_set<std::string> railway_poi_set = {"depot","station","workshop","halt","interlocking","junction","spur_junction","terminal","platform"};
  return railway_poi_set.find(railway) != railway_poi_set.end();
}
bool isAerowayPoiType(const std::string& aeroway) {
  static const absl::flat_hash_set<std::string> aeroway_poi_set = {};
  return aeroway_poi_set.find(aeroway) != aeroway_poi_set.end();
}

bool isNegligibleHighwayType(const std::string& highway) {
  static const absl::flat_hash_set<std::string> negligible_highway_type_set = {
      "path",    "construction", "proposed", "raceway",    "bridleway", "rest_area", "su",     "road",     "abandoned",
      "planned", "trailhead",    "stairs",   "dismantled", "disused",   "razed",     "access", "corridor", "stop"};
  return negligible_highway_type_set.find(highway) != negligible_highway_type_set.end();
}
bool isNegligibleRailwayType(const std::string& railway) {
  static const absl::flat_hash_set<std::string> negligible_railway_type_set = {"construction","abandoned","disused","proposed","planned","dismantled","razed","ventilation_shaft"};
  return negligible_railway_type_set.find(railway) != negligible_railway_type_set.end();
}
bool isNegligibleAerowayType(const std::string& aeroway) {
  static const absl::flat_hash_set<std::string> negligible_aeroway_type_set = {};
  return negligible_aeroway_type_set.find(aeroway) != negligible_aeroway_type_set.end();
}