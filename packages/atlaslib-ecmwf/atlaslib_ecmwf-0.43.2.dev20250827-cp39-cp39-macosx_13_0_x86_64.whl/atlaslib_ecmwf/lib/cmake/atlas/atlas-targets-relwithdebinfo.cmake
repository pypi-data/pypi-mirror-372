#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "atlas" for configuration "RelWithDebInfo"
set_property(TARGET atlas APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(atlas PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELWITHDEBINFO "Qhull::qhull_r"
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libatlas.0.43.dylib"
  IMPORTED_SONAME_RELWITHDEBINFO "@rpath/libatlas.0.43.dylib"
  )

list(APPEND _cmake_import_check_targets atlas )
list(APPEND _cmake_import_check_files_for_atlas "${_IMPORT_PREFIX}/lib/libatlas.0.43.dylib" )

# Import target "atlas-main" for configuration "RelWithDebInfo"
set_property(TARGET atlas-main APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(atlas-main PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/atlas"
  )

list(APPEND _cmake_import_check_targets atlas-main )
list(APPEND _cmake_import_check_files_for_atlas-main "${_IMPORT_PREFIX}/bin/atlas" )

# Import target "atlas-meshgen" for configuration "RelWithDebInfo"
set_property(TARGET atlas-meshgen APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(atlas-meshgen PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/atlas-meshgen"
  )

list(APPEND _cmake_import_check_targets atlas-meshgen )
list(APPEND _cmake_import_check_files_for_atlas-meshgen "${_IMPORT_PREFIX}/bin/atlas-meshgen" )

# Import target "atlas-grids" for configuration "RelWithDebInfo"
set_property(TARGET atlas-grids APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(atlas-grids PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/atlas-grids"
  )

list(APPEND _cmake_import_check_targets atlas-grids )
list(APPEND _cmake_import_check_files_for_atlas-grids "${_IMPORT_PREFIX}/bin/atlas-grids" )

# Import target "atlas-grid-points" for configuration "RelWithDebInfo"
set_property(TARGET atlas-grid-points APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(atlas-grid-points PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/atlas-grid-points"
  )

list(APPEND _cmake_import_check_targets atlas-grid-points )
list(APPEND _cmake_import_check_files_for_atlas-grid-points "${_IMPORT_PREFIX}/bin/atlas-grid-points" )

# Import target "atlas-gaussian-latitudes" for configuration "RelWithDebInfo"
set_property(TARGET atlas-gaussian-latitudes APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(atlas-gaussian-latitudes PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/atlas-gaussian-latitudes"
  )

list(APPEND _cmake_import_check_targets atlas-gaussian-latitudes )
list(APPEND _cmake_import_check_files_for_atlas-gaussian-latitudes "${_IMPORT_PREFIX}/bin/atlas-gaussian-latitudes" )

# Import target "atlas-atest-mgrids" for configuration "RelWithDebInfo"
set_property(TARGET atlas-atest-mgrids APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(atlas-atest-mgrids PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/atlas-atest-mgrids"
  )

list(APPEND _cmake_import_check_targets atlas-atest-mgrids )
list(APPEND _cmake_import_check_files_for_atlas-atest-mgrids "${_IMPORT_PREFIX}/bin/atlas-atest-mgrids" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
