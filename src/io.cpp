//
// Created by Jiawei Lu on 2/16/23.
//

#include "io.h"
#include <osmium/io/any_input.hpp>
#include <osmium/handler.hpp>
#include <osmium/visitor.hpp>
#include <iostream>
#include <fstream>
#include <geos.h>



struct CountHandler : public osmium::handler::Handler
{
    bool POI;

    std::map<unsigned long, OSMNode*> osm_node_dict;
    std::map<unsigned long, Way*> osm_way_dict;


    void node(const osmium::Node& node) noexcept
    {
        OSMNode *osm_node = new OSMNode(node);
        osm_node_dict[osm_node->osm_node_id] = osm_node;
    }


    void way(const osmium::Way& way) noexcept
    {
        Way *way_ = new Way(way);
        osm_way_dict[way_->osm_way_id] = way_;
    }


    void relation(const osmium::Relation& relation) noexcept
    {
        if (!POI)
            return;

    }

};

static void
geos_message_handler(const char* fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    vprintf (fmt, ap);
    va_end(ap);
}


void getBounds(OSMNetwork *osmnet, std::string filename)
{


}

void processNWR(OSMNetwork *osmnet, CountHandler *handler)
{
    // ==============  Node ================ //
    osmnet->osm_node_dict = handler->osm_node_dict;

    // ==============  Way ================ //
    for (auto &iter : handler->osm_way_dict)
    {
        bool valid = true;
        for (unsigned long ref_node_id: iter.second->ref_node_id_vector)
        {
            if (handler->osm_node_dict.find(ref_node_id) == handler->osm_node_dict.end())
            {
                valid = false;
                std::cout << "WARNING: ref node " << ref_node_id << " in way " << iter.first << " is not defined, way " << iter.first << "will be skipped\n";
                break;
            }
            iter.second->ref_node_vector.push_back(handler->osm_node_dict[ref_node_id]);
        }

        if (valid)
            osmnet->osm_way_dict[iter.first] = iter.second;
    }

    // ==============  Relation ================ //

}


OSMNetwork* readOSMFile(std::string filename, bool POI, bool strict_mode)
{
//    initGEOS(geos_message_handler, geos_message_handler);

    OSMNetwork *osmnet = new OSMNetwork();
    getBounds(osmnet, filename);

    CountHandler handler;
    handler.POI = POI;

    try
    {
        const osmium::io::File input_file{filename};
        osmium::io::Reader reader{input_file};
        osmium::apply(reader, handler);
        reader.close();
    } catch (const std::exception& e)
    {
        std::cerr << e.what() << '\n';
    }

    processNWR(osmnet, &handler);

    return osmnet;
}

void outputNetToCSV(Network *network, const std::string &output_folder)
{

    std::string node_filepath = output_folder.empty() ? "node.csv" : output_folder + "/node.csv";
    std::ofstream node_file(node_filepath);
    if (!node_file)
    {
        std::cout << "\nError: Cannot open file " << node_filepath << std::endl;
        exit(0);
    }

    node_file << "name,node_id,osm_node_id,ctrl_type,x_coord,y_coord,notes\n";

    for (auto & [node_id, node] : network->node_dict)
    {
        node_file << node->name << "," << node_id << "," << node->osm_node_id << "," << node->ctrl_type << "," << std::to_string(node->x)
                    << "," << std::to_string(node->y) << "," << node->notes << "\n";
    }
    node_file.close();


    std::string link_filepath = output_folder.empty() ? "link.csv" : output_folder + "/link.csv";
    std::ofstream link_file(link_filepath);
    if (!link_file)
    {
        std::cout << "\nError: Cannot open file " << link_filepath << std::endl;
        exit(0);
    }

    link_file << "link_id,osm_way_id,from_node_id,to_node_id,length,geometry\n";
    std::string link_geo;
    for (auto & [link_id, link] : network->link_dict)
    {
        link_geo = "\"LINESTRING (" + std::to_string(link->from_node->x) + " " + std::to_string(link->from_node->y) + ", " + std::to_string(link->to_node->x) + " " + std::to_string(link->to_node->y) + ")\"";

        link_file << link_id << "," << link->osm_way_id << "," << link->from_node->node_id << "," << link->to_node->node_id
                  << ",," << link_geo << "\n";
    }
    link_file.close();
}
