//
// Created by Jiawei Lu on 2/16/23.
//

#include "utils.h"

#include <geos/geom/CoordinateSequence.h>
#include <geos/geom/GeometryFactory.h>
#include <geos/geom/LineString.h>
#include <geos/geom/Polygon.h>

#include <cmath>
#include <cstddef>
#include <memory>
#include <utility>
#include <vector>

#include "absl/base/log_severity.h"
#include "absl/log/globals.h"
#include "absl/log/initialize.h"
#include "osmnetwork.h"

constexpr double EARTH_RADIUS = 6371000.0;

void initializeAbslLogging() {
  absl::InitializeLog();
  absl::SetStderrThreshold(absl::LogSeverityAtLeast::kInfo);
};

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

std::unique_ptr<geos::geom::Polygon> getPolygonFromOsmNodes(const std::vector<OsmNode*>& osm_nodes,
                                                            const geos::geom::GeometryFactory* factory) {
  geos::geom::CoordinateSequence coord_seq;
  if (osm_nodes.size() < 3) {
    return nullptr;
  }
  for (const OsmNode* osm_node : osm_nodes) {
    coord_seq.add(*(osm_node->geometry()->getCoordinate()));
  }
  if (osm_nodes.at(0)->osmNodeId() != osm_nodes.back()->osmNodeId()) {
    coord_seq.add(*(osm_nodes.at(0)->geometry()->getCoordinate()));
  }
  return factory->createPolygon(std::move(coord_seq));
}