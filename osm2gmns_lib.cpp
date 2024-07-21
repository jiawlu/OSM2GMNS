//
// Created by Jiawei Lu on 2/17/23.
//

#include <absl/container/flat_hash_set.h>
#include <absl/log/log.h>

#include <cstddef>
#include <string>

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

absl::flat_hash_set<HighWayLinkType> parseLinkTypes(const char** link_types_val, size_t link_types_len) {
  absl::flat_hash_set<HighWayLinkType> link_types;
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
  return link_types;
}

extern "C" {

C_API void initializeAbslLoggingPy() { initializeAbslLogging(); };

C_API Network* getNetFromFilePy(const char* osm_filepath, const char** link_types_val, size_t link_types_len,
                                const char** connector_link_types_val, size_t connector_link_types_len, bool POI,
                                float POI_sampling_ratio, bool strict_boundary) {
  const absl::flat_hash_set<HighWayLinkType> link_types = parseLinkTypes(link_types_val, link_types_len);
  const absl::flat_hash_set<HighWayLinkType> connector_link_types =
      parseLinkTypes(connector_link_types_val, connector_link_types_len);
  Network* network =
      getNetFromFile(osm_filepath, link_types, connector_link_types, POI, POI_sampling_ratio, strict_boundary);
  return network;
};

C_API void consolidateComplexIntersectionsPy(Network* network, bool auto_identify, const char* intersection_file,
                                             float int_buffer) {
  consolidateComplexIntersections(network, auto_identify, intersection_file, int_buffer);
};

C_API void generateNodeActivityInfoPy(Network* network, const char* zone_file) {
  generateNodeActivityInfo(network, zone_file);
};

C_API void outputNetToCSVPy(const Network* network, const char* output_folder) {
  outputNetToCSV(network, output_folder);
};

C_API size_t getNumberOfNodesPy(const Network* network) { return network->numberOfNodes(); };
C_API size_t getNumberOfLinksPy(const Network* network) { return network->numberOfLinks(); };
}