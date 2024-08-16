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

    const auto map_folder = std::filesystem::path("dev/maps/District_of_Columbia");
    // const auto map_folder = std::filesystem::path("dev/maps/gatech");
    // const auto map_folder = std::filesystem::path("dev/maps/Ile-de-France");
    // const auto map_folder = std::filesystem::path("dev/maps/debug");

    const std::string map_filename = "map.osm.pbf";
    // const std::string map_filename = "illinois-latest.osm.pbf";
    // const std::string map_filename = "map.osm";

    Network* network = getNetFromFile(map_folder / map_filename, {ModeType::AUTO},
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
