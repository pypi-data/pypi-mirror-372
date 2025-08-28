/*
 * (C) Copyright 2011- ECMWF.
 *
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
 * In applying this licence, ECMWF does not waive the privileges and immunities
 * granted to it by virtue of its status as an intergovernmental organisation nor
 * does it submit to any jurisdiction.
 */

#ifndef MULTIO_ecbuild_config_h
#define MULTIO_ecbuild_config_h

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

#define MULTIO_OS_NAME          "Linux-4.18.0-372.26.1.el8_6.x86_64"
#define MULTIO_OS_BITS          64
#define MULTIO_OS_BITS_STR      "64"
#define MULTIO_OS_STR           "linux.64"
#define MULTIO_OS_VERSION       "4.18.0-372.26.1.el8_6.x86_64"
#define MULTIO_SYS_PROCESSOR    "x86_64"

#define MULTIO_BUILD_TIMESTAMP  "20250827150215"
#define MULTIO_BUILD_TYPE       "RelWithDebInfo"

#define MULTIO_C_COMPILER_ID      "GNU"
#define MULTIO_C_COMPILER_VERSION "13.3.1"

#define MULTIO_CXX_COMPILER_ID      "GNU"
#define MULTIO_CXX_COMPILER_VERSION "13.3.1"

#define MULTIO_C_COMPILER       "/opt/rh/gcc-toolset-13/root/usr/bin/cc"
#define MULTIO_C_FLAGS          " -pipe -O2 -g -DNDEBUG"

#define MULTIO_CXX_COMPILER     "/opt/rh/gcc-toolset-13/root/usr/bin/c++"
#define MULTIO_CXX_FLAGS        " -pipe -Wall -Wextra -Wno-unused-parameter -Wno-unused-variable -Wno-sign-compare -O2 -g -DNDEBUG"

/* Needed for finding per package config files */

#define MULTIO_INSTALL_DIR       "/tmp/multio/target/multio"
#define MULTIO_INSTALL_BIN_DIR   "/tmp/multio/target/multio/bin"
#define MULTIO_INSTALL_LIB_DIR   "/tmp/multio/target/multio/lib64"
#define MULTIO_INSTALL_DATA_DIR  "/tmp/multio/target/multio/share/multio"

#define MULTIO_DEVELOPER_SRC_DIR "/src/eckit/src/fckit/src/eccodes/src/atlas/src/metkit/src/fdb/src/mir/src/multio"
#define MULTIO_DEVELOPER_BIN_DIR "/tmp/multio/build"

/* Fortran support */

#if 1

#define MULTIO_Fortran_COMPILER_ID      "IntelLLVM"
#define MULTIO_Fortran_COMPILER_VERSION "2025.2.0"

#define MULTIO_Fortran_COMPILER "/opt/intel/oneapi/compiler/latest/bin/ifx"
#define MULTIO_Fortran_FLAGS    " -real-size 64 -fpe0 -init=snan -no-fma -O2 -g"

#endif

#endif /* MULTIO_ecbuild_config_h */
