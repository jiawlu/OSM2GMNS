project(osm2gmns_dev)

add_executable(osm2gmns_dev osm2gmns_dev.cpp)

target_include_directories(osm2gmns_dev PRIVATE ${PROJECT_SOURCE_DIR}/../src)
target_link_libraries(osm2gmns_dev PRIVATE osm2gmns_core)
