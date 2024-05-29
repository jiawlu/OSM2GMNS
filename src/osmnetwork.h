//
// Created by Lu, Jiawei on 5/23/24.
//

#ifndef OSM2GMNS_OSMNETWORK_H
#define OSM2GMNS_OSMNETWORK_H

// #include <osmium/io/any_input.hpp>
// #include <osmium/handler.hpp>

#include <cstddef>
#include <cstdint>
#include <map>
#include <memory>
#include <string>
#include <vector>

// #include "absl/strings/match.h"
// #include "geos/geom/Geometry.h"
#include <geos.h>  // NOLINT
#include <geos/geom/Geometry.h>

#include "osmium/osm/node.hpp"
#include "osmium/osm/way.hpp"

using OsmIdType = int64_t;

class OsmNode;

using OsmNodePtr = std::shared_ptr<OsmNode>;

class OsmNode {
 public:
  explicit OsmNode(const osmium::Node& node);

  [[nodiscard]] OsmIdType osmNodeId() const;
  [[nodiscard]] const std::string& name() const;
  [[nodiscard]] bool isCrossing() const;

 private:
  OsmIdType osm_node_id_;
  std::string name_;
  Geometry* geometry{};
  double x, y;
  std::string osm_highway_;
  std::string ctrl_type{};

  bool in_region{true};
  bool is_crossing{false};

  std::string notes{};
  //    Node* node;
  bool node_assigned{false};

  int usage_count{0};
};

class Way {
 public:
  explicit Way(const osmium::Way& way) : osm_way_id(way.id()) {
    for (const auto& way_node : way.nodes()) {
      ref_node_id_vector.push_back(way_node.ref());
    }

    const char* highway_ = way.tags()["highway"];
    highway = highway_ != nullptr ? highway_ : "";
    const char* railway_ = way.tags()["railway"];
    railway = railway_ != nullptr ? railway_ : "";
    const char* aeroway_ = way.tags()["aeroway"];
    aeroway = aeroway_ != nullptr ? aeroway_ : "";

    const char* building_ = way.tags()["building"];
    building = building_ != nullptr ? building_ : "";
    const char* amenity_ = way.tags()["amenity"];
    amenity = amenity_ != nullptr ? amenity_ : "";
    const char* leisure_ = way.tags()["leisure"];
    leisure = leisure_ != nullptr ? leisure_ : "";
  }

  [[nodiscard]] int64_t getOsmWayId() const;

  void getNodeListForSegments() {
    const size_t number_of_ref_nodes = ref_node_vector.size();
    int last_idx = 0;
    int idx = 0;
    OsmNode* osmnode = nullptr;

    while (true) {
      std::vector<OsmNode*> m_segment_node_vector{ref_node_vector[last_idx]};
      for (idx = last_idx + 1; idx < number_of_ref_nodes; idx++) {
        osmnode = ref_node_vector[idx];
        m_segment_node_vector.push_back(osmnode);
        if (osmnode->isCrossing()) {
          last_idx = idx;
          break;
        }
      }

      segment_node_vector.push_back(m_segment_node_vector);
      number_of_segments++;

      if (idx == number_of_ref_nodes - 1) {
        break;
      }
    }
  }

 private:
  int64_t osm_way_id;
  std::vector<OsmIdType> ref_node_id_vector{};
  std::vector<OsmNode*> ref_node_vector{};

  std::string highway{};
  std::string railway{};
  std::string aeroway{};

  bool oneway{};

  std::string building{};
  std::string amenity{};
  std::string leisure{};

  int number_of_segments{0};
  std::vector<std::vector<OsmNode*>> segment_node_vector{};
};

class OSMNetwork {
 public:
  OSMNetwork() = default;

 private:
  std::map<OsmIdType, OsmNode*> osm_node_dict{};
  std::map<OsmIdType, Way*> osm_way_dict{};

  std::vector<Way*> link_way_vector{};

  Geometry* bounds{};
};

#endif  // OSM2GMNS_OSMNETWORK_H
