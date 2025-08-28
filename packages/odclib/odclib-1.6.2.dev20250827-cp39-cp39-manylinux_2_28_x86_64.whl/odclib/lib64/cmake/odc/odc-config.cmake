# Config file for the odc package
# Defines the following variables:
#
#  odc_FEATURES       - list of enabled features
#  odc_VERSION        - version of the package
#  odc_GIT_SHA1       - Git revision of the package
#  odc_GIT_SHA1_SHORT - short Git revision of the package
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
set_and_check(odc_CMAKE_DIR "${PACKAGE_PREFIX_DIR}/lib64/cmake/odc")
set_and_check(odc_BASE_DIR "${PACKAGE_PREFIX_DIR}/.")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ODC_CMAKE_DIR ${odc_CMAKE_DIR})
  set(ODC_BASE_DIR ${odc_BASE_DIR})
endif()

### export version info
set(odc_VERSION           "1.6.2")
set(odc_GIT_SHA1          "b17379653100f4489a4ba5c80a6dff2a01f56372")
set(odc_GIT_SHA1_SHORT    "b173796")

if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ODC_VERSION           "1.6.2" )
  set(ODC_GIT_SHA1          "b17379653100f4489a4ba5c80a6dff2a01f56372" )
  set(ODC_GIT_SHA1_SHORT    "b173796" )
endif()

### has this configuration been exported from a build tree?
set(odc_IS_BUILD_DIR_EXPORT OFF)
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ODC_IS_BUILD_DIR_EXPORT ${odc_IS_BUILD_DIR_EXPORT})
endif()

### include the <project>-import.cmake file if there is one
if(EXISTS ${odc_CMAKE_DIR}/odc-import.cmake)
  set(odc_IMPORT_FILE "${odc_CMAKE_DIR}/odc-import.cmake")
  include(${odc_IMPORT_FILE})
endif()

### insert definitions for IMPORTED targets
if(NOT odc_BINARY_DIR)
  find_file(odc_TARGETS_FILE
    NAMES odc-targets.cmake
    HINTS ${odc_CMAKE_DIR}
    NO_DEFAULT_PATH)
  if(odc_TARGETS_FILE)
    include(${odc_TARGETS_FILE})
  endif()
endif()

### include the <project>-post-import.cmake file if there is one
if(EXISTS ${odc_CMAKE_DIR}/odc-post-import.cmake)
  set(odc_POST_IMPORT_FILE "${odc_CMAKE_DIR}/odc-post-import.cmake")
  include(${odc_POST_IMPORT_FILE})
endif()

### handle third-party dependencies
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ODC_LIBRARIES         "")
  set(ODC_TPLS              "" )

  include(${CMAKE_CURRENT_LIST_FILE}.tpls OPTIONAL)
endif()

### publish this file as imported
if( DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT )
  set(odc_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(odc_IMPORT_FILE)
  set(ODC_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(ODC_IMPORT_FILE)
endif()

### export features and check requirements
set(odc_FEATURES "TESTS;PKGCONFIG;WARNINGS;WARNINGS")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(ODC_FEATURES ${odc_FEATURES})
endif()
foreach(_f ${odc_FEATURES})
  set(odc_${_f}_FOUND 1)
  set(odc_HAVE_${_f} 1)
  if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
    set(ODC_HAVE_${_f} 1)
  endif()
endforeach()
check_required_components(odc)
