project(osm2gmns_test_dev)

add_executable(osm2gmns_test_dev osm2gmns_test_dev.cpp)

target_include_directories(osm2gmns_test_dev PUBLIC ${PROJECT_SOURCE_DIR}/../src)
target_link_libraries(osm2gmns_test_dev osm2gmns_core)