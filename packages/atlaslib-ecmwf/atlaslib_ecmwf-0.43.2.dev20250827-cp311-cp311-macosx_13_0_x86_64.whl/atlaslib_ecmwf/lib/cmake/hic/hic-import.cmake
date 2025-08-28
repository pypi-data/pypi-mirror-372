
include( CMakeFindDependencyMacro )

set( hic_HAVE_CUDA 0 )
set( hic_HAVE_HIP  0 )

if( hic_HAVE_CUDA )
  find_dependency( CUDAToolkit )
endif()
if( hic_HAVE_HIP )
  find_dependency( hip CONFIG )
endif()

