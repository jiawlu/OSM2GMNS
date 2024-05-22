cmake_minimum_required(VERSION 3.25)
project(osm2gmns)

set(CMAKE_CXX_STANDARD 17)
#set(CMAKE_CXX_STANDARD_REQUIRED True)


#add_subdirectory(libraries/geos)
#add_subdirectory(libraries/bzip2)
#add_subdirectory(libraries/libexpat/expat)
#add_subdirectory(libraries/zlib)

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


#add_executable(osm2gmns_test osm2gmns_test.cpp)
#
#target_link_libraries(osm2gmns_test geos osm2gmns)


#set(CMAKE_BUILD_TYPE  "Release")

#include_directories("../libs/share/libosmium/include" "../libs/share/protozero/include")
#
#include_directories("../libs/mac_arm64/bzip2/include"
#                    "../libs/mac_arm64/expat/include"
#                    "../libs/mac_arm64/geos/include"
#                    "../libs/mac_arm64/zlib/include")
#link_directories("libs/mac_arm64")

# if (APPLE)
#     include_directories("../libs/mac_arm64/bzip2/include"
#             "../libs/mac_arm64/expat/include"
#             "../libs/mac_arm64/geos/include"
#             "../libs/mac_arm64/zlib/include")
#     link_directories("libs/mac_arm64")

# #    include_directories("../libs/mac_x86-64/bzip2/include"
# #            "../libs/mac_x86-64/expat/include"
# #            "../libs/mac_x86-64/geos/include"
# #            "../libs/mac_x86-64/zlib/include")
# #    link_directories("libs/mac_x86-64")
# elseif (UNIX)
#     include_directories("../libs/linux/bzip2/include"
#             "../libs/linux/expat/include"
#             "../libs/linux/geos/include"
#             "../libs/linux/zlib/include")
#     link_directories("libs/linux")
# elseif(WIN32)
#     include_directories("../libs/win/bzip2/include"
#             "../libs/win/expat/include"
#             "../libs/win/geos/include"
#             "../libs/win/zlib/include")
#     link_directories("libs/linux")
# endif()




#add_library(osm2gmns SHARED buildnet.cpp networks.cpp io.cpp util_geo.cpp pyapi.cpp)
#add_executable(osm2gmns buildnet.cpp networks.cpp io.cpp util_geo.cpp osm2gmns.cpp)

#set_target_properties(osm2gmns PROPERTIES LINK_FLAGS "-Wl,-rpath,$SOURCE/libs/mac_arm64")

#add_library(expat SHARED IMPORTED)
#set_target_properties(expat PROPERTIES IMPORTED_LOCATION
#        ${PROJECT_SOURCE_DIR}/libs/mac_arm64/libexpat.dylib)

#target_link_libraries(osm2gmns expat bz2.1 z geos_c.1)

# install(TARGETS osm2gmns DESTINATION bin)

#cmake ..
#make

#mkdir build && cd build
#cmake -DCMAKE_INSTALL_PREFIX:PATH=`pwd`/install ..
#cmake --build . --target install --config Release