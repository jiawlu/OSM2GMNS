//
// Created by Lu, Jiawei on 5/23/24.
//

#ifndef OSM2GMNS_OSMNETWORK_H
#define OSM2GMNS_OSMNETWORK_H

// #include <osmium/io/any_input.hpp>
// #include <osmium/handler.hpp>
#include <geos.h>

#include <osmium/visitor.hpp>

class OSMNode {
 public:
  explicit OSMNode(const osmium::Node& node)
      : osm_node_id(node.id()), x(node.location().lon()), y(node.location().lat()) {
    //        geometry = GEOSGeom_createPointFromXY(node.location().lon(), node.location().lat());

    const char* name_ = node.tags()["name"];
    if (name_) name = name_;
    const char* highway_ = node.tags()["highway"];
    if (highway_) osm_highway = highway_;
    const char* signal_ = node.tags()["signal"];
    if (signal_ != nullptr) {
      std::string signal_str = signal_;
      ctrl_type = signal_str.find("signal") != std::string::npos ? "signal" : "";
    }

    in_region = true;
    is_crossing = false;

    notes = "";
    node_assigned = false;
    usage_count = 0;
  }

  std::string name{};
  unsigned long osm_node_id;
  Geometry* geometry{};
  double x, y;
  std::string osm_highway{};
  std::string ctrl_type{};

  bool in_region;
  bool is_crossing;

  std::string notes{};
  //    Node* node;
  bool node_assigned;

  int usage_count;
};

class Way {
 public:
  explicit Way(const osmium::Way& way) : osm_way_id(way.id()), number_of_segments(0) {
    for (auto& way_node : way.nodes()) ref_node_id_vector.push_back(way_node.ref());

    const char* highway_ = way.tags()["highway"];
    highway = highway_ ? highway_ : "";
    const char* railway_ = way.tags()["railway"];
    railway = railway_ ? railway_ : "";
    const char* aeroway_ = way.tags()["aeroway"];
    aeroway = aeroway_ ? aeroway_ : "";

    const char* building_ = way.tags()["building"];
    building = building_ ? building_ : "";
    const char* amenity_ = way.tags()["amenity"];
    amenity = amenity_ ? amenity_ : "";
    const char* leisure_ = way.tags()["leisure"];
    leisure = leisure_ ? leisure_ : "";
  }

  unsigned long osm_way_id;
  std::vector<unsigned long> ref_node_id_vector{};
  std::vector<OSMNode*> ref_node_vector{};

  std::string highway{};
  std::string railway{};
  std::string aeroway{};

  bool oneway{};

  std::string building{};
  std::string amenity{};
  std::string leisure{};

  int number_of_segments;
  std::vector<std::vector<OSMNode*>> segment_node_vector{};

  void getNodeListForSegments() {
    int number_of_ref_nodes = 0 = ref_node_vector.size();
    int last_idx = 0;
    int idx = 0;
    OSMNode* osmnode = nullptr;

    while (true) {
      std::vector<OSMNode*> m_segment_node_vector{ref_node_vector[last_idx]};
      for (idx = last_idx + 1; idx < number_of_ref_nodes; idx++) {
        osmnode = ref_node_vector[idx];
        m_segment_node_vector.push_back(osmnode);
        if (osmnode->is_crossing) {
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
};

class OSMNetwork {
 public:
  OSMNetwork() = default;

  std::map<unsigned long, OSMNode*> osm_node_dict{};
  std::map<unsigned long, Way*> osm_way_dict{};

  std::vector<Way*> link_way_vector{};

  Geometry* bounds{};
};

#endif  // OSM2GMNS_OSMNETWORK_H
