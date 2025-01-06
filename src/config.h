//
// Created by Jiawei Lu on 1/4/25.
//

#ifndef OSM2GMNS_CONFIG_H
#define OSM2GMNS_CONFIG_H

#include <vector>

struct OsmParsingConfig {
  std::vector<const char*> osm_node_attributes;
  std::vector<const char*> osm_link_attributes;
  std::vector<const char*> osm_poi_attributes;
};

#endif  // OSM2GMNS_CONFIG_H