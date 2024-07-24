cmake_minimum_required(VERSION 3.25)
project(osm2gmns VERSION 1.0.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

#include(cmake/StandardSettings.cmake)
#include(cmake/rootutils.cmake)
message("\nStarted CMake for ${PROJECT_NAME} v${PROJECT_VERSION}...\n")
file(MAKE_DIRECTORY ${PROJECT_BINARY_DIR}/config)
configure_file(${PROJECT_SOURCE_DIR}/config.h.in ${PROJECT_BINARY_DIR}/config/config.h)

option(CMAKE_INSTALL_LOCAL_ONLY "Install only locally" ON)
# set(CMAKE_INSTALL_LIBDIR "lib")
# set(CMAKE_INSTALL_LIBDIR ".")
set(BUILD_SHARED_LIBS OFF)
set(ENABLE_SHARED_LIB OFF CACHE BOOL "Build libbz2 as a shared library" FORCE)
set(ENABLE_STATIC_LIB ON CACHE BOOL "Build libbz2 in static mode also" FORCE)
set(EXPAT_SHARED_LIBS OFF)
set(EXPAT_MSVC_STATIC_CRT ON)

# find_program(iwyu_path NAMES include-what-you-use iwyu REQUIRED)
SET(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include(FetchContent)
set(FETCHCONTENT_QUIET OFF)

SET(ABSL_PROPAGATE_CXX_STD ON)
SET(ABSL_BUILD_TESTING OFF)
#set(ABSL_ENABLE_INSTALL ON)

message("CMAKE_SYSTEM_PROCESSOR: ${CMAKE_SYSTEM_PROCESSOR}")

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
        absl::log_initialize
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
set(Required_Libraries ${Required_Libraries} bz2_static)
include_directories(SYSTEM ${bzip2_SOURCE_DIR})

FetchContent_Declare(
        expat
        GIT_REPOSITORY https://github.com/libexpat/libexpat.git
        GIT_TAG  R_2_6_2
        SOURCE_SUBDIR  expat
        SYSTEM
)
FetchContent_MakeAvailable(expat)
include_directories(SYSTEM ${expat_SOURCE_DIR}/expat/lib)
include_directories(SYSTEM ${expat_BINARY_DIR})
if (WIN32)
    set(Required_Libraries ${Required_Libraries} expat)
elseif (UNIX)
    set(Required_Libraries ${Required_Libraries} ${expat_BINARY_DIR}/libexpat.a)
else ()
    message(FATAL_ERROR "Unsupported operating system")
endif ()
# if (CMAKE_SYSTEM_NAME STREQUAL "Windows")
#     set(Required_Libraries ${Required_Libraries} libexpat)
# else ()
#     set(Required_Libraries ${Required_Libraries} expat)
# endif()
# link_directories(${expat_BINARY_DIR})

FetchContent_Declare(
        z
        GIT_REPOSITORY https://github.com/madler/zlib.git
        GIT_TAG  v1.3.1
        SYSTEM
)
FetchContent_MakeAvailable(z)
include_directories(BEFORE SYSTEM ${z_SOURCE_DIR})
include_directories(BEFORE SYSTEM ${z_BINARY_DIR})
if (WIN32)
    set(Required_Libraries ${Required_Libraries} zlibstatic)
elseif (UNIX)
    set(Required_Libraries ${Required_Libraries} ${z_BINARY_DIR}/libz.a)
else ()
    message(FATAL_ERROR "Unsupported operating system")
endif ()
# link_directories(BEFORE ${z_BINARY_DIR})

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
        GIT_TAG  3.12.2
        SYSTEM
)
FetchContent_MakeAvailable(geos)
set(Required_Libraries ${Required_Libraries} GEOS::geos)
include_directories(SYSTEM ${geos_SOURCE_DIR}/include)
include_directories(SYSTEM ${geos_BINARY_DIR}/include)
add_definitions(-DUSE_UNSTABLE_GEOS_CPP_API)

FetchContent_Declare(
        fast-cpp-csv-parser
        GIT_REPOSITORY https://github.com/ben-strasser/fast-cpp-csv-parser.git
        GIT_TAG        master
        SYSTEM
        OVERRIDE_FIND_PACKAGE
)
FetchContent_Populate(fast-cpp-csv-parser)
include_directories(SYSTEM ${fast-cpp-csv-parser_SOURCE_DIR})

find_package(OpenMP REQUIRED)
if (OPENMP_FOUND)
    set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
    set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
endif()
set(Required_Libraries ${Required_Libraries} OpenMP::OpenMP_CXX)

add_subdirectory(src)

option(BUILD_OSM2GMNS_EXE "Build osm2gmns executable" ON)
if (BUILD_OSM2GMNS_EXE)
    add_executable(osm2gmns osm2gmns_main.cpp)
    target_link_libraries(osm2gmns osm2gmns_core)
endif ()

option(BUILD_OSM2GMNS_LIB "Build osm2gmns library" ON)
if (BUILD_OSM2GMNS_LIB)
    add_library(osm2gmnslib SHARED osm2gmns_lib.cpp)
    target_link_libraries(osm2gmnslib osm2gmns_core)
    set_target_properties(osm2gmnslib PROPERTIES OUTPUT_NAME osm2gmns)
    if (WIN32)
        set_target_properties(osm2gmnslib PROPERTIES
            COMPILE_FLAGS "-static-libgcc -static-libstdc++"
            LINK_FLAGS "-static-libgcc -static-libstdc++")
    endif ()
endif ()

option(BUILD_OSM2GMNS_DEV "Build executable for development" OFF)
if (BUILD_OSM2GMNS_DEV)
    add_subdirectory(dev)
endif ()


# if(UNIX)
#     if(APPLE)
#         if (BUILD_OSM2GMNS_EXE)
#             set_target_properties(osm2gmns PROPERTIES INSTALL_RPATH "@executable_path/lib")
#         endif ()
#         if (BUILD_OSM2GMNS_LIB)
#             set_target_properties(osm2gmnslib PROPERTIES INSTALL_RPATH "@loader_path/lib")
#         endif ()
#     else()
#         if (BUILD_OSM2GMNS_EXE)
#             set_target_properties(osm2gmns PROPERTIES INSTALL_RPATH "$ORIGIN/lib")
#         endif ()
#         if (BUILD_OSM2GMNS_LIB)
#             set_target_properties(osm2gmnslib PROPERTIES INSTALL_RPATH "$ORIGIN/lib")
#         endif ()
#     endif()
# elseif(WIN32)
#     # Copy dependencies to the same directory as the executable and library
#     add_custom_command(TARGET YourExecutable POST_BUILD
#         COMMAND ${CMAKE_COMMAND} -E copy_if_different
#             $<TARGET_FILE:SomeLibrary>
#             $<TARGET_FILE_DIR:YourExecutable>
#     )
#     add_custom_command(TARGET YourLibrary POST_BUILD
#         COMMAND ${CMAKE_COMMAND} -E copy_if_different
#             $<TARGET_FILE:SomeLibrary>
#             $<TARGET_FILE_DIR:YourLibrary>
#     )
#     # Install dependencies alongside the executable and library
#     install(FILES $<TARGET_FILE:SomeLibrary> DESTINATION ${INSTALL_ROOT_DIR})
# endif()


if (BUILD_OSM2GMNS_EXE)
    install(TARGETS osm2gmns RUNTIME DESTINATION .)
endif ()
if (BUILD_OSM2GMNS_LIB)
    if (WIN32)
        install(TARGETS osm2gmnslib RUNTIME DESTINATION .)
    else ()
        install(TARGETS osm2gmnslib LIBRARY DESTINATION .)
    endif ()
endif ()
