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

    verboseLevel(true, VerboseLevel::Trace);

    const auto map_folder = std::filesystem::path("dev/maps/yuba");
    // const auto map_folder = std::filesystem::path("dev/maps/imperial");
    // const auto map_folder =
    //     std::filesystem::path("/Users/jlu486/GaTech Dropbox/Jiawei Lu/OSM_GMNS_GD_test/GMNS_test/1_Sioux Falls");
    // const auto map_folder =
    //     std::filesystem::path("/Users/jlu486/GaTech Dropbox/Jiawei Lu/Work/CAVLite/OSM2GMNS/maps/AZ");

    const std::string map_filename = "map.osm.pbf";
    // const std::string map_filename = "map.pbf";
    // const std::string map_filename = "arizona-latest.osm.pbf";

    Network* network = getNetFromFile(map_folder / map_filename, {ModeType::AUTO},
                                      {HighWayLinkType::MOTORWAY, HighWayLinkType::TRUNK, HighWayLinkType::PRIMARY,
                                       HighWayLinkType::SECONDARY, HighWayLinkType::TERTIARY},
                                      {HighWayLinkType::RESIDENTIAL}, true, 1.0, true);

    // Network* network = getNetFromFile(map_folder / map_filename, {}, {}, true, 1.0, true);

    consolidateComplexIntersections(network, true);

    generateNodeActivityInfo(network);

    fillLinkAttributesWithDefaultValues(network, true, {}, false, {{HighWayLinkType::MOTORWAY, 1}}, true,
                                        {{HighWayLinkType::MOTORWAY, 1}});

    outputNetToCSV(network, map_folder);

    delete network;
  } catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
  return 0;
}
