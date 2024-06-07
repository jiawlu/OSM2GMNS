//
// Created by Lu, Jiawei on 5/23/24.
//

#include "osmnetwork.h"

#include <absl/container/flat_hash_map.h>
#include <absl/strings/match.h>
#include <geos/geom/Coordinate.h>
#include <geos/geom/GeometryFactory.h>
#include <geos/geom/Polygon.h>

#include <chrono>
#include <cstddef>
#include <exception>
#include <filesystem>
#include <iostream>
#include <osmium/io/any_input.hpp>  // NOLINT
#include <osmium/io/file.hpp>       // NOLINT
#include <osmium/io/reader.hpp>     // NOLINT
#include <osmium/osm/box.hpp>
#include <osmium/osm/node.hpp>
#include <osmium/osm/relation.hpp>
#include <osmium/osm/tag.hpp>
#include <osmium/osm/way.hpp>
#include <osmium/visitor.hpp>  // NOLINT
#include <string>
#include <utility>
#include <vector>

#include "constants.h"
#include "osmconfig.h"
#include "utils.h"

const char* getOSMTagValue(const osmium::TagList& tag_list, const char* tag_key) {
  const char* tag_value = tag_list[tag_key];
  return tag_value != nullptr ? tag_value : "";
}

OsmHandler::OsmHandler(bool POI) : POI_(POI) {}
void OsmHandler::node(const osmium::Node& node) { osm_node_vector_.push_back(new OsmNode(node)); }
void OsmHandler::way(const osmium::Way& way) { osm_way_vector_.push_back(new OsmWay(way)); }
void OsmHandler::relation(const osmium::Relation& /*unused*/) const {
  if (!POI_) {
    return;
  }
}

std::vector<OsmNode*>& OsmHandler::osmNodeVector() { return osm_node_vector_; }
std::vector<OsmWay*>& OsmHandler::osmWayVector() { return osm_way_vector_; }

OsmNode::OsmNode(const osmium::Node& node)
    : osm_node_id_(node.id()),
      x(node.location().lon()),
      y(node.location().lat()),
      name_(getOSMTagValue(node.tags(), "name")),
      highway_(getOSMTagValue(node.tags(), "highway")),
      signal_(getOSMTagValue(node.tags(), "signal")) {
  if (absl::StrContains(signal_, "signal")) {
    is_signalized_ = true;
  }
}

OsmIdType OsmNode::osmNodeId() const { return osm_node_id_; }
const std::string& OsmNode::name() const { return name_; }
bool OsmNode::isCrossing() const { return is_crossing_; }

void OsmNode::initOsmNode(const geos::geom::GeometryFactory* factory, const geos::geom::Polygon* boundary,
                          bool strict_mode) {
  geometry_ = factory->createPoint(geos::geom::Coordinate(x, y));
  if (strict_mode && !boundary->covers(geometry_.get())) {
    in_region_ = false;
  }
}
void OsmNode::setIsCrossing(bool is_crossing) { is_crossing_ = is_crossing; }

OsmWay::OsmWay(const osmium::Way& way)
    : osm_way_id_(way.id()),
      highway_(getOSMTagValue(way.tags(), "highway")),
      railway_(getOSMTagValue(way.tags(), "railway")),
      aeroway_(getOSMTagValue(way.tags(), "aeroway")),
      building_(getOSMTagValue(way.tags(), "building")),
      amenity_(getOSMTagValue(way.tags(), "amenity")),
      leisure_(getOSMTagValue(way.tags(), "leisure")),
      junction_(getOSMTagValue(way.tags(), "junction")),
      area_(getOSMTagValue(way.tags(), "area")),
      motor_vehicle_(getOSMTagValue(way.tags(), "motor_vehicle")),
      motorcar_(getOSMTagValue(way.tags(), "motorcar")),
      service_(getOSMTagValue(way.tags(), "service")),
      foot_(getOSMTagValue(way.tags(), "foot")),
      bicycle_(getOSMTagValue(way.tags(), "bicycle")) {
  for (const auto& way_node : way.nodes()) {
    ref_node_id_vector_.push_back(way_node.ref());
  }
}

OsmIdType OsmWay::osmWayId() const { return osm_way_id_; }
// const std::vector<OsmIdType>& OsmWay::refNodeIdVector() const { return ref_node_id_vector_; }

void OsmWay::initOsmWay(const absl::flat_hash_map<OsmIdType, OsmNode*>& osm_node_dict) {
  mapRefNodes(osm_node_dict);
  if (contains_unknown_ref_nodes_) {
    return;
  }
  identifyWayType();
  configAttributes();
}

void OsmWay::mapRefNodes(const absl::flat_hash_map<OsmIdType, OsmNode*>& osm_node_dict) {
  bool unknown_ref_node_found = false;
  OsmIdType unknown_ref_node_id = 0;
  ref_node_vector_.reserve(ref_node_id_vector_.size());
  for (const OsmIdType ref_node_id : ref_node_id_vector_) {
    auto iter = osm_node_dict.find(ref_node_id);
    if (iter != osm_node_dict.end()) {
      ref_node_vector_.push_back(iter->second);
    } else {
      unknown_ref_node_found = true;
      unknown_ref_node_id = ref_node_id;
      break;
    }
  }
  if (unknown_ref_node_found) {
#pragma omp critical
    std::cout << "  warning: ref node " << unknown_ref_node_id << " in way " << osm_way_id_ << " is not defined, way "
              << osm_way_id_ << " will not be imported\n";
    contains_unknown_ref_nodes_ = true;
  }
}

