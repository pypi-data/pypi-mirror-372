/*
 * (C) Copyright 2011- ECMWF.
 *
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
 * In applying this licence, ECMWF does not waive the privileges and immunities
 * granted to it by virtue of its status as an intergovernmental organisation nor
 * does it submit to any jurisdiction.
 */

#ifndef MIR_ecbuild_config_h
#define MIR_ecbuild_config_h

/* ecbuild info */

#ifndef ECBUILD_VERSION_STR
#define ECBUILD_VERSION_STR "3.11.0"
#endif
#ifndef ECBUILD_VERSION
#define ECBUILD_VERSION "3.11.0"
#endif
#ifndef ECBUILD_MACROS_DIR
#define ECBUILD_MACROS_DIR  "/opt/actions-runner/work/_work/mir/mir/ecbuild/cmake"
#endif

/* config info */

#define MIR_OS_NAME          "Darwin-22.5.0"
#define MIR_OS_BITS          64
#define MIR_OS_BITS_STR      "64"
#define MIR_OS_STR           "macosx.64"
#define MIR_OS_VERSION       "22.5.0"
#define MIR_SYS_PROCESSOR    "x86_64"

#define MIR_BUILD_TIMESTAMP  "20250826162139"
#define MIR_BUILD_TYPE       "RelWithDebInfo"

#define MIR_C_COMPILER_ID      "AppleClang"
#define MIR_C_COMPILER_VERSION "14.0.3.14030022"

#define MIR_CXX_COMPILER_ID      "AppleClang"
#define MIR_CXX_COMPILER_VERSION "14.0.3.14030022"

#define MIR_C_COMPILER       "/Library/Developer/CommandLineTools/usr/bin/cc"
#define MIR_C_FLAGS          " -pipe -O2 -g -DNDEBUG"

#define MIR_CXX_COMPILER     "/Library/Developer/CommandLineTools/usr/bin/c++"
#define MIR_CXX_FLAGS        " -pipe -Wall -Wextra -Wno-unused-parameter -Wno-unused-variable -Wno-sign-compare -O2 -g -DNDEBUG"

/* Needed for finding per package config files */

#define MIR_INSTALL_DIR       "/tmp/mir/target/mir"
#define MIR_INSTALL_BIN_DIR   "/tmp/mir/target/mir/bin"
#define MIR_INSTALL_LIB_DIR   "/tmp/mir/target/mir/lib"
#define MIR_INSTALL_DATA_DIR  "/tmp/mir/target/mir/share/mir"

#define MIR_DEVELOPER_SRC_DIR "/opt/actions-runner/work/_work/mir/mir/proj"
#define MIR_DEVELOPER_BIN_DIR "/tmp/mir/build"

/* Fortran support */

#if 0

#define MIR_Fortran_COMPILER_ID      ""
#define MIR_Fortran_COMPILER_VERSION ""

#define MIR_Fortran_COMPILER ""
#define MIR_Fortran_FLAGS    ""

#endif

#endif /* MIR_ecbuild_config_h */
