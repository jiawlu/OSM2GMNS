//
// Created by Jiawei Lu on 2/17/23.
//

#include <exception>
#include <filesystem>
#include <iostream>
#include <string>

#include "functions.h"
#include "io.h"
#include "networks.h"
#include "osmconfig.h"
#include "utils.h"

int main(int /*argc*/, char* /*argv*/[]) {
  try {
    initializeAbslLogging();

    // const auto map_folder = std::filesystem::path("dev/maps/yuba");
    // const auto map_folder = std::filesystem::path("dev/maps/imperial");
    const auto map_folder =
        std::filesystem::path("/Users/jlu486/GaTech Dropbox/Jiawei Lu/Work/CAVLite/OSM2GMNS/maps/debug");
    // const std::string map_filename = "map.osm.pbf";
    const std::string map_filename = "toll.osm";

    Network* network = getNetFromFile(map_folder / map_filename,
                                      {HighWayLinkType::MOTORWAY, HighWayLinkType::TRUNK, HighWayLinkType::PRIMARY,
                                       HighWayLinkType::SECONDARY, HighWayLinkType::TERTIARY},
                                      {HighWayLinkType::RESIDENTIAL}, false);

    outputNetToCSV(network, map_folder);

    delete network;
  } catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
  return 0;
}
