//
// Created by Lu, Jiawei on 5/31/24.
//

#ifndef OSM2GMNS_OSMCONFIG_H
#define OSM2GMNS_OSMCONFIG_H

#include <cstdint>
#include <set>
#include <string>

using OsmIdType = int64_t;

enum class WayType : uint8_t { HIGHWAY, RAILWAY, AEROWAY, POI, OTHER };

enum class HighWayLinkType : uint8_t {
  MOTORWAY,
  TRUNK,
  PRIMARY,
  SECONDARY,
  TERTIARY,
  RESIDENTIAL,
  LIVING_STREET,
  SERVICE,
  CYCLEWAY,
  FOOTWAY,
  TRACK,
  UNCLASSIFIED,
  OTHER
};

HighWayLinkType highwayStringToLinkType(const std::string& highway_type_str);

const std::set<std::string>& highwayPOISet();

#endif  // OSM2GMNS_OSMCONFIG_H
