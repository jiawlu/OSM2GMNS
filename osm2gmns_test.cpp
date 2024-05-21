//
// Created by Jiawei Lu on 2/17/23.
//

#include "buildnet.h"
#include "io.h"


int main(int argc, char* argv[]) {
//    if (argc != 2) {
//        std::cerr << "Usage: " << argv[0] << " OSMFILE\n";
//        return 1;
//    }

    std::string filename = "/Users/jiawei/Dropbox (ASU)/Work/CAVLite/OSM2GMNS/maps/AZ/arizona-latest.osm.pbf";
//    std::string filename = "/Users/jiawei/Dropbox (ASU)/Work/CAVLite/OSM2GMNS/maps/asu/asu.osm";

    Network *network = getNetFromFile(filename, false);

    std::cout << "writing network\n";
    outputNetToCSV(network, "/Users/jiawei/Dropbox (ASU)/Work/CAVLite/OSM2GMNS/maps/asu/c");

    std::cout << "done\n";
}
