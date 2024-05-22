//
// Created by Jiawei Lu on 2/16/23.
//

#ifndef OSM2GMNS_NETWORKS_H
#define OSM2GMNS_NETWORKS_H

#include <geos.h>
#include <string>
#include <map>


//#include <osmium/io/any_input.hpp>
//#include <osmium/handler.hpp>
#include <osmium/visitor.hpp>


class Node;
class Link;

class OSMNode
{
public:
    OSMNode(const osmium::Node& node)
    {
        osm_node_id = node.id();
//        geometry = GEOSGeom_createPointFromXY(node.location().lon(), node.location().lat());
        x = node.location().lon();
        y = node.location().lat();

        const char* name_ = node.tags()["name"];
        if (name_)
            name = name_;
        const char* highway_ = node.tags()["highway"];
        if (highway_)
            osm_highway = highway_;
        const char* signal_ = node.tags()["signal"];
        if (signal_)
        {
            std::string signal_str = signal_;
            ctrl_type = signal_str.find("signal") != std::string::npos ? "signal" : "";
        }

        in_region = true;
        is_crossing = false;

        notes = "";
        node_assigned = false;
        usage_count = 0;
    }

    std::string name;
    unsigned long osm_node_id;
    Geometry* geometry;
    double x, y;
    std::string osm_highway;
    std::string ctrl_type;

    bool in_region;
    bool is_crossing;

    std::string notes;
    Node* node;
    bool node_assigned;

    int usage_count;

};


class Way
{
public:
    Way(const osmium::Way& way)
    {
        osm_way_id = way.id();

        for (auto &way_node : way.nodes())
            ref_node_id_vector.push_back(way_node.ref());

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

        number_of_segments = 0;

    }

    unsigned long osm_way_id;
    std::vector<unsigned long> ref_node_id_vector;
    std::vector<OSMNode*> ref_node_vector;

    std::string highway;
    std::string railway;
    std::string aeroway;

    bool oneway;

    std::string building;
    std::string amenity;
    std::string leisure;

    int number_of_segments;
    std::vector<std::vector<OSMNode*>> segment_node_vector;

    void getNodeListForSegments()
    {
        int number_of_ref_nodes = ref_node_vector.size();
        int last_idx = 0;
        int idx = 0;
        OSMNode *osmnode;

        while (true)
        {
            std::vector<OSMNode*> m_segment_node_vector {ref_node_vector[last_idx]};
            for (idx=last_idx+1; idx<number_of_ref_nodes; idx++)
            {
                osmnode = ref_node_vector[idx];
                m_segment_node_vector.push_back(osmnode);
                if (osmnode->is_crossing)
                {
                    last_idx = idx;
                    break;
                }
            }

            segment_node_vector.push_back(m_segment_node_vector);
            number_of_segments++;

            if (idx == number_of_ref_nodes-1)
                break;
        }
    }
};

class OSMNetwork
{
public:
    OSMNetwork()
    {

    }

    std::map<unsigned long, OSMNode*> osm_node_dict;
    std::map<unsigned long, Way*> osm_way_dict;

    std::vector<Way*> link_way_vector;


    Geometry* bounds;
};



class Node
{
public:
    Node(unsigned int node_id_)
    {
        node_id = node_id_;
    }
    unsigned int node_id;
    std::string name;
    unsigned long osm_node_id;
    std::string osm_highway;
    std::string ctrl_type;
    Geometry* geometry;
    double x, y;
    std::string notes;

    std::vector<Link*> outgoing_link_vector, incoming_link_vector;

    void buildFromOSMNode(OSMNode* osmnode)
    {

        name = osmnode->name;
        osm_node_id = osmnode->osm_node_id;
        osm_highway = osmnode->osm_highway;
        ctrl_type = osmnode->ctrl_type;
        geometry = osmnode->geometry;
        x = osmnode->x;
        y = osmnode->y;
//        self.geometry_xy = osmnode.geometry_xy
        notes = osmnode->notes;
    }



};

class Link
{
public:
    Link(unsigned int link_id_)
    {
        link_id = link_id_;
    }
    unsigned int link_id;
    unsigned long osm_way_id;

    Node *from_node, *to_node;
    Geometry* geometry;


    void buildFromOSMWay(Way *way, std::vector<OSMNode*> &ref_node_vector)
    {
        osm_way_id = way->osm_way_id;
        from_node = ref_node_vector[0]->node;
        to_node = ref_node_vector[ref_node_vector.size()-1]->node;

        from_node->outgoing_link_vector.push_back(this);
        to_node->incoming_link_vector.push_back(this);

    }
};


class Network
{
public:
    Network()
    {
        max_node_id = 0;
        max_link_id = 0;
    }

    std::map<unsigned int, Node*> node_dict;
    std::map<unsigned int, Link*> link_dict;

    unsigned int max_node_id;
    unsigned int max_link_id;
};

#endif //OSM2GMNS_NETWORKS_H
