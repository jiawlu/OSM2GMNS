//
// Created by Lu, Jiawei on 5/23/24.
//

#ifndef OSM2GMNS_OSMNETWORK_H
#define OSM2GMNS_OSMNETWORK_H

#include <absl/container/flat_hash_map.h>
#include <geos/geom/Geometry.h>
#include <geos/geom/GeometryFactory.h>

#include <cstddef>
#include <memory>
#include <osmium/handler.hpp>
#include <osmium/osm/node.hpp>
#include <osmium/osm/way.hpp>
#include <string>
#include <vector>

#include "osmconfig.h"

class OsmNode;
class OsmWay;

class OsmHandler : public osmium::handler::Handler {
 public:
  explicit OsmHandler(bool POI);

  void node(const osmium::Node& node);
  void way(const osmium::Way& way);
  void relation(const osmium::Relation& /*relation*/) const;

  std::vector<OsmNode*>& osmNodeVector();
  std::vector<OsmWay*>& osmWayVector();

 private:
  bool POI_;
  std::vector<OsmNode*> osm_node_vector_;
  std::vector<OsmWay*> osm_way_vector_;
};

class OsmNode {
 public:
  explicit OsmNode(const osmium::Node& node);

  [[nodiscard]] OsmIdType osmNodeId() const;
  [[nodiscard]] const std::string& name() const;
  [[nodiscard]] bool isCrossing() const;

  void initOsmNode(const geos::geom::GeometryFactory* factory, const geos::geom::Polygon* boundary, bool strict_mode);
  void setIsCrossing(bool is_crossing);

 private:
  OsmIdType osm_node_id_;
  std::string name_;
  std::unique_ptr<geos::geom::Point> geometry_;
  double x, y;
  std::string highway_;
  std::string signal_;

  bool is_signalized_{false};
  bool in_region_{true};
  bool is_crossing_{false};

  std::string notes{};
  //    Node* node;
  bool node_assigned{false};

  int usage_count{0};
};

class OsmWay {
 public:
  explicit OsmWay(const osmium::Way& way);

  [[nodiscard]] OsmIdType osmWayId() const;

  void initOsmWay(const absl::flat_hash_map<OsmIdType, OsmNode*>& osm_node_dict);

  //  void setIsValid(bool is_valid);
  //  void setRefNodeVectorSize();
  //  void addRefNode(OsmNode* osm_node);

  void getNodeListForSegments() {
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

 private:
  void mapRefNodes(const absl::flat_hash_map<OsmIdType, OsmNode*>& osm_node_dict);
  void identifyWayType();
  void configAttributes();

  OsmIdType osm_way_id_;
  std::string highway_;
  std::string railway_;
  std::string aeroway_;

  std::string building_;
  std::string amenity_;
  std::string leisure_;
  std::string junction_;
  std::string area_;
  std::string motor_vehicle_;
  std::string motorcar_;
  std::string service_;
  std::string foot_;
  std::string bicycle_;

  std::vector<OsmIdType> ref_node_id_vector_;
  std::vector<OsmNode*> ref_node_vector_;
  bool contains_unknown_ref_nodes_{false};

  WayType way_type_{WayType::OTHER};
  HighWayLinkType highway_link_type_{HighWayLinkType::OTHER};
  bool oneway_{true};

  int number_of_segments{0};
  std::vector<std::vector<OsmNode*>> segment_node_vector_;
};

class OsmNetwork {
 public:
  explicit OsmNetwork(const std::string& osm_filepath, bool POI, bool strict_mode);
  ~OsmNetwork();
  OsmNetwork(const OsmNetwork&) = delete;
  OsmNetwork& operator=(const OsmNetwork&) = delete;
  OsmNetwork(OsmNetwork&&) = delete;
  OsmNetwork& operator=(OsmNetwork&&) = delete;

 private:
  void processRawOsmData();

  bool POI_;
  bool strict_mode_;

  geos::geom::GeometryFactory::Ptr factory_;
  std::unique_ptr<geos::geom::Polygon> boundary_;

  //  absl::flat_hash_map<OsmIdType, OsmNodePtr> osm_node_dict_;
  //  absl::flat_hash_map<OsmIdType, OsmWayPtr> osm_way_dict_;
  absl::flat_hash_map<OsmIdType, OsmNode*> osm_node_dict_;
  absl::flat_hash_map<OsmIdType, OsmWay*> osm_way_dict_;
  std::vector<OsmNode*> osm_node_vector_;
  std::vector<OsmWay*> osm_way_vector_;

  std::vector<OsmWay*> link_way_vector{};

  geos::geom::Geometry* bounds{};
};

#endif  // OSM2GMNS_OSMNETWORK_H
