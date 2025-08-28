/*
 * (C) Copyright 2011- ECMWF.
 *
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
 * In applying this licence, ECMWF does not waive the privileges and immunities
 * granted to it by virtue of its status as an intergovernmental organisation nor
 * does it submit to any jurisdiction.
 */

#ifndef ATLAS_ecbuild_config_h
#define ATLAS_ecbuild_config_h

/* ecbuild info */

#ifndef ECBUILD_VERSION_STR
#define ECBUILD_VERSION_STR "3.11.0"
#endif
#ifndef ECBUILD_VERSION
#define ECBUILD_VERSION "3.11.0"
#endif
#ifndef ECBUILD_MACROS_DIR
#define ECBUILD_MACROS_DIR  "/opt/actions-runner/work/_work/python-develop-bundle/python-develop-bundle/ecbuild/cmake"
#endif

/* config info */

#define ATLAS_OS_NAME          "Darwin-22.5.0"
#define ATLAS_OS_BITS          64
#define ATLAS_OS_BITS_STR      "64"
#define ATLAS_OS_STR           "macosx.64"
#define ATLAS_OS_VERSION       "22.5.0"
#define ATLAS_SYS_PROCESSOR    "arm64"

#define ATLAS_BUILD_TIMESTAMP  "20250827154735"
#define ATLAS_BUILD_TYPE       "RelWithDebInfo"

#define ATLAS_C_COMPILER_ID      "AppleClang"
#define ATLAS_C_COMPILER_VERSION "14.0.3.14030022"

#define ATLAS_CXX_COMPILER_ID      "AppleClang"
#define ATLAS_CXX_COMPILER_VERSION "14.0.3.14030022"

#define ATLAS_C_COMPILER       "/Library/Developer/CommandLineTools/usr/bin/cc"
#define ATLAS_C_FLAGS          " -pipe -O2 -g -DNDEBUG"

#define ATLAS_CXX_COMPILER     "/Library/Developer/CommandLineTools/usr/bin/c++"
#define ATLAS_CXX_FLAGS        " -pipe -Wall -Wextra -Wno-unused-parameter -Wno-sign-compare -O2 -g -DNDEBUG"

/* Needed for finding per package config files */

#define ATLAS_INSTALL_DIR       "/tmp/atlas/target/atlas"
#define ATLAS_INSTALL_BIN_DIR   "/tmp/atlas/target/atlas/bin"
#define ATLAS_INSTALL_LIB_DIR   "/tmp/atlas/target/atlas/lib"
#define ATLAS_INSTALL_DATA_DIR  "/tmp/atlas/target/atlas/share/atlas"

#define ATLAS_DEVELOPER_SRC_DIR "/opt/actions-runner/work/_work/python-develop-bundle/python-develop-bundle/src/eckit/src/fckit/src/eccodes/src/atlas"
#define ATLAS_DEVELOPER_BIN_DIR "/tmp/atlas/build"

/* Fortran support */

#if 0

#define ATLAS_Fortran_COMPILER_ID      ""
#define ATLAS_Fortran_COMPILER_VERSION ""

#define ATLAS_Fortran_COMPILER "/opt/homebrew/bin/gfortran"
#define ATLAS_Fortran_FLAGS    " -O2 -g -DNDEBUG"

#endif

#endif /* ATLAS_ecbuild_config_h */
