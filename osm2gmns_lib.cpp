//
// Created by Jiawei Lu on 2/17/23.
//

#include <cstddef>

#include "src/functions.h"
#include "src/io.h"
#include "src/networks.h"

#ifdef _WIN32
#define C_API __declspec(dllexport)
#else
#define C_API
#endif

extern "C" {

C_API Network* getNetFromFilePy(const char* osm_filepath, bool POI) {
  Network* network = getNetFromFile(osm_filepath, POI);
  return network;
};

C_API void outputNetToCSVPy(const Network* network, const char* output_folder) {
  outputNetToCSV(network, output_folder);
};

C_API size_t getNumberOfNodesPy(const Network* network) { return network->numberOfNodes(); };
C_API size_t getNumberOfLinksPy(const Network* network) { return network->numberOfLinks(); };
}