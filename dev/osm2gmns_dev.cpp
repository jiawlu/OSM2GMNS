//
// Created by Jiawei Lu on 2/17/23.
//

#include <exception>
#include <filesystem>
#include <iostream>

#include "functions.h"
#include "io.h"
#include "networks.h"
#include "utils.h"

int main(int /*argc*/, char* /*argv*/[]) {
  try {
    initializeAbslLogging();

    const auto map_folder = std::filesystem::path("test_dev/maps/yuba");
    // const auto map_folder = std::filesystem::path("dev/maps/imperial");

    Network* network = getNetFromFile(map_folder / "map.osm.pbf", false);

    outputNetToCSV(network, map_folder);

    delete network;
  } catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
  return 0;
}
