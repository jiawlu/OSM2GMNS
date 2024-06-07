//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_FUNCTIONS_H
#define OSM2GMNS_FUNCTIONS_H

#include <filesystem>

#include "networks.h"

Network* getNetFromFile(const std::filesystem::path& osm_filepath, bool POI);

#endif  // OSM2GMNS_FUNCTIONS_H
