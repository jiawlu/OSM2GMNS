add_library(osm2gmns_core STATIC
        osmnetwork.cpp
        osmconfig.cpp
        networks.cpp
        io.cpp
        utils.cpp
        functions.cpp)

target_link_libraries(osm2gmns_core PUBLIC ${Required_Libraries})
