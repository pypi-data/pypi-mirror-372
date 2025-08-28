# Config file for the atlas package
# Defines the following variables:
#
#  atlas_FEATURES       - list of enabled features
#  atlas_VERSION        - version of the package
#  atlas_GIT_SHA1       - Git revision of the package
#  atlas_GIT_SHA1_SHORT - short Git revision of the package
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
set_and_check(atlas_CMAKE_DIR "${PACKAGE_PREFIX_DIR}/lib64/cmake/atlas")
set_and_check(atlas_BASE_DIR "${PACKAGE_PREFIX_DIR}/.")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ATLAS_CMAKE_DIR ${atlas_CMAKE_DIR})
  set(ATLAS_BASE_DIR ${atlas_BASE_DIR})
endif()

### export version info
set(atlas_VERSION           "0.43.2")
set(atlas_GIT_SHA1          "5c1f57eeaa5af5dc5228ad2456ee7c4a4afbba6f")
set(atlas_GIT_SHA1_SHORT    "5c1f57e")

if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ATLAS_VERSION           "0.43.2" )
  set(ATLAS_GIT_SHA1          "5c1f57eeaa5af5dc5228ad2456ee7c4a4afbba6f" )
  set(ATLAS_GIT_SHA1_SHORT    "5c1f57e" )
endif()

### has this configuration been exported from a build tree?
set(atlas_IS_BUILD_DIR_EXPORT OFF)
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ATLAS_IS_BUILD_DIR_EXPORT ${atlas_IS_BUILD_DIR_EXPORT})
endif()

### include the <project>-import.cmake file if there is one
if(EXISTS ${atlas_CMAKE_DIR}/atlas-import.cmake)
  set(atlas_IMPORT_FILE "${atlas_CMAKE_DIR}/atlas-import.cmake")
  include(${atlas_IMPORT_FILE})
endif()

### insert definitions for IMPORTED targets
if(NOT atlas_BINARY_DIR)
  find_file(atlas_TARGETS_FILE
    NAMES atlas-targets.cmake
    HINTS ${atlas_CMAKE_DIR}
    NO_DEFAULT_PATH)
  if(atlas_TARGETS_FILE)
    include(${atlas_TARGETS_FILE})
  endif()
endif()

### include the <project>-post-import.cmake file if there is one
if(EXISTS ${atlas_CMAKE_DIR}/atlas-post-import.cmake)
  set(atlas_POST_IMPORT_FILE "${atlas_CMAKE_DIR}/atlas-post-import.cmake")
  include(${atlas_POST_IMPORT_FILE})
endif()

### handle third-party dependencies
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ATLAS_LIBRARIES         "")
  set(ATLAS_TPLS              "" )

  include(${CMAKE_CURRENT_LIST_FILE}.tpls OPTIONAL)
endif()

### publish this file as imported
if( DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT )
  set(atlas_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(atlas_IMPORT_FILE)
  set(ATLAS_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(ATLAS_IMPORT_FILE)
endif()

### export features and check requirements
set(atlas_FEATURES "TESTS;PKGCONFIG;ECKIT_CODEC;WARNINGS;ATLAS_GRID;ATLAS_FIELD;ATLAS_FUNCTIONSPACE;ATLAS_INTERPOLATION;ATLAS_TRANS;ATLAS_NUMERICS;OMP;OMP_CXX;TESSELATION;ATLAS_RUN;PKGCONFIG")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ATLAS_FEATURES ${atlas_FEATURES})
endif()
foreach(_f ${atlas_FEATURES})
  set(atlas_${_f}_FOUND 1)
  set(atlas_HAVE_${_f} 1)
  if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
    set(ATLAS_HAVE_${_f} 1)
  endif()
endforeach()
check_required_components(atlas)
