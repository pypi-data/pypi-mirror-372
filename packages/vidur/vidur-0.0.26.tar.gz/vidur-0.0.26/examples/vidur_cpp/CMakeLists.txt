cmake_minimum_required(VERSION 3.22)
project(vidur_example LANGUAGES CXX)

# Set build settings
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add cmake modules path if needed (where you've placed FindVidur.cmake)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

# Find Vidur using the FindVidur.cmake module
find_package(Vidur REQUIRED)

# Create your executable
add_executable(config_test config_test.cpp)

# Link against Vidur using the imported target
target_link_libraries(config_test PRIVATE Vidur::Vidur)