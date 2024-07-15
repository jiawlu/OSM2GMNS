

add_library(osm2gmns_core STATIC
# add_library(osm2gmns_core
        osmnetwork.cpp
        osmconfig.cpp
        networks.cpp
        io.cpp
        utils.cpp
        functions.cpp)


#target_include_directories(osm2gmns PUBLIC
#        ${CMAKE_CURRENT_SOURCE_DIR}
#        ${CMAKE_SOURCE_DIR}/libraries/protozero/include
#        ${CMAKE_SOURCE_DIR}/libraries/libosmium/include
#        ${CMAKE_SOURCE_DIR}/libraries/geos/include
#        ${CMAKE_BINARY_DIR}/libraries/geos/include
#        )
#
#target_link_directories(osm2gmns PRIVATE
#        ${CMAKE_BINARY_DIR}/libraries/bzip2
#        ${CMAKE_BINARY_DIR}/libraries/libexpat/expat
#        ${CMAKE_BINARY_DIR}/libraries/zlib)
#
#
#target_link_libraries(osm2gmns bz2 expat z)
target_link_libraries(osm2gmns_core PUBLIC ${Required_Libraries})


# set_target_properties(osm2gmns_core PROPERTIES
#     INSTALL_RPATH "${RPATH_DIR}"
# )

# install(TARGETS osm2gmns_core
#     LIBRARY DESTINATION .
# )