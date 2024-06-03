//
// Created by Lu, Jiawei on 6/3/24.
//

#include "osmconfig.h"

#include <absl/container/flat_hash_map.h>

#include <iostream>
#include <set>
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
  std::cout << "  warning: new highway type " << highway_type_str << " is detected.\n";
  return HighWayLinkType::OTHER;
}

const std::set<std::string>& highwayPOISet() {
  static const std::set<std::string> highway_poi_set = {"bus_stop", "platform"};
  return highway_poi_set;
}
