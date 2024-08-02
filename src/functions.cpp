#include "functions.h"

#include <absl/container/flat_hash_map.h>
#include <absl/container/flat_hash_set.h>
#include <absl/log/log.h>

#include <cstdint>
#include <filesystem>
#include <vector>

#include "io.h"
#include "networks.h"
#include "osmconfig.h"
#include "osmnetwork.h"

VerboseLevel verboseLevel(bool update, VerboseLevel new_level) {
  static VerboseLevel verbose_level = VerboseLevel::Information;
  if (update) {
    verbose_level = new_level;
  }
  return verbose_level;
}

Network* getNetFromFile(const std::filesystem::path& osm_filepath, const absl::flat_hash_set<ModeType>& mode_types,
                        const absl::flat_hash_set<HighWayLinkType>& link_types,
                        const absl::flat_hash_set<HighWayLinkType>& connector_link_types, bool POI,
                        float POI_sampling_ratio, bool strict_boundary) {
  LOG(INFO) << "loading data from osm file";
  auto* osmnet = new OsmNetwork(osm_filepath, mode_types, link_types, connector_link_types, POI, strict_boundary);

  LOG(INFO) << "start to build network";
  return new Network(osmnet, link_types, connector_link_types, POI, POI_sampling_ratio);

  LOG(INFO) << "build network done";
};

void consolidateComplexIntersections(Network* network, bool auto_identify,
                                     const std::filesystem::path& intersection_file, float int_buffer) {
  if (!intersection_file.empty() && !std::filesystem::exists(intersection_file)) {
    LOG(ERROR) << "intersection file " << intersection_file
               << " does not exist. consolidateComplexIntersections() skipped";
    return;
  }
  if (intersection_file.empty()) {
    network->consolidateComplexIntersections(auto_identify, {}, int_buffer);
  } else {
    const std::vector<Intersection*> intersection_vector = readIntersectionFile(intersection_file);
    network->consolidateComplexIntersections(auto_identify, intersection_vector, int_buffer);
  }
}

void generateNodeActivityInfo(Network* network, const std::filesystem::path& zone_file) {
  if (!zone_file.empty() && !std::filesystem::exists(zone_file)) {
    LOG(ERROR) << "zone file " << zone_file << " does not exist. generateNodeActivityInfo() skipped";
    return;
  }
  if (zone_file.empty()) {
    network->generateNodeActivityInfo();
  } else {
    const std::vector<Zone*> zone_vector = readZoneFile(zone_file);
    network->generateNodeActivityInfo(zone_vector);
  }
}

void fillLinkAttributesWithDefaultValues(Network* network, bool default_lanes,
                                         const absl::flat_hash_map<HighWayLinkType, int32_t>& default_lanes_dict,
                                         bool default_speed,
                                         const absl::flat_hash_map<HighWayLinkType, float>& default_speed_dict,
                                         bool default_capacity,
                                         const absl::flat_hash_map<HighWayLinkType, int32_t>& default_capacity_dict) {
  absl::flat_hash_map<HighWayLinkType, int32_t> default_lanes_dict_;
  if (default_lanes) {
    default_lanes_dict_ = getPresetDefaultLanesDict();
    for (const auto& [link_type, default_val] : default_lanes_dict) {
      default_lanes_dict_[link_type] = default_val;
    }
  }
  absl::flat_hash_map<HighWayLinkType, float> default_speed_dict_;
  if (default_speed) {
    default_speed_dict_ = getPresetDefaultSpeedDict();
    for (const auto& [link_type, default_val] : default_speed_dict) {
      default_speed_dict_[link_type] = default_val;
    }
  }
  absl::flat_hash_map<HighWayLinkType, int32_t> default_capacity_dict_;
  if (default_capacity) {
    default_capacity_dict_ = getPresetDefaultCapacityDict();
    for (const auto& [link_type, default_val] : default_capacity_dict) {
      default_capacity_dict_[link_type] = default_val;
    }
  }
  network->fillLinkAttributesWithDefaultValues(default_lanes_dict_, default_speed_dict_, default_capacity_dict_);
}