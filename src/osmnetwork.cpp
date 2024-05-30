//
// Created by Lu, Jiawei on 5/23/24.
//

#include "osmnetwork.h"

#include <absl/container/flat_hash_map.h>
#include <absl/strings/match.h>

#include <cstdint>
#include <exception>
#include <iostream>
#include <memory>
#include <osmium/io/any_input.hpp>  // NOLINT
#include <osmium/io/file.hpp>       // NOLINT
#include <osmium/io/reader.hpp>     // NOLINT
#include <osmium/osm/node.hpp>
#include <osmium/osm/relation.hpp>
#include <osmium/osm/tag.hpp>
#include <osmium/osm/way.hpp>
#include <osmium/visitor.hpp>  // NOLINT
#include <string>

const char* getOSMTagValue(const osmium::TagList& tag_list, const char* tag_key) {
  const char* tag_value = tag_list[tag_key];
  return tag_value != nullptr ? tag_value : "";
}

OsmHandler::OsmHandler(bool POI) : POI_(POI) {}
void OsmHandler::node(const osmium::Node& node) noexcept {
  osm_node_dict_[node.id()] = std::make_shared<OsmNode>(node);
}
void OsmHandler::way(const osmium::Way& way) noexcept { osm_way_dict_[way.id()] = std::make_shared<OsmWay>(way); }
void OsmHandler::relation(const osmium::Relation& /*unused*/) const noexcept {
  if (!POI_) {
    return;
  }
}

const absl::flat_hash_map<OsmIdType, OsmNodePtr>& OsmHandler::osmNodeDict() { return osm_node_dict_; }
const absl::flat_hash_map<OsmIdType, OsmWayPtr>& OsmHandler::osmWayDict() { return osm_way_dict_; }

OsmNode::OsmNode(const osmium::Node& node)
    : osm_node_id_(node.id()),
      x(node.location().lon()),
      y(node.location().lat()),
      name_(getOSMTagValue(node.tags(), "name")),
      highway_(getOSMTagValue(node.tags(), "highway")),
      signal_(getOSMTagValue(node.tags(), "signal")) {
  if (absl::StrContains(signal_, "signal")) {
    is_signalized = true;
  }
  //        geometry = GEOSGeom_createPointFromXY(node.location().lon(), node.location().lat());
}

OsmIdType OsmNode::osmNodeId() const { return osm_node_id_; }
const std::string& OsmNode::name() const { return name_; }
bool OsmNode::isCrossing() const { return is_crossing; }

OsmWay::OsmWay(const osmium::Way& way)
    : osm_way_id_(way.id()),
      highway_(getOSMTagValue(way.tags(), "highway")),
      railway_(getOSMTagValue(way.tags(), "railway")),
      aeroway_(getOSMTagValue(way.tags(), "aeroway")),
      building_(getOSMTagValue(way.tags(), "building")),
      amenity_(getOSMTagValue(way.tags(), "amenity")),
      leisure_(getOSMTagValue(way.tags(), "leisure")) {
  for (const auto& way_node : way.nodes()) {
    ref_node_id_vector.push_back(way_node.ref());
  }
}

int64_t OsmWay::osmWayId() const { return osm_way_id_; }

OsmNetwork::OsmNetwork(const std::string& osm_filepath, bool POI, bool /*strict_mode*/) {
  OsmHandler handler(POI);
  try {
    const osmium::io::File input_file{osm_filepath};
    osmium::io::Reader reader{input_file};
    osmium::apply(reader, handler);
    reader.close();
  } catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
  }
  std::cout << "nodes: " << handler.osmNodeDict().size() << " ways: " << handler.osmWayDict().size() << "\n";

  processRawOsmData(handler);

  std::cout << "done\n";

  //  getBounds(osmnet, filename);

  //  processNWR(osmnet, &handler);
}

void OsmNetwork::processRawOsmData(const OsmHandler& osm_handler) {}
