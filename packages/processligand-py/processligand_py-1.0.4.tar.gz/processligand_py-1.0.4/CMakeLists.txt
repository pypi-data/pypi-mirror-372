# CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(processligand_builder C CXX)

include(FetchContent)

set(BUILD_STATIC_EXECUTABLE ON CACHE BOOL "Build static executable" FORCE)
set(CMAKE_BUILD_TYPE Release)

FetchContent_Declare(
  processligand_repo
  GIT_REPOSITORY https://github.com/NRGlab/Process_Ligand.git
  GIT_TAG        cmake
)

FetchContent_GetProperties(processligand_repo)
if(NOT processligand_repo_POPULATED)
  FetchContent_Populate(processligand_repo)
endif()

add_subdirectory(${processligand_repo_SOURCE_DIR} ${processligand_repo_BINARY_DIR})

set(PROCESSLIGAND_EXECUTABLE $<TARGET_FILE:ProcessLigand>)

install(PROGRAMS ${PROCESSLIGAND_EXECUTABLE}
    DESTINATION ${CMAKE_INSTALL_PREFIX}/bin
)

install(FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/processligandpy/__init__.py
    ${CMAKE_CURRENT_SOURCE_DIR}/src/processligandpy/processligand_wrapper.py
    DESTINATION ${CMAKE_INSTALL_PREFIX}
)
