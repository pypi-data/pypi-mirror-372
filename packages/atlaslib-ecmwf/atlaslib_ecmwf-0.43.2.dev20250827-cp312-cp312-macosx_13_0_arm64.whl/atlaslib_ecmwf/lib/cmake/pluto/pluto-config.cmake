# Config file for the pluto package
# Defines the following variables:
#
#  pluto_FEATURES       - list of enabled features
#  pluto_VERSION        - version of the package
#  pluto_GIT_SHA1       - Git revision of the package
#  pluto_GIT_SHA1_SHORT - short Git revision of the package
#


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was project-config.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

### computed paths
set_and_check(pluto_CMAKE_DIR "${PACKAGE_PREFIX_DIR}/lib/cmake/pluto")
set_and_check(pluto_BASE_DIR "${PACKAGE_PREFIX_DIR}/.")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(PLUTO_CMAKE_DIR ${pluto_CMAKE_DIR})
  set(PLUTO_BASE_DIR ${pluto_BASE_DIR})
endif()

### export version info
set(pluto_VERSION           "0.43.2")
set(pluto_GIT_SHA1          "")
set(pluto_GIT_SHA1_SHORT    "")

if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(PLUTO_VERSION           "0.43.2" )
  set(PLUTO_GIT_SHA1          "" )
  set(PLUTO_GIT_SHA1_SHORT    "" )
endif()

### has this configuration been exported from a build tree?
set(pluto_IS_BUILD_DIR_EXPORT OFF)
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(PLUTO_IS_BUILD_DIR_EXPORT ${pluto_IS_BUILD_DIR_EXPORT})
endif()

### include the <project>-import.cmake file if there is one
if(EXISTS ${pluto_CMAKE_DIR}/pluto-import.cmake)
  set(pluto_IMPORT_FILE "${pluto_CMAKE_DIR}/pluto-import.cmake")
  include(${pluto_IMPORT_FILE})
endif()

### insert definitions for IMPORTED targets
if(NOT pluto_BINARY_DIR)
  find_file(pluto_TARGETS_FILE
    NAMES pluto-targets.cmake
    HINTS ${pluto_CMAKE_DIR}
    NO_DEFAULT_PATH)
  if(pluto_TARGETS_FILE)
    include(${pluto_TARGETS_FILE})
  endif()
endif()

### include the <project>-post-import.cmake file if there is one
if(EXISTS ${pluto_CMAKE_DIR}/pluto-post-import.cmake)
  set(pluto_POST_IMPORT_FILE "${pluto_CMAKE_DIR}/pluto-post-import.cmake")
  include(${pluto_POST_IMPORT_FILE})
endif()

### handle third-party dependencies
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(PLUTO_LIBRARIES         "")
  set(PLUTO_TPLS              "" )

  include(${CMAKE_CURRENT_LIST_FILE}.tpls OPTIONAL)
endif()

### publish this file as imported
if( DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT )
  set(pluto_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(pluto_IMPORT_FILE)
  set(PLUTO_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(PLUTO_IMPORT_FILE)
endif()

### export features and check requirements
set(pluto_FEATURES "TESTS;PKGCONFIG;ECKIT_CODEC;WARNINGS;ATLAS_GRID;ATLAS_FIELD;ATLAS_FUNCTIONSPACE;ATLAS_INTERPOLATION;ATLAS_TRANS;ATLAS_NUMERICS;FORTRAN;FORTRAN")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(PLUTO_FEATURES ${pluto_FEATURES})
endif()
foreach(_f ${pluto_FEATURES})
  set(pluto_${_f}_FOUND 1)
  set(pluto_HAVE_${_f} 1)
  if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
    set(PLUTO_HAVE_${_f} 1)
  endif()
endforeach()
check_required_components(pluto)
