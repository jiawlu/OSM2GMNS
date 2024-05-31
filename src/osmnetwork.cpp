//
// Created by Lu, Jiawei on 5/23/24.
//

#include "osmnetwork.h"

#include <absl/container/flat_hash_map.h>
#include <absl/strings/match.h>

#include <chrono>
#include <exception>
#include <iostream>
#include <osmium/io/any_input.hpp>  // NOLINT
#include <osmium/io/file.hpp>       // NOLINT
#include <osmium/io/reader.hpp>     // NOLINT
#include <osmium/osm/node.hpp>
#include <osmium/osm/relation.hpp>
#include <osmium/osm/tag.hpp>
#include <osmium/osm/way.hpp>
#include <osmium/visitor.hpp>  // NOLINT
#include <string>
#include <utility>
#include <vector>

#include "constants.h"

const char* getOSMTagValue(const osmium::TagList& tag_list, const char* tag_key) {
  const char* tag_value = tag_list[tag_key];
  return tag_value != nullptr ? tag_value : "";
}

OsmHandler::OsmHandler(bool POI) : POI_(POI) {}
void OsmHandler::node(const osmium::Node& node) {
  //  osm_node_dict_[node.id()] = std::make_shared<OsmNode>(node);
  osm_node_vector_.push_back(new OsmNode(node));
}
void OsmHandler::way(const osmium::Way& way) {
  //  osm_way_dict_[way.id()] = std::make_shared<OsmWay>(way);
  osm_way_vector_.push_back(new OsmWay(way));
}
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
  //        geometry = GEOSGeom_createPointFromXY(node.location().lon(), node.location().lat());
}

OsmIdType OsmNode::osmNodeId() const { return osm_node_id_; }
const std::string& OsmNode::name() const { return name_; }
bool OsmNode::isCrossing() const { return is_crossing_; }

void OsmNode::setIsCrossing(bool is_crossing) { is_crossing_ = is_crossing; }

OsmWay::OsmWay(const osmium::Way& way)
    : osm_way_id_(way.id()),
      highway_(getOSMTagValue(way.tags(), "highway")),
      railway_(getOSMTagValue(way.tags(), "railway")),
      aeroway_(getOSMTagValue(way.tags(), "aeroway")),
      building_(getOSMTagValue(way.tags(), "building")),
      amenity_(getOSMTagValue(way.tags(), "amenity")),
      leisure_(getOSMTagValue(way.tags(), "leisure")) {
  for (const auto& way_node : way.nodes()) {
    ref_node_id_vector_.push_back(way_node.ref());
  }
}

OsmIdType OsmWay::osmWayId() const { return osm_way_id_; }
const std::vector<OsmIdType>& OsmWay::refNodeIdVector() const { return ref_node_id_vector_; }

void OsmWay::setIsValid(bool is_valid) { is_valid_ = is_valid; }
void OsmWay::setRefNodeVectorSize() { ref_node_vector_.reserve(ref_node_id_vector_.size()); }
void OsmWay::addRefNode(OsmNode* osm_node) { ref_node_vector_.push_back(osm_node); }

OsmNetwork::OsmNetwork(const std::string& osm_filepath, bool POI, bool /*strict_mode*/) {
  auto time1 = std::chrono::high_resolution_clock::now();
  OsmHandler handler(POI);
  try {
    const osmium::io::File input_file{osm_filepath};
    osmium::io::Reader reader{input_file};
    osmium::apply(reader, handler);
    reader.close();
  } catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
  }
  auto time2 = std::chrono::high_resolution_clock::now();
  std::cout << "parse osm"
            << (std::chrono::duration_cast<std::chrono::microseconds>(time2 - time1) * MICROSECONDS_TO_SECOND).count()
            << "seconds\n";

  //  osm_node_dict_ = std::move(handler.osmNodeDict());
  //  osm_way_dict_ = std::move(handler.osmWayDict());
  //  std::cout << "nodes: " << osm_node_dict_.size() << " ways: " << osm_way_dict_.size() << "\n";
  osm_node_vector_ = std::move(handler.osmNodeVector());
  osm_way_vector_ = std::move(handler.osmWayVector());
  std::cout << "nodes: " << osm_node_vector_.size() << " ways: " << osm_way_vector_.size() << "\n";

  auto time3 = std::chrono::high_resolution_clock::now();
  std::cout << "pass osm"
            << (std::chrono::duration_cast<std::chrono::microseconds>(time3 - time2) * MICROSECONDS_TO_SECOND).count()
            << "seconds\n";

  processRawOsmData();

  //  getBounds(osmnet, filename);

  //  processNWR(osmnet, &handler);
  auto time4 = std::chrono::high_resolution_clock::now();
  std::cout << "process osm"
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
  for (OsmNode* osm_node : osm_node_vector_) {
    osm_node_dict_[osm_node->osmNodeId()] = osm_node;
  }

  /*================= OsmWay =================*/
  for (OsmWay* osm_way : osm_way_vector_) {
    osm_way_dict_[osm_way->osmWayId()] = osm_way;
  }

#pragma omp parallel for schedule(dynamic) default(none) shared(osm_way_vector_, osm_node_dict_, std::cout)
  for (OsmWay* osm_way : osm_way_vector_) {
    bool unknown_ref_node_found = false;
    OsmIdType unknown_ref_node_id = 0;
    osm_way->setRefNodeVectorSize();
    for (const OsmIdType ref_node_id : osm_way->refNodeIdVector()) {
      auto iter = osm_node_dict_.find(ref_node_id);
      if (iter != osm_node_dict_.end()) {
        osm_way->addRefNode(iter->second);
      } else {
        unknown_ref_node_found = true;
        unknown_ref_node_id = ref_node_id;
        break;
      }
    }
    if (unknown_ref_node_found) {
      std::cout << "  warning: ref node " << unknown_ref_node_id << " in way " << osm_way->osmWayId()
                << " is not defined, way " << osm_way->osmWayId() << " will not be imported\n";
    }
  }

  std::cout << "done\n";
}
