cmake_minimum_required(VERSION 3.25)
project(osm2gmns VERSION 1.0.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

#include(cmake/StandardSettings.cmake)
#include(cmake/rootutils.cmake)
message("\nStarted CMake for ${PROJECT_NAME} v${PROJECT_VERSION}...\n")
file(MAKE_DIRECTORY ${PROJECT_BINARY_DIR}/config)
configure_file(${PROJECT_SOURCE_DIR}/config.h.in ${PROJECT_BINARY_DIR}/config/config.h)

#set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake")
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)

find_program(iwyu_path NAMES include-what-you-use iwyu REQUIRED)
SET(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include(FetchContent)
set(FETCHCONTENT_QUIET OFF)

SET(ABSL_PROPAGATE_CXX_STD ON)
SET(ABSL_BUILD_TESTING OFF)
#set(ABSL_ENABLE_INSTALL ON)

FetchContent_Declare(
        absl
        GIT_REPOSITORY https://github.com/abseil/abseil-cpp.git
        GIT_TAG 20230125.3
        SYSTEM
)
FetchContent_MakeAvailable(absl)
include_directories(SYSTEM ${absl_SOURCE_DIR})
set(Required_Libraries ${Required_Libraries}
        absl::base
        absl::algorithm
        absl::log
        absl::hash
        absl::memory
        absl::numeric
        absl::strings
        absl::raw_hash_map
)

FetchContent_Declare(
        protozero
        GIT_REPOSITORY https://github.com/mapbox/protozero.git
        GIT_TAG v1.7.1
        SYSTEM
)
FetchContent_Populate(protozero)
include_directories(SYSTEM ${protozero_SOURCE_DIR}/include)

FetchContent_Declare(
        bzip2
        GIT_REPOSITORY https://gitlab.com/bzip2/bzip2.git
        GIT_TAG  master
        SYSTEM
)
FetchContent_MakeAvailable(bzip2)
set(Required_Libraries ${Required_Libraries} bz2)
include_directories(SYSTEM ${bzip2_SOURCE_DIR})

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
include_directories(SYSTEM ${osmium_SOURCE_DIR}/include)


FetchContent_Declare(
        geos
        GIT_REPOSITORY https://github.com/libgeos/geos.git
        GIT_TAG  3.12.1
        SYSTEM
)
FetchContent_MakeAvailable(geos)
set(Required_Libraries ${Required_Libraries} GEOS::geos)
include_directories(SYSTEM ${geos_SOURCE_DIR}/include)
include_directories(SYSTEM ${geos_BINARY_DIR}/include)
add_definitions(-DUSE_UNSTABLE_GEOS_CPP_API)

find_package(OpenMP REQUIRED)
if (OPENMP_FOUND)
    set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
    set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
endif()
set(Required_Libraries ${Required_Libraries} OpenMP::OpenMP_CXX)

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
    set_target_properties(osm2gmnslib PROPERTIES
        OUTPUT_NAME osm2gmns
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/osm2gmns")
endif ()

option(BUILD_TEST_DEV "Build Test For Development" OFF)
if (BUILD_TEST_DEV)
    add_subdirectory(test_dev)
endif ()
