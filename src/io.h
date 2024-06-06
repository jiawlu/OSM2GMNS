//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_IO_H
#define OSM2GMNS_IO_H

#include <string>

#include "networks.h"

void outputNetToCSV(const Network* network, const std::string& output_folder);

#endif  // OSM2GMNS_IO_H
