/*
 * (C) Copyright 2011- ECMWF.
 *
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
 * In applying this licence, ECMWF does not waive the privileges and immunities
 * granted to it by virtue of its status as an intergovernmental organisation nor
 * does it submit to any jurisdiction.
 */

#ifndef ODC_ecbuild_config_h
#define ODC_ecbuild_config_h

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

#define ODC_OS_NAME          "Linux-4.18.0-372.26.1.el8_6.x86_64"
#define ODC_OS_BITS          64
#define ODC_OS_BITS_STR      "64"
#define ODC_OS_STR           "linux.64"
#define ODC_OS_VERSION       "4.18.0-372.26.1.el8_6.x86_64"
#define ODC_SYS_PROCESSOR    "x86_64"

#define ODC_BUILD_TIMESTAMP  "20250827151727"
#define ODC_BUILD_TYPE       "RelWithDebInfo"

#define ODC_C_COMPILER_ID      "GNU"
#define ODC_C_COMPILER_VERSION "13.3.1"

#define ODC_CXX_COMPILER_ID      "GNU"
#define ODC_CXX_COMPILER_VERSION "13.3.1"

#define ODC_C_COMPILER       "/opt/rh/gcc-toolset-13/root/usr/bin/cc"
#define ODC_C_FLAGS          " -pipe -O2 -g -DNDEBUG"

#define ODC_CXX_COMPILER     "/opt/rh/gcc-toolset-13/root/usr/bin/c++"
#define ODC_CXX_FLAGS        " -pipe -Wall -Wextra -Wno-unused-parameter -Wno-unused-variable -Wno-sign-compare -O2 -g -DNDEBUG"

/* Needed for finding per package config files */

#define ODC_INSTALL_DIR       "/tmp/odc/target/odc"
#define ODC_INSTALL_BIN_DIR   "/tmp/odc/target/odc/bin"
#define ODC_INSTALL_LIB_DIR   "/tmp/odc/target/odc/lib64"
#define ODC_INSTALL_DATA_DIR  "/tmp/odc/target/odc/share/odc"

#define ODC_DEVELOPER_SRC_DIR "/src/eckit/src/fckit/src/eccodes/src/atlas/src/metkit/src/fdb/src/mir/src/multio/src/odc"
#define ODC_DEVELOPER_BIN_DIR "/tmp/odc/build"

/* Fortran support */

#if 0

#define ODC_Fortran_COMPILER_ID      ""
#define ODC_Fortran_COMPILER_VERSION ""

#define ODC_Fortran_COMPILER "/opt/intel/oneapi/compiler/latest/bin/ifx"
#define ODC_Fortran_FLAGS    ""

#endif

#endif /* ODC_ecbuild_config_h */
