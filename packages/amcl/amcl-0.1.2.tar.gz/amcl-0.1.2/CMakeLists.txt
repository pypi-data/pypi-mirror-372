cmake_minimum_required(VERSION 3.15...3.27)
project(amcl_python VERSION 0.1.2 LANGUAGES CXX C)

# Set C++ standard to C++17 (required for modern C++ features)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Enable position independent code for all targets
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

include(CheckSymbolExists)
check_symbol_exists(drand48 stdlib.h HAVE_DRAND48)

add_library(
  amcl
  src/amcl.cpp
  src/map/map.c
  src/map/map_cspace.cpp
  src/map/map_range.c
  src/motion_model/differential_motion_model.cpp
  src/motion_model/omni_motion_model.cpp
  src/pf/eig3.c
  src/pf/pf.c
  src/pf/pf_draw.c
  src/pf/pf_kdtree.c
  src/pf/pf_pdf.c
  src/pf/pf_vector.c
  src/sensors/laser/beam_model.cpp
  src/sensors/laser/laser.cpp
  src/sensors/laser/likelihood_field_model.cpp
  src/sensors/laser/likelihood_field_model_prob.cpp)

target_include_directories(
  amcl
  PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include)

if(HAVE_DRAND48)
  target_compile_definitions(amcl PRIVATE "HAVE_DRAND48")
endif()

# Warn if the user invokes CMake directly
if (NOT SKBUILD)
  message(WARNING "\
  This CMake file is meant to be executed using 'scikit-build-core'.
  Running it directly will almost certainly not produce the desired
  result. If you are a user trying to install this package, use the
  command below, which will install all necessary build dependencies,
  compile the package in an isolated environment, and then install it.
  =====================================================================
   $ pip install .
  =====================================================================
  If you are a software developer, and this is your own package, then
  it is usually much more efficient to install the build dependencies
  in your environment once and use the following command that avoids
  a costly creation of a new virtual environment at every compilation:
  =====================================================================
   $ pip install nanobind scikit-build-core[pyproject]
   $ pip install --no-build-isolation -ve .
  =====================================================================
  You may optionally add -Ceditable.rebuild=true to auto-rebuild when
  the package is imported. Otherwise, you need to rerun the above
  after editing C++ files.")
endif()

add_executable(
  amcl_example
  src/main.cpp)

target_link_libraries(
  amcl_example
  amcl)

if (CMAKE_VERSION VERSION_LESS 3.18)
  set(DEV_MODULE Development)
else()
  set(DEV_MODULE Development.Module)
endif()

find_package(Python "3.8...<3.14"
  REQUIRED COMPONENTS Interpreter Development.Module
  OPTIONAL_COMPONENTS Development.SABIModule)

if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

if (Python_VERSION VERSION_GREATER_EQUAL "3.12")
  message(STATUS "Building with stable ABI (Python ${Python_VERSION} >= 3.12)")
  set(ABI_FLAG STABLE_ABI)
else()
  message(STATUS "Building without stable ABI (Python ${Python_VERSION} < 3.12)")
  set(ABI_FLAG "")
endif()

execute_process(
  COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE nanobind_ROOT)
find_package(nanobind CONFIG REQUIRED)

if (nanobind_FOUND)
  message(STATUS "Found nanobind: ${nanobind_VERSION}")
  message(STATUS "Python version: ${Python_VERSION}")
  
  message(STATUS "Building with stable ABI (Python ${Python_VERSION} >= 3.12)")
  nanobind_add_module(
    _amcl_impl
    ${ABI_FLAG}
    NB_STATIC
    src/python_bindings.cpp
  )
  
  # Ensure C++17 for the Python bindings
  set_target_properties(_amcl_impl PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
  )
  
  target_link_libraries(_amcl_impl PRIVATE amcl)
  
  install(TARGETS _amcl_impl
    LIBRARY DESTINATION amcl
  )
  
  message(STATUS "Python bindings will be built")
else()
  message(WARNING "nanobind not found - Python bindings will not be built")
  message(STATUS "To install nanobind: pip install nanobind")
endif()
