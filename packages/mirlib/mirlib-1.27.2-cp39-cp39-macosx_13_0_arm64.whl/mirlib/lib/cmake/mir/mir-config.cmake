# Config file for the mir package
# Defines the following variables:
#
#  mir_FEATURES       - list of enabled features
#  mir_VERSION        - version of the package
#  mir_GIT_SHA1       - Git revision of the package
#  mir_GIT_SHA1_SHORT - short Git revision of the package
#


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was project-config.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

### computed paths
set_and_check(mir_CMAKE_DIR "${PACKAGE_PREFIX_DIR}/lib/cmake/mir")
set_and_check(mir_BASE_DIR "${PACKAGE_PREFIX_DIR}/.")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(MIR_CMAKE_DIR ${mir_CMAKE_DIR})
  set(MIR_BASE_DIR ${mir_BASE_DIR})
endif()

### export version info
set(mir_VERSION           "1.27.2")
set(mir_GIT_SHA1          "bef64b6b373d1ab1d248cf57e086e11fb00bb8a8")
set(mir_GIT_SHA1_SHORT    "bef64b6")

if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(MIR_VERSION           "1.27.2" )
  set(MIR_GIT_SHA1          "bef64b6b373d1ab1d248cf57e086e11fb00bb8a8" )
  set(MIR_GIT_SHA1_SHORT    "bef64b6" )
endif()

### has this configuration been exported from a build tree?
set(mir_IS_BUILD_DIR_EXPORT OFF)
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(MIR_IS_BUILD_DIR_EXPORT ${mir_IS_BUILD_DIR_EXPORT})
endif()

### include the <project>-import.cmake file if there is one
if(EXISTS ${mir_CMAKE_DIR}/mir-import.cmake)
  set(mir_IMPORT_FILE "${mir_CMAKE_DIR}/mir-import.cmake")
  include(${mir_IMPORT_FILE})
endif()

### insert definitions for IMPORTED targets
if(NOT mir_BINARY_DIR)
  find_file(mir_TARGETS_FILE
    NAMES mir-targets.cmake
    HINTS ${mir_CMAKE_DIR}
    NO_DEFAULT_PATH)
  if(mir_TARGETS_FILE)
    include(${mir_TARGETS_FILE})
  endif()
endif()

### include the <project>-post-import.cmake file if there is one
if(EXISTS ${mir_CMAKE_DIR}/mir-post-import.cmake)
  set(mir_POST_IMPORT_FILE "${mir_CMAKE_DIR}/mir-post-import.cmake")
  include(${mir_POST_IMPORT_FILE})
endif()

### handle third-party dependencies
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(MIR_LIBRARIES         "")
  set(MIR_TPLS              "" )

  include(${CMAKE_CURRENT_LIST_FILE}.tpls OPTIONAL)
endif()

### publish this file as imported
if( DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT )
  set(mir_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(mir_IMPORT_FILE)
  set(MIR_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(MIR_IMPORT_FILE)
endif()

### export features and check requirements
set(mir_FEATURES "TESTS;PKGCONFIG;MIR_DOWNLOAD_MASKS;ATLAS;WARNINGS;WARNINGS")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(MIR_FEATURES ${mir_FEATURES})
endif()
foreach(_f ${mir_FEATURES})
  set(mir_${_f}_FOUND 1)
  set(mir_HAVE_${_f} 1)
  if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
    set(MIR_HAVE_${_f} 1)
  endif()
endforeach()
check_required_components(mir)
