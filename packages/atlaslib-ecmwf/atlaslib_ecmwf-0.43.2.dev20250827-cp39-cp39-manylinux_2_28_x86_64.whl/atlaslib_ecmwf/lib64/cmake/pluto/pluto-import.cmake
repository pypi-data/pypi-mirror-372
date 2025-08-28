
include( CMakeFindDependencyMacro )

set( pluto_HAVE_CUDA 0 )
set( pluto_HAVE_HIP  0 )

find_dependency( hic HINTS ${CMAKE_CURRENT_LIST_DIR}/../hic /tmp/atlas/build/hic /tmp/atlas/build/hic )

