cmake_minimum_required(VERSION 3.22)
project(vidur_native LANGUAGES CXX)

################################################################################
# Build settings
################################################################################
set(CMAKE_CXX_STANDARD          20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS             "-Wall -Wextra")
set(CMAKE_CXX_FLAGS_RELEASE     "-g -O3")
set(BUILD_SHARED_LIBS           OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
# Generate compile_commands.json for clang tools
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
add_definitions(-D_GLIBCXX_USE_CXX11_ABI=0)
################################################################################
# Python Configuration
################################################################################

# Supported python versions
set(PYTHON_SUPPORTED_VERSIONS "3.10;3.11;3.12;3.13")

# Include utility functions
include(${CMAKE_CURRENT_LIST_DIR}/cmake/utils.cmake)

# Find Python
if(DEFINED VIDUR_PYTHON_EXECUTABLE)
    find_python_from_executable(
    "${VIDUR_PYTHON_EXECUTABLE}"
    "${PYTHON_SUPPORTED_VERSIONS}"
    )
else()
    message(FATAL_ERROR
        "Please set VIDUR_PYTHON_EXECUTABLE to the path of the desired python version"
        " before running cmake configure."
    )
endif()

################################################################################
# Dependencies
################################################################################

# Fetch and include pybind11
include(FetchContent)
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG        v2.11.1
)

# Fetch and include fmt
FetchContent_Declare(
    fmt
    GIT_REPOSITORY https://github.com/fmtlib/fmt.git
    GIT_TAG        10.1.1
)

FetchContent_MakeAvailable(pybind11 fmt)

# Set include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/csrc/include
)

################################################################################
# Source Files
################################################################################
file(GLOB_RECURSE CPP_SOURCES "csrc/vidur/**/*.cpp")
################################################################################
# Library Output Directory
################################################################################
# Set output director so that it is consistent with the build system
if(NOT DEFINED CMAKE_LIBRARY_OUTPUT_DIRECTORY)
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/vidur)
endif()
################################################################################
# Python Module
################################################################################
# Create the Python module
Python_add_library(_native MODULE ${CPP_SOURCES} WITH_SOABI)

target_include_directories(_native PRIVATE
    ${pybind11_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/csrc/include
)

target_link_libraries(_native PRIVATE
    ${pybind11_LIBRARIES}
    fmt::fmt
)

set_target_properties(_native PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}
)
################################################################################
add_custom_target(default DEPENDS _native)
################################################################################
