
include( CMakeFindDependencyMacro )

set( atlas_HAVE_MPI                          0 )
set( atlas_HAVE_OMP                          True )
set( atlas_HAVE_OMP_CXX                      True )
set( atlas_HAVE_OMP_Fortran                  0 )
set( atlas_HAVE_ECTRANS                      0 )
set( atlas_HAVE_FORTRAN                      0 )
set( atlas_HAVE_EIGEN                        0 )
set( atlas_HAVE_GRIDTOOLS_STORAGE            0 )
set( atlas_HAVE_TESSELATION                  True )
set( ATLAS_LIBRARIES                         atlas )
set( atlas_VERSION_STR                       0.43.2.dev20250827 )
set( atlas_REQUIRES_PRIVATE_DEPENDENCIES     FALSE )

## eckit
find_dependency( eckit HINTS ${CMAKE_CURRENT_LIST_DIR}/../eckit /tmp/atlas/prereqs/eckitlib/lib64/cmake/eckit  )

## fckit
if( atlas_HAVE_FORTRAN )
  find_dependency( fckit HINTS ${CMAKE_CURRENT_LIST_DIR}/../fckit fckit_DIR-NOTFOUND  )
endif()

find_dependency( atlas_io HINTS ${CMAKE_CURRENT_LIST_DIR}/../atlas_io /tmp/atlas/build/atlas_io /tmp/atlas/build/atlas_io )
find_dependency( hic HINTS ${CMAKE_CURRENT_LIST_DIR}/../hic /tmp/atlas/build/hic /tmp/atlas/build/hic )
find_dependency( pluto HINTS ${CMAKE_CURRENT_LIST_DIR}/../pluto /tmp/atlas/build/pluto /tmp/atlas/build/pluto )

## Eigen3
set( Eigen3_HINT Eigen3_DIR-NOTFOUND )
if( atlas_HAVE_EIGEN AND Eigen3_HINT )
  find_dependency( Eigen3 HINTS ${Eigen3_HINT} )
endif()

## gridtools_storage
if( atlas_HAVE_GRIDTOOLS_STORAGE )
  # Required for GridTools' find_package( MPI COMPONENTS CXX )
  if( NOT CMAKE_CXX_COMPILER_LOADED )
    enable_language( CXX )
  endif()
  find_dependency( GridTools HINTS
        ${GridTools_ROOT}/lib/cmake       # non-standard install (reported upstream)
        $ENV{GridTools_ROOT}/lib/cmake    # non-standard install (reported upstream)
        ${CMAKE_CURRENT_LIST_DIR}/..      # non-standard install (reported upstream)
        ${CMAKE_PREFIX_PATH}/lib/cmake    # non-standard install (reported upstream)
        ${CMAKE_INSTALL_PREFIX}/lib/cmake # non-standard install (reported upstream)
        ${CMAKE_CURRENT_LIST_DIR}/../gridtools
        
         )
endif()

## OpenMP
unset( atlas_OMP_COMPONENTS )
if( atlas_HAVE_OMP_Fortran AND 
    CMAKE_Fortran_COMPILER_LOADED AND
    atlas_REQUIRES_PRIVATE_DEPENDENCIES )
  list( APPEND atlas_OMP_COMPONENTS Fortran )
endif()
if( atlas_HAVE_OMP_CXX )
  if( NOT CMAKE_CXX_COMPILER_LOADED )
    enable_language( CXX )
  endif()
  list( APPEND atlas_OMP_COMPONENTS CXX )
endif()
if( atlas_OMP_COMPONENTS )
  find_dependency( OpenMP COMPONENTS ${atlas_OMP_COMPONENTS} )
endif()

## transi
if( atlas_HAVE_ECTRANS AND atlas_REQUIRES_PRIVATE_DEPENDENCIES )
    set( transi_DIR transi_DIR-NOTFOUND )
    if( transi_DIR )
        find_dependency( transi HINTS ${CMAKE_CURRENT_LIST_DIR}/../transi transi_DIR-NOTFOUND )
    else()
        find_dependency( ectrans COMPONENTS transi double HINTS ${CMAKE_CURRENT_LIST_DIR}/../ectrans ectrans_DIR-NOTFOUND )
    endif()
endif()

## Qhull
if( atlas_HAVE_TESSELATION AND atlas_REQUIRES_PRIVATE_DEPENDENCIES )
    find_dependency( Qhull HINTS /tmp/qhull/target/lib64/cmake/Qhull )
endif()

## Fortran
set( atlas_FORTRAN_FOUND 0 )
if( atlas_HAVE_FORTRAN )
  set( atlas_FORTRAN_FOUND 1 )
elseif( atlas_FIND_REQUIRED_FORTRAN )
  message( FATAL_ERROR "atlas was not compiled with FORTRAN enabled" )
endif()

set( atlas_DIR ${CMAKE_CURRENT_LIST_DIR} CACHE STRING "" )


function( atlas_create_plugin name )

  set( options )
  set( single_value_args VERSION LIBRARY URL NAMESPACE)
  set( multi_value_args )
  cmake_parse_arguments( _PAR "${options}" "${single_value_args}" "${multi_value_args}"  ${_FIRST_ARG} ${ARGN} )

  set( _plugin_file share/plugins/${name}.yml )

  if( NOT DEFINED _PAR_VERSION )
    set( _version ${${PROJECT_NAME}_VERSION} )
  else()
    set( _version ${_PAR_VERSION} )
  endif()
  if( NOT DEFINED _PAR_LIBRARY )
    set( _library "${name}" )
  else()
    set( _library "${_PAR_LIBRARY}" )
  endif()
  if( NOT DEFINED _PAR_URL )
      set( _url "http://www.ecmwf.int" )
  else()
      set( _url ${_PAR_URL} )
  endif()
  if( NOT DEFINED _PAR_NAMESPACE )
      set( _namespace "int.ecmwf" )
  else()
      set( _namespace ${_PAR_NAMESPACE} )
  endif()

  file( WRITE  ${CMAKE_BINARY_DIR}/${_plugin_file} "plugin:\n" )
  file( APPEND ${CMAKE_BINARY_DIR}/${_plugin_file} "  name:      ${name}\n" )
  file( APPEND ${CMAKE_BINARY_DIR}/${_plugin_file} "  namespace: ${_namespace}\n" )
  file( APPEND ${CMAKE_BINARY_DIR}/${_plugin_file} "  url:       ${_url}\n" )
  file( APPEND ${CMAKE_BINARY_DIR}/${_plugin_file} "  version:   ${_version}\n" )
  file( APPEND ${CMAKE_BINARY_DIR}/${_plugin_file} "  library:   ${_library}\n" )

  install( FILES ${CMAKE_BINARY_DIR}/${_plugin_file} DESTINATION share/plugins )
endfunction()
