#if 0
/*
 * (C) Copyright 2013 ECMWF.
 *
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
 * In applying this licence, ECMWF does not waive the privileges and immunities
 * granted to it by virtue of its status as an intergovernmental organisation
 * nor does it submit to any jurisdiction.
 */
// clang-format off
#endif

#ifndef atlas_library_defines_h
#define atlas_library_defines_h

#define ATLAS_HAVE_OMP                       0
#define ATLAS_OMP_TASK_SUPPORTED             0
#define ATLAS_OMP_TASK_UNTIED_SUPPORTED      0
#define ATLAS_HAVE_GPU                       0
#define ATLAS_HAVE_ACC                       0
#define ATLAS_HAVE_QHULL                     1
#define ATLAS_HAVE_CGAL                      0
#define ATLAS_HAVE_TESSELATION               1
#define ATLAS_HAVE_FORTRAN                   0
#define ATLAS_HAVE_EIGEN                     1
#define ATLAS_HAVE_FFTW                      1
#define ATLAS_HAVE_MPI                       0
#define ATLAS_HAVE_PROJ                      0
#define ATLAS_BITS_GLOBAL                    64
#define ATLAS_ARRAYVIEW_BOUNDS_CHECKING      0
#define ATLAS_INDEXVIEW_BOUNDS_CHECKING      0
#define ATLAS_VECTOR_BOUNDS_CHECKING         0
#define ATLAS_INIT_SNAN                      0
#define ATLAS_HAVE_GRIDTOOLS_STORAGE         0
#define ATLAS_GRIDTOOLS_STORAGE_BACKEND_HOST 0
#define ATLAS_GRIDTOOLS_STORAGE_BACKEND_CUDA 0
#define ATLAS_HAVE_TRANS                     0
#define ATLAS_HAVE_ECTRANS                   0
#define ATLAS_HAVE_FEENABLEEXCEPT            0
#define ATLAS_HAVE_FEDISABLEEXCEPT           0
#define ATLAS_BUILD_TYPE_DEBUG               0
#define ATLAS_BUILD_TYPE_RELEASE             0
#define ATLAS_ECKIT_VERSION_INT              13105
#define ATLAS_ECKIT_DEVELOP                  0
#define ATLAS_HAVE_FUNCTIONSPACE             1

#define ATLAS_BITS_LOCAL 32

#if defined( __GNUC__ ) || defined( __clang__ )
#define ATLAS_MAYBE_UNUSED __attribute__( ( unused ) )
#define ATLAS_ALWAYS_INLINE __attribute__( ( always_inline ) ) inline
#else
#define ATLAS_MAYBE_UNUSED
#define ATLAS_ALWAYS_INLINE inline
#endif

#define ATLAS_UNREACHABLE() __builtin_unreachable()

#if defined(__NVCOMPILER)
#    define ATLAS_SUPPRESS_WARNINGS_PUSH                 _Pragma( "diag push" )
#    define ATLAS_SUPPRESS_WARNINGS_POP                  _Pragma( "diag pop" )
#    define ATLAS_SUPPRESS_WARNINGS_INTEGER_SIGN_CHANGE  _Pragma( "diag_suppress integer_sign_change" )
#    define ATLAS_SUPPRESS_WARNINGS_CODE_IS_UNREACHABLE  _Pragma( "diag_suppress code_is_unreachable" )
#elif defined(__INTEL_LLVM_COMPILER)
#    define ATLAS_SUPPRESS_WARNINGS_PUSH                      _Pragma( "clang diagnostic push")
#    define ATLAS_SUPPRESS_WARNINGS_POP                       _Pragma( "clang diagnostic pop" )
#    define ATLAS_SUPPRESS_WARNINGS_UNUSED_BUT_SET_VARIABLE   _Pragma( "clang diagnostic ignored \"-Wunused-but-set-variable\"")
#elif defined(__INTEL_COMPILER)
#    define ATLAS_SUPPRESS_WARNINGS_PUSH                 _Pragma( "warning push" )
#    define ATLAS_SUPPRESS_WARNINGS_POP                  _Pragma( "warning pop" )
#    define ATLAS_SUPPRESS_WARNINGS_INTEGER_SIGN_CHANGE  _Pragma( "warning disable 68" )
#    define ATLAS_SUPPRESS_WARNINGS_BOTH_INLINE_NOINLINE _Pragma( "warning disable 2196" )
#elif defined(__GNUC__)
#    define ATLAS_SUPPRESS_WARNINGS_PUSH                 _Pragma( "GCC diagnostic push" ) \
                                                         _Pragma( "GCC diagnostic ignored \"-Wpragmas\"" ) \
                                                         _Pragma( "GCC diagnostic ignored \"-Wunknown-warning-option\"" )
#    define ATLAS_SUPPRESS_WARNINGS_POP                  _Pragma( "GCC diagnostic pop" )
#    define ATLAS_SUPPRESS_WARNINGS_TEMPLATE_ID_CDTOR    _Pragma( "GCC diagnostic ignored \"-Wtemplate-id-cdtor\"" )
#endif


#if !defined(ATLAS_SUPPRESS_WARNINGS_PUSH)
#    define ATLAS_SUPPRESS_WARNINGS_PUSH
#endif
#if !defined(ATLAS_SUPPRESS_WARNINGS_POP)
#    define ATLAS_SUPPRESS_WARNINGS_POP
#endif
#if !defined(ATLAS_SUPPRESS_WARNINGS_INTEGER_SIGN_CHANGE)
#    define ATLAS_SUPPRESS_WARNINGS_INTEGER_SIGN_CHANGE
#endif
#if !defined(ATLAS_SUPPRESS_WARNINGS_CODE_IS_UNREACHABLE)
#    define ATLAS_SUPPRESS_WARNINGS_CODE_IS_UNREACHABLE
#endif
#if !defined(ATLAS_SUPPRESS_WARNINGS_TEMPLATE_ID_CDTOR)
#    define ATLAS_SUPPRESS_WARNINGS_TEMPLATE_ID_CDTOR
#endif
#if !defined(ATLAS_SUPPRESS_WARNINGS_UNUSED_BUT_SET_VARIABLE)
#    define ATLAS_SUPPRESS_WARNINGS_UNUSED_BUT_SET_VARIABLE
#endif
#if !defined(ATLAS_SUPPRESS_WARNINGS_BOTH_INLINE_NOINLINE)
#    define ATLAS_SUPPRESS_WARNINGS_BOTH_INLINE_NOINLINE
#endif

#endif

