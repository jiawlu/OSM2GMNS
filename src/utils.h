//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_UTILS_H
#define OSM2GMNS_UTILS_H

#include <geos/geom/LineString.h>

constexpr double MIN_LAT = -90.0;
constexpr double MAX_LAT = 90.0;
constexpr double MIN_LON = -180.0;
constexpr double MAX_LON = 180.0;

void initializeAbslLogging();
double calculateLineStringLength(const geos::geom::LineString* lineString);

#endif  // OSM2GMNS_UTILS_H
