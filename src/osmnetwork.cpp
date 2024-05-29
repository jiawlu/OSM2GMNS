//
// Created by Lu, Jiawei on 5/23/24.
//

#include "osmnetwork.h"

#include <cstdint>
#include <osmium/osm/node.hpp>
#include <osmium/osm/tag.hpp>
#include <string>

const char* getOSMTagValue(const osmium::TagList& tag_list, const char* tag_key) {
  const char* tag_value = tag_list[tag_key];
  return tag_value != nullptr ? tag_value : "";
}

//        geometry = GEOSGeom_createPointFromXY(node.location().lon(), node.location().lat());
OsmNode::OsmNode(const osmium::Node& node)
    : osm_node_id_(node.id()),
      x(node.location().lon()),
      y(node.location().lat()),
      name_(getOSMTagValue(node.tags(), "name")),
      osm_highway_(getOSMTagValue(node.tags(), "highway")) {
  //  const char* signal_ = node.tags()["signal"];
  //  if (signal_ != nullptr) {
  //    const std::string signal_str = signal_;
  //    ctrl_type = absl::StrContains(signal_str, "signal") ? "signal" : "";
  //  }
}

OsmIdType OsmNode::osmNodeId() const { return osm_node_id_; }
const std::string& OsmNode::name() const { return name_; }
bool OsmNode::isCrossing() const { return is_crossing; }

int64_t Way::getOsmWayId() const { return osm_way_id; }