include( CMakeFindDependencyMacro )
find_dependency( eccodes HINTS /tmp/mir/prereqs/eccodeslib/lib64/cmake/eccodes )
find_dependency( eckit   HINTS /tmp/mir/prereqs/eckitlib/lib64/cmake/eckit )
find_dependency( atlas   HINTS /tmp/mir/prereqs/atlaslib-ecmwf/lib64/cmake/atlas )

set( MIR_LIBRARIES mir )
