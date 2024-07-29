//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_FUNCTIONS_H
#define OSM2GMNS_FUNCTIONS_H

#include <absl/container/flat_hash_map.h>
#include <absl/container/flat_hash_set.h>

#include <cstdint>
#include <filesystem>

#include "networks.h"
#include "osmconfig.h"

constexpr float DEFAULT_INT_BUFFER = 20.0;

enum class VerboseLevel : uint8_t { None, Information, Trace };

[[maybe_unused]] VerboseLevel verboseLevel(bool update = false, VerboseLevel new_level = VerboseLevel::Information);

Network* getNetFromFile(const std::filesystem::path& osm_filepath,
                        const absl::flat_hash_set<ModeType>& mode_types = {ModeType::AUTO},
                        const absl::flat_hash_set<HighWayLinkType>& link_types = {},
                        const absl::flat_hash_set<HighWayLinkType>& connector_link_types = {}, bool POI = false,
                        float POI_sampling_ratio = 1.0, bool strict_boundary = true);

void consolidateComplexIntersections(Network* network, bool auto_identify = false,
                                     const std::filesystem::path& intersection_file = "",
                                     float int_buffer = DEFAULT_INT_BUFFER);

void generateNodeActivityInfo(Network* network, const std::filesystem::path& zone_file = "");

void fillLinkAttributesWithDefaultValues(
    Network* network, bool default_lanes = false,
    const absl::flat_hash_map<HighWayLinkType, int32_t>& default_lanes_dict = {}, bool default_speed = false,
    const absl::flat_hash_map<HighWayLinkType, float>& default_speed_dict = {}, bool default_capacity = false,
    const absl::flat_hash_map<HighWayLinkType, int32_t>& default_capacity_dict = {});

#endif  // OSM2GMNS_FUNCTIONS_H
