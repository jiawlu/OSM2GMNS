//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_FUNCTIONS_H
#define OSM2GMNS_FUNCTIONS_H

#include <string>

#include "networks.h"

Network* getNetFromFile(const std::string& filename, bool POI);

#endif  // OSM2GMNS_FUNCTIONS_H
