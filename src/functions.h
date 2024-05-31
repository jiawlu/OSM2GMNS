//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_FUNCTIONS_H
#define OSM2GMNS_FUNCTIONS_H

#include <memory>
#include <string>

#include "networks.h"

std::unique_ptr<Network> getNetFromFile(const std::string& filename, bool POI);

#endif  // OSM2GMNS_FUNCTIONS_H
