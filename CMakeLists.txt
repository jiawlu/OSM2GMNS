cmake_minimum_required(VERSION 3.25)
project(osm2gmns)

set(CMAKE_CXX_STANDARD 17)
#set(CMAKE_CXX_STANDARD_REQUIRED True)

include(FetchContent)
set(FETCHCONTENT_QUIET OFF)

FetchContent_Declare(
        protozero
        GIT_REPOSITORY https://github.com/mapbox/protozero.git
        GIT_TAG v1.7.1
        SYSTEM
)
FetchContent_Populate(protozero)
include_directories(${protozero_SOURCE_DIR}/include)

FetchContent_Declare(
        bzip2
        GIT_REPOSITORY https://gitlab.com/bzip2/bzip2.git
        GIT_TAG  master
        SYSTEM
)
FetchContent_MakeAvailable(bzip2)
set(Required_Libraries ${Required_Libraries} bz2)
#include_directories(${geos_SOURCE_DIR}/include)

FetchContent_Declare(
        expat
        GIT_REPOSITORY https://github.com/libexpat/libexpat.git
        GIT_TAG  R_2_6_2
        SYSTEM
)
FetchContent_MakeAvailable(expat)
set(Required_Libraries ${Required_Libraries} expat)
#include_directories(${geos_SOURCE_DIR}/include)

FetchContent_Declare(
        z
        GIT_REPOSITORY https://github.com/madler/zlib.git
        GIT_TAG  v1.3.1
        SYSTEM
)
FetchContent_MakeAvailable(z)
set(Required_Libraries ${Required_Libraries} z)
#include_directories(${geos_SOURCE_DIR}/include)

FetchContent_Declare(
        osmium
        GIT_REPOSITORY https://github.com/osmcode/libosmium.git
        GIT_TAG v2.20.0
        SYSTEM
)
FetchContent_Populate(osmium)
include_directories(${osmium_SOURCE_DIR}/include)


FetchContent_Declare(
        geos
        GIT_REPOSITORY https://github.com/libgeos/geos.git
        GIT_TAG  3.12.1
        SYSTEM
)
FetchContent_MakeAvailable(geos)
#set(Required_Libraries ${Required_Libraries} date::date date::date-tz)
include_directories(${geos_SOURCE_DIR}/include)
include_directories(${geos_BINARY_DIR}/include)

add_subdirectory(src)

option(BUILD_EXE "Build osm2gmns executable" ON)
if (BUILD_EXE)
    add_executable(osm2gmns osm2gmns_main.cpp)
    target_link_libraries(osm2gmns osm2gmns_core)
endif ()

option(BUILD_LIB "Build osm2gmns library" ON)
if (BUILD_LIB)
    add_library(osm2gmnslib osm2gmns_lib.cpp)
    target_link_libraries(osm2gmnslib osm2gmns_core)
    set_target_properties(osm2gmnslib PROPERTIES OUTPUT_NAME osm2gmns)
endif ()

option(BUILD_TEST_DEV "Build Test For Development" OFF)
if (BUILD_TEST_DEV)
    add_subdirectory(test_dev)
endif ()
