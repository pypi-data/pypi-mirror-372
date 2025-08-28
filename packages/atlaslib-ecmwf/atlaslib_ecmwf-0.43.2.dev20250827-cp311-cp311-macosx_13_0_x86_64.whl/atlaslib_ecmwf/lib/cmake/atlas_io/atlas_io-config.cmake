# Config file for the atlas_io package
# Defines the following variables:
#
#  atlas_io_FEATURES       - list of enabled features
#  atlas_io_VERSION        - version of the package
#  atlas_io_GIT_SHA1       - Git revision of the package
#  atlas_io_GIT_SHA1_SHORT - short Git revision of the package
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
set_and_check(atlas_io_CMAKE_DIR "${PACKAGE_PREFIX_DIR}/lib/cmake/atlas_io")
set_and_check(atlas_io_BASE_DIR "${PACKAGE_PREFIX_DIR}/.")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ATLAS_IO_CMAKE_DIR ${atlas_io_CMAKE_DIR})
  set(ATLAS_IO_BASE_DIR ${atlas_io_BASE_DIR})
endif()

### export version info
set(atlas_io_VERSION           "0.43.2")
set(atlas_io_GIT_SHA1          "")
set(atlas_io_GIT_SHA1_SHORT    "")

if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ATLAS_IO_VERSION           "0.43.2" )
  set(ATLAS_IO_GIT_SHA1          "" )
  set(ATLAS_IO_GIT_SHA1_SHORT    "" )
endif()

### has this configuration been exported from a build tree?
set(atlas_io_IS_BUILD_DIR_EXPORT OFF)
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ATLAS_IO_IS_BUILD_DIR_EXPORT ${atlas_io_IS_BUILD_DIR_EXPORT})
endif()

### include the <project>-import.cmake file if there is one
if(EXISTS ${atlas_io_CMAKE_DIR}/atlas_io-import.cmake)
  set(atlas_io_IMPORT_FILE "${atlas_io_CMAKE_DIR}/atlas_io-import.cmake")
  include(${atlas_io_IMPORT_FILE})
endif()

### insert definitions for IMPORTED targets
if(NOT atlas_io_BINARY_DIR)
  find_file(atlas_io_TARGETS_FILE
    NAMES atlas_io-targets.cmake
    HINTS ${atlas_io_CMAKE_DIR}
    NO_DEFAULT_PATH)
  if(atlas_io_TARGETS_FILE)
    include(${atlas_io_TARGETS_FILE})
  endif()
endif()

### include the <project>-post-import.cmake file if there is one
if(EXISTS ${atlas_io_CMAKE_DIR}/atlas_io-post-import.cmake)
  set(atlas_io_POST_IMPORT_FILE "${atlas_io_CMAKE_DIR}/atlas_io-post-import.cmake")
  include(${atlas_io_POST_IMPORT_FILE})
endif()

### handle third-party dependencies
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ATLAS_IO_LIBRARIES         "")
  set(ATLAS_IO_TPLS              "" )

  include(${CMAKE_CURRENT_LIST_FILE}.tpls OPTIONAL)
endif()

### publish this file as imported
if( DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT )
  set(atlas_io_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(atlas_io_IMPORT_FILE)
  set(ATLAS_IO_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(ATLAS_IO_IMPORT_FILE)
endif()

### export features and check requirements
set(atlas_io_FEATURES "TESTS;PKGCONFIG;ECKIT_CODEC;WARNINGS;WARNINGS")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ATLAS_IO_FEATURES ${atlas_io_FEATURES})
endif()
foreach(_f ${atlas_io_FEATURES})
  set(atlas_io_${_f}_FOUND 1)
  set(atlas_io_HAVE_${_f} 1)
  if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
    set(ATLAS_IO_HAVE_${_f} 1)
  endif()
endforeach()
check_required_components(atlas_io)
