//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_FUNCTIONS_H
#define OSM2GMNS_FUNCTIONS_H

#include <filesystem>
#include <unordered_set>

#include "networks.h"
#include "osmconfig.h"

Network* getNetFromFile(const std::filesystem::path& osm_filepath, std::unordered_set<HighWayLinkType> link_types,
                        bool POI);

#endif  // OSM2GMNS_FUNCTIONS_H
