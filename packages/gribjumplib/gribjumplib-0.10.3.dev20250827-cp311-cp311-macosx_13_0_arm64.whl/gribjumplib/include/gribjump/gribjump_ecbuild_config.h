/*
 * (C) Copyright 2011- ECMWF.
 *
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
 * In applying this licence, ECMWF does not waive the privileges and immunities
 * granted to it by virtue of its status as an intergovernmental organisation nor
 * does it submit to any jurisdiction.
 */

#ifndef GRIBJUMP_ecbuild_config_h
#define GRIBJUMP_ecbuild_config_h

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

#define GRIBJUMP_OS_NAME          "Darwin-22.5.0"
#define GRIBJUMP_OS_BITS          64
#define GRIBJUMP_OS_BITS_STR      "64"
#define GRIBJUMP_OS_STR           "macosx.64"
#define GRIBJUMP_OS_VERSION       "22.5.0"
#define GRIBJUMP_SYS_PROCESSOR    "arm64"

#define GRIBJUMP_BUILD_TIMESTAMP  "20250827155434"
#define GRIBJUMP_BUILD_TYPE       "RelWithDebInfo"

#define GRIBJUMP_C_COMPILER_ID      "AppleClang"
#define GRIBJUMP_C_COMPILER_VERSION "14.0.3.14030022"

#define GRIBJUMP_CXX_COMPILER_ID      "AppleClang"
#define GRIBJUMP_CXX_COMPILER_VERSION "14.0.3.14030022"

#define GRIBJUMP_C_COMPILER       "/Library/Developer/CommandLineTools/usr/bin/cc"
#define GRIBJUMP_C_FLAGS          " -pipe -O2 -g -DNDEBUG"

#define GRIBJUMP_CXX_COMPILER     "/Library/Developer/CommandLineTools/usr/bin/c++"
#define GRIBJUMP_CXX_FLAGS        " -pipe -Wall -Wextra -Wno-unused-parameter -Wno-unused-variable -Wno-sign-compare -O2 -g -DNDEBUG"

/* Needed for finding per package config files */

#define GRIBJUMP_INSTALL_DIR       "/tmp/gribjump/target/gribjump"
#define GRIBJUMP_INSTALL_BIN_DIR   "/tmp/gribjump/target/gribjump/bin"
#define GRIBJUMP_INSTALL_LIB_DIR   "/tmp/gribjump/target/gribjump/lib"
#define GRIBJUMP_INSTALL_DATA_DIR  "/tmp/gribjump/target/gribjump/share/gribjump"

#define GRIBJUMP_DEVELOPER_SRC_DIR "/opt/actions-runner/work/_work/python-develop-bundle/python-develop-bundle/src/eckit/src/fckit/src/eccodes/src/atlas/src/metkit/src/fdb/src/mir/src/multio/src/odc/src/gribjump"
#define GRIBJUMP_DEVELOPER_BIN_DIR "/tmp/gribjump/build"

/* Fortran support */

#if 0

#define GRIBJUMP_Fortran_COMPILER_ID      ""
#define GRIBJUMP_Fortran_COMPILER_VERSION ""

#define GRIBJUMP_Fortran_COMPILER ""
#define GRIBJUMP_Fortran_FLAGS    ""

#endif

#endif /* GRIBJUMP_ecbuild_config_h */
