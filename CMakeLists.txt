cmake_minimum_required(VERSION 3.24)

# if (WIN32)
#     set(CMAKE_C_COMPILER "C:\\mingw64\\bin\\gcc")
#     set(CMAKE_CXX_COMPILER "C:\\mingw64\\bin\\g++")
# elseif(UNIX)
#     set(CMAKE_C_COMPILER /opt/homebrew/Cellar/llvm/15.0.7_1/bin/clang)
#     set(CMAKE_CXX_COMPILER /opt/homebrew/Cellar/llvm/15.0.7_1/bin/clang++)
# endif()

# option(BUILD_X86 "BUILD X86 or not" ON)

#set(CMAKE_OSX_ARCHITECTURES "x86_64")


project(osm2gmns)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)




add_subdirectory(libraries/geos)

add_subdirectory(libraries/bzip2)
add_subdirectory(libraries/libexpat/expat)
add_subdirectory(libraries/zlib)



add_subdirectory(src)

add_executable(osm2gmns_test osm2gmns_test.cpp)

target_link_libraries(osm2gmns_test geos osm2gmns)


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