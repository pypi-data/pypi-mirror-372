# CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(FlexAID_Builder CXX)

include(FetchContent)
include(GNUInstallDirs)

FetchContent_Declare(
  flexaid_repo
  GIT_REPOSITORY https://github.com/NRGlab/FlexAID.git
  GIT_TAG        5e06c8bba23179209bef5c40a2e100158244320f
)

FetchContent_MakeAvailable(flexaid_repo)

set(FLEXAID_EXECUTABLE $<TARGET_FILE:FlexAID>)

install(PROGRAMS ${FLEXAID_EXECUTABLE}
    DESTINATION ${CMAKE_INSTALL_PREFIX}/bin
)

install(FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/flexaidpy/__init__.py
    ${CMAKE_CURRENT_SOURCE_DIR}/src/flexaidpy/FlexAID_wrapper.py
    ${CMAKE_CURRENT_SOURCE_DIR}/src/flexaidpy/write_config.py
    ${CMAKE_CURRENT_SOURCE_DIR}/src/flexaidpy/write_ga.py
    DESTINATION ${CMAKE_INSTALL_PREFIX}
)

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src/flexaidpy/deps
        DESTINATION ${CMAKE_INSTALL_PREFIX})