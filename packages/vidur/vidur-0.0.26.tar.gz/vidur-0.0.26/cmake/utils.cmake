# Find Python from executable
macro(find_python_from_executable EXECUTABLE SUPPORTED_VERSIONS)
  file(REAL_PATH ${EXECUTABLE} EXECUTABLE)
  set(Python_EXECUTABLE ${EXECUTABLE})
  find_package(Python COMPONENTS Interpreter Development.Module)
  if (NOT Python_FOUND)
    message(FATAL_ERROR "Unable to find python matching: ${EXECUTABLE}.")
  endif()
  set(_VER "${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}")
  set(_SUPPORTED_VERSIONS_LIST ${SUPPORTED_VERSIONS} ${ARGN})
  if (NOT _VER IN_LIST _SUPPORTED_VERSIONS_LIST)
    message(FATAL_ERROR
      "Python version (${_VER}) is not one of the supported versions: "
      "${_SUPPORTED_VERSIONS_LIST}.")
  endif()
  message(STATUS "Found python matching: ${EXECUTABLE}.")
endmacro()

# Run Python command and get output
function(run_python OUT EXPR ERR_MSG)
  execute_process(
    COMMAND
    "${Python_EXECUTABLE}" "-c" "${EXPR}"
    OUTPUT_VARIABLE PYTHON_OUT
    RESULT_VARIABLE PYTHON_ERROR_CODE
    ERROR_VARIABLE PYTHON_STDERR
    OUTPUT_STRIP_TRAILING_WHITESPACE)

  if(NOT PYTHON_ERROR_CODE EQUAL 0)
    message(FATAL_ERROR "${ERR_MSG}: ${PYTHON_STDERR}")
  endif()
  set(${OUT} ${PYTHON_OUT} PARENT_SCOPE)
endfunction()

# Append path to CMAKE_PREFIX_PATH
macro(append_cmake_prefix_path PKG EXPR)
  run_python(_PREFIX_PATH
    "import ${PKG}; print(${EXPR})" "Failed to locate ${PKG} path")
  list(APPEND CMAKE_PREFIX_PATH ${_PREFIX_PATH})
endmacro()
