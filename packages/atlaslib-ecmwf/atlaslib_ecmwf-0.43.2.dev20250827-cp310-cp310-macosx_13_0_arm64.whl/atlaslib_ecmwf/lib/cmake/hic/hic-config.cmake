# Config file for the hic package
# Defines the following variables:
#
#  hic_FEATURES       - list of enabled features
#  hic_VERSION        - version of the package
#  hic_GIT_SHA1       - Git revision of the package
#  hic_GIT_SHA1_SHORT - short Git revision of the package
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
set_and_check(hic_CMAKE_DIR "${PACKAGE_PREFIX_DIR}/lib/cmake/hic")
set_and_check(hic_BASE_DIR "${PACKAGE_PREFIX_DIR}/.")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(HIC_CMAKE_DIR ${hic_CMAKE_DIR})
  set(HIC_BASE_DIR ${hic_BASE_DIR})
endif()

### export version info
set(hic_VERSION           "0.43.2")
set(hic_GIT_SHA1          "")
set(hic_GIT_SHA1_SHORT    "")

if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(HIC_VERSION           "0.43.2" )
  set(HIC_GIT_SHA1          "" )
  set(HIC_GIT_SHA1_SHORT    "" )
endif()

### has this configuration been exported from a build tree?
set(hic_IS_BUILD_DIR_EXPORT OFF)
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(HIC_IS_BUILD_DIR_EXPORT ${hic_IS_BUILD_DIR_EXPORT})
endif()

### include the <project>-import.cmake file if there is one
if(EXISTS ${hic_CMAKE_DIR}/hic-import.cmake)
  set(hic_IMPORT_FILE "${hic_CMAKE_DIR}/hic-import.cmake")
  include(${hic_IMPORT_FILE})
endif()

### insert definitions for IMPORTED targets
if(NOT hic_BINARY_DIR)
  find_file(hic_TARGETS_FILE
    NAMES hic-targets.cmake
    HINTS ${hic_CMAKE_DIR}
    NO_DEFAULT_PATH)
  if(hic_TARGETS_FILE)
    include(${hic_TARGETS_FILE})
  endif()
endif()

### include the <project>-post-import.cmake file if there is one
if(EXISTS ${hic_CMAKE_DIR}/hic-post-import.cmake)
  set(hic_POST_IMPORT_FILE "${hic_CMAKE_DIR}/hic-post-import.cmake")
  include(${hic_POST_IMPORT_FILE})
endif()

### handle third-party dependencies
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(HIC_LIBRARIES         "")
  set(HIC_TPLS              "" )

  include(${CMAKE_CURRENT_LIST_FILE}.tpls OPTIONAL)
endif()

### publish this file as imported
if( DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT )
  set(hic_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(hic_IMPORT_FILE)
  set(HIC_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(HIC_IMPORT_FILE)
endif()

### export features and check requirements
set(hic_FEATURES "TESTS;PKGCONFIG;ECKIT_CODEC;WARNINGS;ATLAS_GRID;ATLAS_FIELD;ATLAS_FUNCTIONSPACE;ATLAS_INTERPOLATION;ATLAS_TRANS;ATLAS_NUMERICS;WARNINGS")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(HIC_FEATURES ${hic_FEATURES})
endif()
foreach(_f ${hic_FEATURES})
  set(hic_${_f}_FOUND 1)
  set(hic_HAVE_${_f} 1)
  if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
    set(HIC_HAVE_${_f} 1)
  endif()
endforeach()
check_required_components(hic)
