# Config file for the fdb5 package
# Defines the following variables:
#
#  fdb5_FEATURES       - list of enabled features
#  fdb5_VERSION        - version of the package
#  fdb5_GIT_SHA1       - Git revision of the package
#  fdb5_GIT_SHA1_SHORT - short Git revision of the package
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
set_and_check(fdb5_CMAKE_DIR "${PACKAGE_PREFIX_DIR}/lib/cmake/fdb5")
set_and_check(fdb5_BASE_DIR "${PACKAGE_PREFIX_DIR}/.")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(FDB5_CMAKE_DIR ${fdb5_CMAKE_DIR})
  set(FDB5_BASE_DIR ${fdb5_BASE_DIR})
endif()

### export version info
set(fdb5_VERSION           "5.17.5")
set(fdb5_GIT_SHA1          "4ea8e6431d8a5cb71ca4c2603c32831b979cb210")
set(fdb5_GIT_SHA1_SHORT    "4ea8e64")

if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(FDB5_VERSION           "5.17.5" )
  set(FDB5_GIT_SHA1          "4ea8e6431d8a5cb71ca4c2603c32831b979cb210" )
  set(FDB5_GIT_SHA1_SHORT    "4ea8e64" )
endif()

### has this configuration been exported from a build tree?
set(fdb5_IS_BUILD_DIR_EXPORT OFF)
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(FDB5_IS_BUILD_DIR_EXPORT ${fdb5_IS_BUILD_DIR_EXPORT})
endif()

### include the <project>-import.cmake file if there is one
if(EXISTS ${fdb5_CMAKE_DIR}/fdb5-import.cmake)
  set(fdb5_IMPORT_FILE "${fdb5_CMAKE_DIR}/fdb5-import.cmake")
  include(${fdb5_IMPORT_FILE})
endif()

### insert definitions for IMPORTED targets
if(NOT fdb5_BINARY_DIR)
  find_file(fdb5_TARGETS_FILE
    NAMES fdb5-targets.cmake
    HINTS ${fdb5_CMAKE_DIR}
    NO_DEFAULT_PATH)
  if(fdb5_TARGETS_FILE)
    include(${fdb5_TARGETS_FILE})
  endif()
endif()

### include the <project>-post-import.cmake file if there is one
if(EXISTS ${fdb5_CMAKE_DIR}/fdb5-post-import.cmake)
  set(fdb5_POST_IMPORT_FILE "${fdb5_CMAKE_DIR}/fdb5-post-import.cmake")
  include(${fdb5_POST_IMPORT_FILE})
endif()

### handle third-party dependencies
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(FDB5_LIBRARIES         "")
  set(FDB5_TPLS              "" )

  include(${CMAKE_CURRENT_LIST_FILE}.tpls OPTIONAL)
endif()

### publish this file as imported
if( DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT )
  set(fdb5_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(fdb5_IMPORT_FILE)
  set(FDB5_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(FDB5_IMPORT_FILE)
endif()

### export features and check requirements
set(fdb5_FEATURES "TESTS;PKGCONFIG;TOCFDB;FDB_REMOTE;BUILD_TOOLS;FDB_BUILD_TOOLS;WARNINGS;WARNINGS")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(FDB5_FEATURES ${fdb5_FEATURES})
endif()
foreach(_f ${fdb5_FEATURES})
  set(fdb5_${_f}_FOUND 1)
  set(fdb5_HAVE_${_f} 1)
  if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
    set(FDB5_HAVE_${_f} 1)
  endif()
endforeach()
check_required_components(fdb5)
