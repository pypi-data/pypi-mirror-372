/*
 * (C) Copyright 1996- ECMWF.
 *
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
 *
 * In applying this licence, ECMWF does not waive the privileges and immunities
 * granted to it by virtue of its status as an intergovernmental organisation nor
 * does it submit to any jurisdiction.
 */


#pragma once

#include "mir/mir_ecbuild_config.h"

#include "mir/api/mir_version.h"


#define mir_HAVE_ATLAS 1
#define mir_HAVE_GRID_FESOM 1
#define mir_HAVE_GRID_ICON 1
#define mir_HAVE_GRID_ORCA 1
#define mir_HAVE_PNG 0


constexpr bool _to_bool(int x = 0) {
    return x != 0;
}

constexpr bool MIR_HAVE_ATLAS       = _to_bool(1);
constexpr bool MIR_HAVE_NETCDF      = _to_bool(0);
constexpr bool MIR_HAVE_OMP         = _to_bool(0);
constexpr bool MIR_HAVE_PNG         = _to_bool(0);
constexpr bool MIR_HAVE_PROJ        = _to_bool();
constexpr bool MIR_HAVE_TESSELATION = _to_bool(1);
