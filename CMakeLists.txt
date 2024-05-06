# Copyright 2022 NWChemEx-Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

cmake_minimum_required(VERSION 3.14)

#Downloads common CMake modules used throughout NWChemEx
include(cmake/get_nwx_cmake.cmake)

#Sets the version to whatever git thinks it is
include(get_version_from_git)
get_version_from_git(pluginplayer_version "${CMAKE_CURRENT_LIST_DIR}")
project(pluginplayer VERSION "${pluginplayer_version}" LANGUAGES CXX)

include(nwx_versions)
include(get_cmaize)
include(nwx_cxx_api_docs)

### Files and Paths ###
set(python_src_directory "${CMAKE_CURRENT_LIST_DIR}/src/")

# # Doxygen docs
nwx_cxx_api_docs("${CMAKE_CURRENT_SOURCE_DIR}/src" "${CMAKE_CURRENT_SOURCE_DIR}/include")

### Options ###
cmaize_option_list(
    BUILD_TESTING OFF "Should we build the tests?"
)

### Tests need PluginPlay examples ##
if("${BUILD_TESTING}")
    set(PP_BUILD_TARGETS pluginplay pluginplay_examples)
    set(PP_FIND_TARGETS nwx::pluginplay nwx::pluginplay_depends)
    set(PP_BUILD_TESTS ON)
else()
    set(PP_BUILD_TARGETS pluginplay)
    set(PP_FIND_TARGETS nwx::pluginplay)
    set(PP_BUILD_TESTS OFF)
endif()

## Build FriendZone's dependencies ##
cmaize_find_or_build_dependency(
    pluginplay
    URL github.com/NWChemEx/PluginPlay
    VERSION ${NWX_PLUGINPLAY_VERSION}
    BUILD_TARGET ${PP_BUILD_TARGETS}
    FIND_TARGET ${PP_FIND_TARGETS}
    CMAKE_ARGS BUILD_TESTING=${PP_BUILD_TESTS}
               BUILD_PYBIND11_PYBINDINGS=ON
)

#TOOD: Replace cmaize_add_library when it supports Python
add_library(${PROJECT_NAME} INTERFACE)
target_link_libraries(${PROJECT_NAME} INTERFACE pluginplay)

if("${BUILD_TESTING}")
    include(CTest)
    include(nwx_pybind11)
    set(PYTHON_TEST_DIR "${CMAKE_CURRENT_LIST_DIR}/tests")
    set(examples_src_dir "${CMAKE_CURRENT_LIST_DIR}/tests/pluginplayer_examples")

    cmaize_add_library(
        ${PROJECT_NAME}_examples
        SOURCE_DIR ${examples_src_dir}
        INCLUDE_DIRS ${examples_src_dir}
        DEPENDS Catch2::Catch2 ${PROJECT_NAME}
    )
    nwx_add_pybind11_module(
        ${PROJECT_NAME}_examples
        INSTALL OFF
        SOURCE_DIR ${examples_src_dir}
        DEPENDS parallelzone ${PROJECT_NAME} ${PROJECT_NAME}_examples
    )

    nwx_pybind11_tests(
        py_${PROJECT_NAME}
        "${PYTHON_TEST_DIR}/test_pluginplayer.py"
        SUBMODULES pluginplay_examples pluginplay parallelzone
    )
endif()

install(
    DIRECTORY "${python_src_directory}/pluginplayer"
    DESTINATION "${NWX_MODULE_DIRECTORY}"
)
