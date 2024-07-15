//
// Created by Jiawei Lu on 2/17/23.
//

#include <absl/log/log.h>

#include <cstddef>
#include <string>
#include <unordered_set>

#include "src/functions.h"
#include "src/io.h"
#include "src/networks.h"
#include "src/osmconfig.h"
#include "src/utils.h"

#ifdef _WIN32
#define C_API __declspec(dllexport)
#else
#define C_API
#endif

extern "C" {

C_API void initializeAbslLoggingPy() { initializeAbslLogging(); };

C_API Network* getNetFromFilePy(const char* osm_filepath, const char** link_types_val, size_t link_types_len,
                                bool POI) {
  std::unordered_set<HighWayLinkType> link_types;
  link_types.reserve(link_types_len);
  for (size_t idx = 0; idx < link_types_len; ++idx) {
    const std::string link_type_str = link_types_val[idx];  // NOLINT
    const HighWayLinkType link_type = highwayStringToLinkType(link_type_str);
    if (link_type != HighWayLinkType::OTHER) {
      link_types.insert(link_type);
    } else {
      LOG(WARNING) << "unrecogonized link_type " << link_type_str;
    }
  }

  Network* network = getNetFromFile(osm_filepath, link_types, POI);
  return network;
};

C_API void outputNetToCSVPy(const Network* network, const char* output_folder) {
  outputNetToCSV(network, output_folder);
};

C_API size_t getNumberOfNodesPy(const Network* network) { return network->numberOfNodes(); };
C_API size_t getNumberOfLinksPy(const Network* network) { return network->numberOfLinks(); };
}