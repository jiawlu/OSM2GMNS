//
// Created by Jiawei Lu on 2/17/23.
//

#include <absl/base/log_severity.h>
#include <absl/log/globals.h>
#include <absl/log/initialize.h>

#include <exception>
#include <filesystem>
#include <iostream>
#include <string>

#include "functions.h"
#include "io.h"
#include "networks.h"
#include "osmconfig.h"

int main(int /*argc*/, char* /*argv*/[]) {
  try {
    absl::InitializeLog();
    absl::SetStderrThreshold(absl::LogSeverityAtLeast::kInfo);

    // const auto map_folder = std::filesystem::path("maps/Texas");
    // const auto map_folder = std::filesystem::path("maps/Dallas");
    const auto map_folder = std::filesystem::path("maps/Columbus Ohio Data");

    // const std::string map_filename = "map.osm.pbf";
    // const std::string map_filename = "northwest-latest.osm.pbf";
    // const std::string map_filename = "map_sub.osm";
    const std::string map_filename = "Columbus, Franklin County, Ohio, United States.pbf";

    Network* network = getNetFromFile(map_folder / map_filename,
                                      {ModeType::AUTO, ModeType::BIKE, ModeType::RAILWAY, ModeType::AEROWAY},
                                      {HighWayLinkType::MOTORWAY, HighWayLinkType::TRUNK, HighWayLinkType::PRIMARY,
                                       HighWayLinkType::SECONDARY, HighWayLinkType::TERTIARY},
                                      {HighWayLinkType::RESIDENTIAL}, true, 1.0, true);

    // consolidateComplexIntersections(network, true);

    // generateNodeActivityInfo(network);

    // fillLinkAttributesWithDefaultValues(network, true, {}, false, {{HighWayLinkType::MOTORWAY, 1}}, true,
    //                                     {{HighWayLinkType::MOTORWAY, 1}});

    outputNetToCSV(network, map_folder);

    delete network;
  } catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
  return 0;
}
