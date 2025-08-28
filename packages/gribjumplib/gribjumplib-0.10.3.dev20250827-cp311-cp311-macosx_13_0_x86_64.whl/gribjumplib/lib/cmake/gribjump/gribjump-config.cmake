# Config file for the gribjump package
# Defines the following variables:
#
#  gribjump_FEATURES       - list of enabled features
#  gribjump_VERSION        - version of the package
#  gribjump_GIT_SHA1       - Git revision of the package
#  gribjump_GIT_SHA1_SHORT - short Git revision of the package
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
set_and_check(gribjump_CMAKE_DIR "${PACKAGE_PREFIX_DIR}/lib/cmake/gribjump")
set_and_check(gribjump_BASE_DIR "${PACKAGE_PREFIX_DIR}/.")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(GRIBJUMP_CMAKE_DIR ${gribjump_CMAKE_DIR})
  set(GRIBJUMP_BASE_DIR ${gribjump_BASE_DIR})
endif()

### export version info
set(gribjump_VERSION           "0.10.3")
set(gribjump_GIT_SHA1          "962d16cbbf9cc0c7592b2fe4e53211e1b19e3b6a")
set(gribjump_GIT_SHA1_SHORT    "962d16c")

if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(GRIBJUMP_VERSION           "0.10.3" )
  set(GRIBJUMP_GIT_SHA1          "962d16cbbf9cc0c7592b2fe4e53211e1b19e3b6a" )
  set(GRIBJUMP_GIT_SHA1_SHORT    "962d16c" )
endif()

### has this configuration been exported from a build tree?
set(gribjump_IS_BUILD_DIR_EXPORT OFF)
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(GRIBJUMP_IS_BUILD_DIR_EXPORT ${gribjump_IS_BUILD_DIR_EXPORT})
endif()

### include the <project>-import.cmake file if there is one
if(EXISTS ${gribjump_CMAKE_DIR}/gribjump-import.cmake)
  set(gribjump_IMPORT_FILE "${gribjump_CMAKE_DIR}/gribjump-import.cmake")
  include(${gribjump_IMPORT_FILE})
endif()

### insert definitions for IMPORTED targets
if(NOT gribjump_BINARY_DIR)
  find_file(gribjump_TARGETS_FILE
    NAMES gribjump-targets.cmake
    HINTS ${gribjump_CMAKE_DIR}
    NO_DEFAULT_PATH)
  if(gribjump_TARGETS_FILE)
    include(${gribjump_TARGETS_FILE})
  endif()
endif()

### include the <project>-post-import.cmake file if there is one
if(EXISTS ${gribjump_CMAKE_DIR}/gribjump-post-import.cmake)
  set(gribjump_POST_IMPORT_FILE "${gribjump_CMAKE_DIR}/gribjump-post-import.cmake")
  include(${gribjump_POST_IMPORT_FILE})
endif()

### handle third-party dependencies
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(GRIBJUMP_LIBRARIES         "")
  set(GRIBJUMP_TPLS              "" )

  include(${CMAKE_CURRENT_LIST_FILE}.tpls OPTIONAL)
endif()

### publish this file as imported
if( DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT )
  set(gribjump_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(gribjump_IMPORT_FILE)
  set(GRIBJUMP_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(GRIBJUMP_IMPORT_FILE)
endif()

### export features and check requirements
set(gribjump_FEATURES "TESTS;PKGCONFIG;GRIBJUMP_LOCAL_EXTRACT;WARNINGS;WARNINGS")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(GRIBJUMP_FEATURES ${gribjump_FEATURES})
endif()
foreach(_f ${gribjump_FEATURES})
  set(gribjump_${_f}_FOUND 1)
  set(gribjump_HAVE_${_f} 1)
  if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
    set(GRIBJUMP_HAVE_${_f} 1)
  endif()
endforeach()
check_required_components(gribjump)
