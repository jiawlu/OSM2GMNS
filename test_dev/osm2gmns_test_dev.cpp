//
// Created by Jiawei Lu on 2/17/23.
//

#include <exception>
#include <filesystem>
#include <iostream>
#include <memory>

#include "functions.h"
#include "io.h"
#include "networks.h"

int main(int /*argc*/, char* /*argv*/[]) {
  try {
    // const auto map_folder = std::filesystem::path("test_dev/maps/yuba");
    const auto map_folder = std::filesystem::path("test_dev/maps/imperial");

    std::unique_ptr<Network> network = getNetFromFile(map_folder / "map.osm.pbf", false);

    std::cout << "writing network\n";
    outputNetToCSV(*network, map_folder);

    std::cout << "done\n";
  } catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
  return 0;
}
