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
#define ECBUILD_MACROS_DIR  "/src/ecbuild/cmake"
#endif

/* config info */

#define GRIBJUMP_OS_NAME          "Linux-4.18.0-372.26.1.el8_6.x86_64"
#define GRIBJUMP_OS_BITS          64
#define GRIBJUMP_OS_BITS_STR      "64"
#define GRIBJUMP_OS_STR           "linux.64"
#define GRIBJUMP_OS_VERSION       "4.18.0-372.26.1.el8_6.x86_64"
#define GRIBJUMP_SYS_PROCESSOR    "x86_64"

#define GRIBJUMP_BUILD_TIMESTAMP  "20250827150810"
#define GRIBJUMP_BUILD_TYPE       "RelWithDebInfo"

#define GRIBJUMP_C_COMPILER_ID      "GNU"
#define GRIBJUMP_C_COMPILER_VERSION "13.3.1"

#define GRIBJUMP_CXX_COMPILER_ID      "GNU"
#define GRIBJUMP_CXX_COMPILER_VERSION "13.3.1"

#define GRIBJUMP_C_COMPILER       "/opt/rh/gcc-toolset-13/root/usr/bin/cc"
#define GRIBJUMP_C_FLAGS          " -pipe -O2 -g -DNDEBUG"

#define GRIBJUMP_CXX_COMPILER     "/opt/rh/gcc-toolset-13/root/usr/bin/c++"
#define GRIBJUMP_CXX_FLAGS        " -pipe -Wall -Wextra -Wno-unused-parameter -Wno-unused-variable -Wno-sign-compare -O2 -g -DNDEBUG"

/* Needed for finding per package config files */

#define GRIBJUMP_INSTALL_DIR       "/tmp/gribjump/target/gribjump"
#define GRIBJUMP_INSTALL_BIN_DIR   "/tmp/gribjump/target/gribjump/bin"
#define GRIBJUMP_INSTALL_LIB_DIR   "/tmp/gribjump/target/gribjump/lib64"
#define GRIBJUMP_INSTALL_DATA_DIR  "/tmp/gribjump/target/gribjump/share/gribjump"

#define GRIBJUMP_DEVELOPER_SRC_DIR "/src/eckit/src/fckit/src/eccodes/src/atlas/src/metkit/src/fdb/src/mir/src/multio/src/odc/src/gribjump"
#define GRIBJUMP_DEVELOPER_BIN_DIR "/tmp/gribjump/build"

/* Fortran support */

#if 0

#define GRIBJUMP_Fortran_COMPILER_ID      ""
#define GRIBJUMP_Fortran_COMPILER_VERSION ""

#define GRIBJUMP_Fortran_COMPILER "/opt/intel/oneapi/compiler/latest/bin/ifx"
#define GRIBJUMP_Fortran_FLAGS    ""

#endif

#endif /* GRIBJUMP_ecbuild_config_h */
