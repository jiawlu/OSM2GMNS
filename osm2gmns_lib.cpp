//
// Created by Jiawei Lu on 2/17/23.
//

#include "src/buildnet.h"
#include "src/io.h"

#ifdef _WIN32
#define C_API __declspec(dllexport)
#else
#define C_API
#endif


extern "C"
{
    C_API Network* getNetFromFilePy(const char *filename, bool POI)
    {
    Network *network = getNetFromFile(filename, POI);
    return network;
    };


    C_API void outputNetToCSVPy(Network* network, const char *output_folder)
    {
        outputNetToCSV(network, output_folder);
    };

    C_API unsigned int getNumberOfNodesPy(Network* network)
    {
        return network->node_dict.size();
    };
    C_API unsigned int getNumberOfLinksPy(Network* network)
    {
        return network->link_dict.size();
    };
}