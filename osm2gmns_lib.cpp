//
// Created by Jiawei Lu on 2/17/23.
//

#include <absl/container/flat_hash_map.h>
#include <absl/container/flat_hash_set.h>
#include <absl/log/log.h>

#include <cstddef>
#include <cstdint>
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
    const std::string& link_type_str = link_types_val[idx];  // NOLINT
    const HighWayLinkType link_type = highwayStringToLinkType(link_type_str);
    if (link_type != HighWayLinkType::OTHER) {
      link_types.insert(link_type);
    } else {
      LOG(WARNING) << "unrecogonized link_type " << link_type_str;
    }
  }
  return link_types;
}

absl::flat_hash_set<ModeType> parseModeTypes(const char** mode_types_val, size_t mode_types_len) {
  absl::flat_hash_set<ModeType> mode_types;
  mode_types.reserve(mode_types_len);
  for (size_t idx = 0; idx < mode_types_len; ++idx) {
    const std::string& mode_type_str = mode_types_val[idx];  // NOLINT
    const ModeType mode_type = modeStringToModeType(mode_type_str);
    if (mode_type != ModeType::OTHER) {
      mode_types.insert(mode_type);
    } else {
      LOG(WARNING) << "unrecogonized mode_type " << mode_type_str;
    }
  }
  return mode_types;
}

template <typename T>
struct StrNumDict {
  const char* key;
  T value;
};

template <typename T>
absl::flat_hash_map<HighWayLinkType, T> parseLinkTypeToNumDict(const StrNumDict<T>* dict_val, size_t dict_len) {
  absl::flat_hash_map<HighWayLinkType, T> dict;
  for (size_t idx = 0; idx < dict_len; ++idx) {
    const std::string& link_type_str = dict_val[idx].key;  // NOLINT
    const HighWayLinkType link_type = highwayStringToLinkType(link_type_str);
    if (link_type != HighWayLinkType::OTHER) {
      dict.emplace(link_type, dict_val[idx].value);  // NOLINT
    } else {
      LOG(WARNING) << "unrecogonized link_type " << link_type_str;
    }
  }
  return dict;
}

extern "C" {

C_API void initializeAbslLoggingPy() { initializeAbslLogging(); };

C_API void releaseNetworkMemoryPy(Network* network) { delete network; };

C_API Network* getNetFromFilePy(const char* osm_filepath, const char** mode_types_val, size_t mode_types_len,
                                const char** link_types_val, size_t link_types_len,
                                const char** connector_link_types_val, size_t connector_link_types_len, bool POI,
                                float POI_sampling_ratio, bool strict_boundary) {
  const absl::flat_hash_set<ModeType> mode_types = parseModeTypes(mode_types_val, mode_types_len);
  const absl::flat_hash_set<HighWayLinkType> link_types = parseLinkTypes(link_types_val, link_types_len);
  const absl::flat_hash_set<HighWayLinkType> connector_link_types =
      parseLinkTypes(connector_link_types_val, connector_link_types_len);
  Network* network = getNetFromFile(osm_filepath, mode_types, link_types, connector_link_types, POI, POI_sampling_ratio,
                                    strict_boundary);
  return network;
};

C_API void consolidateComplexIntersectionsPy(Network* network, bool auto_identify, const char* intersection_file,
                                             float int_buffer) {
  consolidateComplexIntersections(network, auto_identify, intersection_file, int_buffer);
};

C_API void generateNodeActivityInfoPy(Network* network, const char* zone_file) {
  generateNodeActivityInfo(network, zone_file);
};

C_API void fillLinkAttributesWithDefaultValuesPy(Network* network, bool default_lanes,
                                                 const StrNumDict<int32_t>* default_lanes_dict_val,
                                                 size_t default_lanes_dict_len, bool default_speed,
                                                 const StrNumDict<float>* default_speed_dict_val,
                                                 size_t default_speed_dict_len, bool default_capacity,
                                                 const StrNumDict<int32_t>* default_capacity_dict_val,
                                                 size_t default_capacity_dict_len) {
  const absl::flat_hash_map<HighWayLinkType, int32_t> default_lanes_dict =
      parseLinkTypeToNumDict<int32_t>(default_lanes_dict_val, default_lanes_dict_len);
  const absl::flat_hash_map<HighWayLinkType, float> default_speed_dict =
      parseLinkTypeToNumDict<float>(default_speed_dict_val, default_speed_dict_len);
  const absl::flat_hash_map<HighWayLinkType, int32_t> default_capacity_dict =
      parseLinkTypeToNumDict<int32_t>(default_capacity_dict_val, default_capacity_dict_len);
  fillLinkAttributesWithDefaultValues(network, default_lanes, default_lanes_dict, default_speed, default_speed_dict,
                                      default_capacity, default_capacity_dict);
}

C_API void outputNetToCSVPy(const Network* network, const char* output_folder) {
  outputNetToCSV(network, output_folder);
};

C_API size_t getNumberOfNodesPy(const Network* network) { return network->numberOfNodes(); };
C_API size_t getNumberOfLinksPy(const Network* network) { return network->numberOfLinks(); };
}