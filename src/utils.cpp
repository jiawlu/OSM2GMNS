//
// Created by Jiawei Lu on 2/16/23.
//

#include "utils.h"

#include <geos/geom/Coordinate.h>
#include <geos/geom/CoordinateSequence.h>
#include <geos/geom/Geometry.h>
#include <geos/geom/GeometryFactory.h>
#include <geos/geom/LineString.h>
#include <geos/geom/LinearRing.h>
#include <geos/geom/Point.h>
#include <geos/geom/Polygon.h>

#include <GeographicLib/Geodesic.hpp>
#include <GeographicLib/UTMUPS.hpp>
#include <cmath>
#include <cstddef>
#include <memory>
#include <utility>
#include <vector>

constexpr double EARTH_RADIUS = 6371000.0;

// void initializeAbslLogging() {
//   absl::InitializeLog();
//   absl::SetStderrThreshold(absl::LogSeverityAtLeast::kInfo);
// };

// VerboseLevel verboseLevel(bool update, VerboseLevel new_level) {
//   static VerboseLevel verbose_level = VerboseLevel::Information;
//   if (update) {
//     verbose_level = new_level;
//   }
//   return verbose_level;
// }

double toRadians(double degrees) {
  return degrees * 3.14159265 / 180.0;  // NOLINT
}

double haversineDistance(double lon1, double lat1, double lon2, double lat2) {
  const double dLat = toRadians(lat2 - lat1);
  const double dLon = toRadians(lon2 - lon1);
  const double para_a = std::sin(dLat / 2) * std::sin(dLat / 2) +
                        std::cos(toRadians(lat1)) * std::cos(toRadians(lat2)) * std::sin(dLon / 2) * std::sin(dLon / 2);
  const double para_c = 2 * std::atan2(std::sqrt(para_a), std::sqrt(1 - para_a));
  return EARTH_RADIUS * para_c;
}

double calculateLineStringLength(const geos::geom::LineString* lineString) {
  double totalLength = 0.0;
  // const geos::geom::CoordinateSequence* coords = lineString->getCoordinateSequence();
  const std::unique_ptr<geos::geom::CoordinateSequence> coords = lineString->getCoordinates();
  for (std::size_t i = 1; i < coords->size(); ++i) {
    const geos::geom::Coordinate& point_1 = coords->getAt(i - 1);
    const geos::geom::Coordinate& point_2 = coords->getAt(i);
    totalLength += haversineDistance(point_1.x, point_1.y, point_2.x, point_2.y);
  }
  return totalLength;
}

double calculateDistanceBetweenTwoPoints(const geos::geom::Point* point1, const geos::geom::Point* point2) {
  const GeographicLib::Geodesic& geod = GeographicLib::Geodesic::WGS84();
  double distance = 0.0;
  geod.Inverse(point1->getY(), point1->getX(), point2->getY(), point2->getX(), distance);
  return distance;
}

std::unique_ptr<geos::geom::Point> projectPointToUTM(const geos::geom::Point* point,
                                                     const geos::geom::GeometryFactory* factory) {
  double utm_x = 0.0;                                           // Easting (x) in meters
  double utm_y = 0.0;                                           // Northing (y) in meters
  int zone = 0;                                                 // UTM zone
  bool northp = true;                                           // Whether coordinate is in northern hemisphere
  GeographicLib::UTMUPS::Forward(point->getY(), point->getX(),  // Input latitude, longitude
                                 zone, northp,                  // Output zone and hemisphere
                                 utm_x, utm_y);                 // Output easting, northing
  return factory->createPoint(geos::geom::Coordinate(utm_x, utm_y));
}

std::unique_ptr<geos::geom::LineString> projectLineStringToUTM(const geos::geom::LineString* line,
                                                               const geos::geom::GeometryFactory* factory) {
  double utm_x = 0.0;  // Easting (x) in meters
  double utm_y = 0.0;  // Northing (y) in meters
  int zone = 0;        // UTM zone
  bool northp = true;  // Whether coordinate is in northern hemisphere
  geos::geom::CoordinateSequence coord_seq;
  for (size_t pnt_idx = 0; pnt_idx < line->getNumPoints(); ++pnt_idx) {
    const geos::geom::Coordinate& coord = line->getCoordinateN(pnt_idx);
    GeographicLib::UTMUPS::Forward(coord.y, coord.x,  // Input latitude, longitude
                                   zone, northp,      // Output zone and hemisphere
                                   utm_x, utm_y);     // Output easting, northing
    coord_seq.add(utm_x, utm_y);
  }
  return factory->createLineString(coord_seq);
}

std::unique_ptr<geos::geom::Polygon> projectPolygonToUTM(const geos::geom::Polygon* poly,
                                                         const geos::geom::GeometryFactory* factory) {
  double utm_x = 0.0;  // Easting (x) in meters
  double utm_y = 0.0;  // Northing (y) in meters
  int zone = 0;        // UTM zone
  bool northp = true;  // Whether coordinate is in northern hemisphere
  geos::geom::CoordinateSequence coord_seq;
  const geos::geom::LinearRing* ring = poly->getExteriorRing();
  for (size_t pnt_idx = 0; pnt_idx < ring->getNumPoints(); ++pnt_idx) {
    const geos::geom::Coordinate& coord = ring->getCoordinateN(pnt_idx);
    GeographicLib::UTMUPS::Forward(coord.y, coord.x,  // Input latitude, longitude
                                   zone, northp,      // Output zone and hemisphere
                                   utm_x, utm_y);     // Output easting, northing
    coord_seq.add(utm_x, utm_y);
  }
  return factory->createPolygon(std::move(coord_seq));
}

std::unique_ptr<geos::geom::Geometry> projectGeometryToUTM(const geos::geom::Geometry* geometry,
                                                           const geos::geom::GeometryFactory* factory) {
  const geos::geom::GeometryTypeId geometry_type_id = geometry->getGeometryTypeId();
  if (geometry_type_id == geos::geom::GEOS_POINT) {
    return projectPointToUTM(dynamic_cast<const geos::geom::Point*>(geometry), factory);
  }
  if (geometry_type_id == geos::geom::GEOS_LINESTRING) {
    return projectLineStringToUTM(dynamic_cast<const geos::geom::LineString*>(geometry), factory);
  }
  if (geometry_type_id == geos::geom::GEOS_POLYGON) {
    return projectPolygonToUTM(dynamic_cast<const geos::geom::Polygon*>(geometry), factory);
  }

  // if (geometry->isCollection())
  if (geometry_type_id == geos::geom::GEOS_MULTIPOLYGON) {
    const size_t number_of_geometries = geometry->getNumGeometries();
    std::vector<std::unique_ptr<geos::geom::Geometry>> geo_vector;
    geo_vector.reserve(number_of_geometries);
    for (size_t geo_idx = 0; geo_idx < number_of_geometries; ++geo_idx) {
      geo_vector.push_back(
          projectPolygonToUTM(dynamic_cast<const geos::geom::Polygon*>(geometry->getGeometryN(geo_idx)), factory));
    }
    return factory->createMultiPolygon(std::move(geo_vector));
  }
  return nullptr;
}

// const GeographicLib::Geodesic& geod = GeographicLib::Geodesic::WGS84();
//   // Distance from JFK to LHR
//   double
//     lat1 = 40.6, lon1 = -73.8, // JFK Airport
//     lat2 = 51.6, lon2 = -0.5;  // LHR Airport
//   double s12;
//   geod.Inverse(lat1, lon1, lat2, lon2, s12);
//   std::cout << s12 / 1000 << " km\n";
//   std::cout << std::endl;