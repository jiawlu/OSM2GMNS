//
// Created by Jiawei Lu on 2/16/23.
//

#include "networks.h"

#include "osmnetwork.h"

Network::Network(OsmNetwork* osmnet) : osmnet_(osmnet) {}

Network::~Network() { delete osmnet_; }