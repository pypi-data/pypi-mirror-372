include( CMakeFindDependencyMacro )
find_dependency( eccodes HINTS /tmp/mir/prereqs/eccodeslib/lib/cmake/eccodes )
find_dependency( eckit   HINTS /tmp/mir/prereqs/eckitlib/lib/cmake/eckit )
find_dependency( atlas   HINTS /tmp/mir/prereqs/atlaslib-ecmwf/lib/cmake/atlas )

set( MIR_LIBRARIES mir )
