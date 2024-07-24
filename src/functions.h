//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_FUNCTIONS_H
#define OSM2GMNS_FUNCTIONS_H

#include <absl/container/flat_hash_set.h>

#include <filesystem>

#include "networks.h"
#include "osmconfig.h"

constexpr float DEFAULT_INT_BUFFER = 20.0;

Network* getNetFromFile(const std::filesystem::path& osm_filepath,
                        const absl::flat_hash_set<HighWayLinkType>& link_types = {},
                        const absl::flat_hash_set<HighWayLinkType>& connector_link_types = {}, bool POI = false,
                        float POI_sampling_ratio = 1.0, bool strict_boundary = true);

void consolidateComplexIntersections(Network* network, bool auto_identify = false,
                                     const std::filesystem::path& intersection_file = "",
                                     float int_buffer = DEFAULT_INT_BUFFER);

void generateNodeActivityInfo(Network* network, const std::filesystem::path& zone_file = "");

#endif  // OSM2GMNS_FUNCTIONS_H
