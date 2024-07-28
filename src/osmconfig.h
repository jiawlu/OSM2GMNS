//
// Created by Lu, Jiawei on 5/31/24.
//

#ifndef OSM2GMNS_OSMCONFIG_H
#define OSM2GMNS_OSMCONFIG_H

#include <absl/container/flat_hash_map.h>

#include <cstdint>
#include <string>

using OsmIdType = int64_t;

enum class WayType : uint8_t { HIGHWAY, RAILWAY, AEROWAY, POI, OTHER };

enum class ModeType : uint8_t { AUTO, BIKE, WALK, RAILWAY, AEROWAY, OTHER };

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

ModeType modeStringToModeType(const std::string& mode_type_str);
HighWayLinkType highwayStringToLinkType(const std::string& highway_type_str);

bool checkAllowedUsedAutoInMotor_Vehicle(const std::string& motor_vehicle);
bool checkAllowedUsedAutoInMotorCar(const std::string& motorcar);
bool checkAllowedUsedBikeInBicycle(const std::string& bicycle);
bool checkAllowedUsedWalkInFoot(const std::string& foot);

bool checkAllowedUsedAutoExHighway(const std::string& highway);
bool checkAllowedUsedAutoExMotor_Vehicle(const std::string& motor_vehicle);
bool checkAllowedUsedAutoExMotorCar(const std::string& motorcar);
bool checkAllowedUsedAutoExAccess(const std::string& access);
bool checkAllowedUsedAutoExService(const std::string& service);
bool checkAllowedUsedBikeExHighway(const std::string& highway);
bool checkAllowedUsedBikeExBicycle(const std::string& bicycle);
bool checkAllowedUsedBikeExService(const std::string& service);
bool checkAllowedUsedBikeExAccess(const std::string& access);
bool checkAllowedUsedWalkExHighway(const std::string& highway);
bool checkAllowedUsedWalkExFoot(const std::string& foot);
bool checkAllowedUsedWalkExService(const std::string& service);
bool checkAllowedUsedWalkExAccess(const std::string& access);

bool getDefaultOneWayFlag(HighWayLinkType highway_link_type);

const absl::flat_hash_map<HighWayLinkType, int32_t>& getPresetDefaultLanesDict();
const absl::flat_hash_map<HighWayLinkType, float>& getPresetDefaultSpeedDict();
const absl::flat_hash_map<HighWayLinkType, int32_t>& getPresetDefaultCapacityDict();

bool isHighwayPoiType(const std::string& highway);
bool isRailwayPoiType(const std::string& railway);
bool isAerowayPoiType(const std::string& aeroway);

bool isNegligibleHighwayType(const std::string& highway);
bool isNegligibleRailwayType(const std::string& railway);
bool isNegligibleAerowayType(const std::string& aeroway);

#endif  // OSM2GMNS_OSMCONFIG_H
