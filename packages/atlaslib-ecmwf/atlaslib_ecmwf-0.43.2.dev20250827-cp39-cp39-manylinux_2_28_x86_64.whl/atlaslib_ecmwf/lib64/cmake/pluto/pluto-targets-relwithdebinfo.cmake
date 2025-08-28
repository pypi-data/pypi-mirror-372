#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pluto" for configuration "RelWithDebInfo"
set_property(TARGET pluto APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(pluto PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib64/libpluto.so"
  IMPORTED_SONAME_RELWITHDEBINFO "libpluto.so"
  )

list(APPEND _cmake_import_check_targets pluto )
list(APPEND _cmake_import_check_files_for_pluto "${_IMPORT_PREFIX}/lib64/libpluto.so" )

# Import target "pluto_f" for configuration "RelWithDebInfo"
set_property(TARGET pluto_f APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(pluto_f PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELWITHDEBINFO "pluto"
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib64/libpluto_f.so"
  IMPORTED_SONAME_RELWITHDEBINFO "libpluto_f.so"
  )

list(APPEND _cmake_import_check_targets pluto_f )
list(APPEND _cmake_import_check_files_for_pluto_f "${_IMPORT_PREFIX}/lib64/libpluto_f.so" )

# Import target "pluto-benchmark" for configuration "RelWithDebInfo"
set_property(TARGET pluto-benchmark APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(pluto-benchmark PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/pluto-benchmark"
  )

list(APPEND _cmake_import_check_targets pluto-benchmark )
list(APPEND _cmake_import_check_files_for_pluto-benchmark "${_IMPORT_PREFIX}/bin/pluto-benchmark" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