void OsmWay::identifyWayType() {
  if (!(building_.empty() && amenity_.empty() && leisure_.empty())) {
    way_type_ = WayType::POI;
  } else if (!highway_.empty()) {
    if (highwayPOISet().find(highway_) != highwayPOISet().end()) {
      way_type_ = WayType::POI;
    }
    way_type_ = WayType::HIGHWAY;
    highway_link_type_ = highwayStringToLinkType(highway_);
    if (highway_link_type_ == HighWayLinkType::OTHER) {
#pragma omp critical
      std::cout << "  warning: new highway type " << highway_ << " is detected.\n";
    }
  } else if (!railway_.empty()) {
    way_type_ = WayType::RAILWAY;
  } else if (!aeroway_.empty()) {
    way_type_ = WayType::AEROWAY;
  } else {
    way_type_ = WayType::OTHER;
  }
}

void OsmWay::configAttributes() {}

void OsmWay::splitIntoSegments() {
  const size_t number_of_ref_nodes = ref_node_vector_.size();
  int last_idx = 0;
  int idx = 0;
  OsmNode* osmnode = nullptr;

  while (true) {
    std::vector<OsmNode*> m_segment_node_vector{ref_node_vector_[last_idx]};
    for (idx = last_idx + 1; idx < number_of_ref_nodes; idx++) {
      osmnode = ref_node_vector_[idx];
      m_segment_node_vector.push_back(osmnode);
      if (osmnode->isCrossing()) {
        last_idx = idx;
        break;
      }
    }

    segment_node_vector_.push_back(m_segment_node_vector);
    number_of_segments++;

    if (idx == number_of_ref_nodes - 1) {
      break;
    }
  }
}

OsmNetwork::OsmNetwork(const std::filesystem::path& osm_filepath, bool POI, bool strict_mode)
    : POI_(POI), strict_mode_(strict_mode) {
  factory_ = geos::geom::GeometryFactory::create();

  const auto time1 = std::chrono::high_resolution_clock::now();
  OsmHandler handler(POI);
  try {
    const osmium::io::File input_file{osm_filepath};
    osmium::io::Reader reader{input_file};

    const osmium::Box& box = reader.header().box();
    if (reader.header().box().valid()) {
      boundary_ = factory_->createPolygon({geos::geom::Coordinate(box.bottom_left().lon(), box.bottom_left().lat()),
                                           geos::geom::Coordinate(box.top_right().lon(), box.bottom_left().lat()),
                                           geos::geom::Coordinate(box.top_right().lon(), box.top_right().lat()),
                                           geos::geom::Coordinate(box.bottom_left().lon(), box.top_right().lat()),
                                           geos::geom::Coordinate(box.bottom_left().lon(), box.bottom_left().lat())});
    } else {
      std::cout << "  warning: no valid boundary information in the osm file\n";
      boundary_ =
          factory_->createPolygon({geos::geom::Coordinate(MIN_LON, MIN_LAT), geos::geom::Coordinate(MAX_LON, MIN_LAT),
                                   geos::geom::Coordinate(MAX_LON, MAX_LAT), geos::geom::Coordinate(MIN_LON, MAX_LAT),
                                   geos::geom::Coordinate(MIN_LON, MIN_LAT)});
    }

    osmium::apply(reader, handler);
    reader.close();
  } catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
  }
  const auto time2 = std::chrono::high_resolution_clock::now();
  std::cout << "parse osm "
            << (std::chrono::duration_cast<std::chrono::microseconds>(time2 - time1) * MICROSECONDS_TO_SECOND).count()
            << "seconds\n";

  osm_node_vector_ = std::move(handler.osmNodeVector());
  osm_way_vector_ = std::move(handler.osmWayVector());
  std::cout << "nodes: " << osm_node_vector_.size() << " ways: " << osm_way_vector_.size() << "\n";
  for (OsmNode* osm_node : osm_node_vector_) {
    osm_node_dict_[osm_node->osmNodeId()] = osm_node;
  }
  for (OsmWay* osm_way : osm_way_vector_) {
    osm_way_dict_[osm_way->osmWayId()] = osm_way;
  }

  const auto time3 = std::chrono::high_resolution_clock::now();
  std::cout << "pass osm "
            << (std::chrono::duration_cast<std::chrono::microseconds>(time3 - time2) * MICROSECONDS_TO_SECOND).count()
            << "seconds\n";

  processRawOsmData();

  //  getBounds(osmnet, filename);

  //  processNWR(osmnet, &handler);
  const auto time4 = std::chrono::high_resolution_clock::now();
  std::cout << "process osm "
            << (std::chrono::duration_cast<std::chrono::microseconds>(time4 - time3) * MICROSECONDS_TO_SECOND).count()
            << "seconds\n";
}

OsmNetwork::~OsmNetwork() {
#pragma omp parallel for schedule(dynamic) default(none) shared(osm_node_vector_)
  for (OsmNode* osm_node : osm_node_vector_) {
    delete osm_node;
  }
#pragma omp parallel for schedule(dynamic) default(none) shared(osm_way_vector_)
  for (OsmWay* osm_way : osm_way_vector_) {
    delete osm_way;
  }
}

void OsmNetwork::processRawOsmData() {
  /*================= OsmNode =================*/
#pragma omp parallel for schedule(dynamic) default(none) shared(osm_node_vector_, factory_, boundary_, strict_mode_)
  for (OsmNode* osm_node : osm_node_vector_) {
    osm_node->initOsmNode(factory_.get(), boundary_.get(), strict_mode_);
  }

  /*================= OsmWay =================*/
#pragma omp parallel for schedule(dynamic) default(none) shared(osm_way_vector_, osm_node_dict_)
  for (OsmWay* osm_way : osm_way_vector_) {
    osm_way->initOsmWay(osm_node_dict_);
  }

  std::cout << "done\n";
}
