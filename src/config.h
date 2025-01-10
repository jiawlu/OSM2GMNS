//
// Created by Jiawei Lu on 1/4/25.
//

#ifndef OSM2GMNS_CONFIG_H
#define OSM2GMNS_CONFIG_H

#include <string>
#include <vector>

struct OsmParsingConfig {
  std::vector<std::string> osm_node_attributes;
  std::vector<std::string> osm_link_attributes;
  std::vector<std::string> osm_poi_attributes;
};

#endif  // OSM2GMNS_CONFIG_H