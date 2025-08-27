# FindVidur.cmake
# Locates the Vidur library and its include files
#
# This module defines the following variables:
#  VIDUR_FOUND        - True if Vidur was found
#  VIDUR_INCLUDE_DIR  - The Vidur include directory
#  VIDUR_LIBRARY      - The Vidur library path
#  Vidur::Vidur       - Imported target for Vidur
#
# Example usage:
#  find_package(Vidur REQUIRED)
#  target_link_libraries(your_target PRIVATE Vidur::Vidur)

# Find Python package (required for Python C API and to locate Vidur)
find_package(Python3 COMPONENTS Development REQUIRED)

# Function to find Python site-packages directory
function(find_python_site_packages_dir result)
    execute_process(
        COMMAND python3 -c "import site; print(site.getsitepackages()[0])"
        OUTPUT_VARIABLE SITE_PACKAGES_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    set(${result} ${SITE_PACKAGES_DIR} PARENT_SCOPE)
endfunction()

# Function to check if Vidur is installed
function(check_vidur_installed result)
    execute_process(
        COMMAND python3 -c "import importlib.util; print(importlib.util.find_spec('vidur') is not None)"
        OUTPUT_VARIABLE VIDUR_INSTALLED
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    set(${result} ${VIDUR_INSTALLED} PARENT_SCOPE)
endfunction()

# Check if Vidur is installed
check_vidur_installed(VIDUR_INSTALLED)

if(NOT "${VIDUR_INSTALLED}" STREQUAL "True")
    message(STATUS "Vidur Python package not found. Make sure it's installed with 'pip install vidur'")
    set(VIDUR_FOUND FALSE)
    return()
endif()

# Get site-packages directory
find_python_site_packages_dir(PYTHON_SITE_PACKAGES)

# Try to find the Vidur library
# Look for different possible extensions based on platform
if(WIN32)
    file(GLOB VIDUR_LIB_CANDIDATES "${PYTHON_SITE_PACKAGES}/vidur/_native*.pyd")
elseif(APPLE)
    file(GLOB VIDUR_LIB_CANDIDATES "${PYTHON_SITE_PACKAGES}/vidur/_native*.so" "${PYTHON_SITE_PACKAGES}/vidur/_native*.dylib")
else() # Linux and others
    file(GLOB VIDUR_LIB_CANDIDATES "${PYTHON_SITE_PACKAGES}/vidur/_native*.so")
endif()

# Select the first matching library
if(VIDUR_LIB_CANDIDATES)
    list(GET VIDUR_LIB_CANDIDATES 0 VIDUR_LIBRARY)
endif()

# Set include directory
set(VIDUR_INCLUDE_DIR "${PYTHON_SITE_PACKAGES}/vidur/include")

# Verify paths exist
if(NOT EXISTS "${VIDUR_LIBRARY}")
    message(STATUS "Vidur library not found at expected location. Checked: ${VIDUR_LIB_CANDIDATES}")
    set(VIDUR_FOUND FALSE)
    return()
endif()

if(NOT EXISTS "${VIDUR_INCLUDE_DIR}")
    # Try to find include files directly in the vidur package if not in the expected subdirectory
    set(VIDUR_INCLUDE_DIR "${PYTHON_SITE_PACKAGES}/vidur")
    if(NOT EXISTS "${VIDUR_INCLUDE_DIR}")
        message(STATUS "Vidur include directory not found at: ${VIDUR_INCLUDE_DIR}")
        set(VIDUR_FOUND FALSE)
        return()
    endif()
endif()

# Set Vidur_FOUND to TRUE
set(VIDUR_FOUND TRUE)

# Create imported target if it doesn't exist
if(NOT TARGET Vidur::Vidur)
    add_library(Vidur::Vidur SHARED IMPORTED)
    set_target_properties(Vidur::Vidur PROPERTIES
        IMPORTED_LOCATION "${VIDUR_LIBRARY}"
        INTERFACE_INCLUDE_DIRECTORIES "${VIDUR_INCLUDE_DIR}"
    )
    # Add dependency on Python
    set_property(TARGET Vidur::Vidur PROPERTY INTERFACE_LINK_LIBRARIES Python3::Python)
endif()

# Standard find_package variables
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Vidur 
    REQUIRED_VARS VIDUR_LIBRARY VIDUR_INCLUDE_DIR
)

mark_as_advanced(VIDUR_INCLUDE_DIR VIDUR_LIBRARY)
