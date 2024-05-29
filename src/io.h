//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_IO_H
#define OSM2GMNS_IO_H

#include <memory>
#include <string>

#include "networks.h"
#include "osmnetwork.h"

std::unique_ptr<OSMNetwork> readOSMFile(const std::string& filename, bool POI, bool strict_mode);

void outputNetToCSV(Network& network, const std::string& output_folder);

#endif  // OSM2GMNS_IO_H
