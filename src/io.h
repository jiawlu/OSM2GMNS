//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_IO_H
#define OSM2GMNS_IO_H

#include <filesystem>
#include <vector>

#include "networks.h"

void outputNetToCSV(const Network* network, const std::filesystem::path& output_folder);

std::vector<Zone*> readZoneFile(const std::filesystem::path& zone_file);

std::vector<Intersection*> readIntersectionFile(const std::filesystem::path& intersection_file);

#endif  // OSM2GMNS_IO_H
