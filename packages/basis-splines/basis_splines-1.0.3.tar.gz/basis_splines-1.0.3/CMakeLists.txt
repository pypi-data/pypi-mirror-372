cmake_minimum_required(VERSION 3.31.6)

set(PACKAGE_VERSION 1.0.3)

project(BasisSplines VERSION ${PACKAGE_VERSION})

include(FetchContent)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

set(PROJECT_INCLUDE_DIR ${PROJECT_SOURCE_DIR}/include/basisSplines)
add_subdirectory(${PROJECT_INCLUDE_DIR})

option(BUILD_TEST "Build tests for transformation." ON)
option(BUILD_EXAMPLES "Build examples." ON)
option(BUILD_PYBINDS "Build python bindings." ON)

find_package(Doxygen)
option(BUILD_DOCS "Build documentation." ON)

if(BUILD_TEST)
    enable_testing()
    add_subdirectory(test)
endif()

if(BUILD_EXAMPLES)
    add_subdirectory(examples/cpp)
endif()

if(BUILD_DOCS)
    set(PYBIND_BINARY_DIR ${PROJECT_BINARY_DIR}/bindings/python)
    set(PYBIND_SOURCE_DIR ${PROJECT_SOURCE_DIR}/bindings/python)

    find_package(Doxygen REQUIRED)
    set(doxyfile_in ${PROJECT_SOURCE_DIR}/Doxyfile.in)
    set(doxyfile ${CMAKE_CURRENT_BINARY_DIR}/docs/Doxyfile)

    configure_file(${doxyfile_in} ${doxyfile} @ONLY)

    # also build python documentation if stubs are available
    if(EXISTS ${PYBIND_SOURCE_DIR}/basisSplinesStubs)
        make_directory(${PYBIND_BINARY_DIR}/basisSplines)
        add_custom_target(process_stubs ALL
            COMMAND doxypypy -c -a ${PYBIND_SOURCE_DIR}/basisSplinesStubs/_core.pyi > ${PYBIND_BINARY_DIR}/basisSplines/_core.py
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
            COMMENT "Processing python stubs with doxypypy")

        add_custom_target(doc ALL
            COMMAND doxygen ${doxyfile}
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
            COMMENT "Generating API documentation with Doxygen"
            DEPENDS process_stubs)
    # fallback to only C++ docs
    else()
        add_custom_target(doc ALL
            COMMAND doxygen ${doxyfile}
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
            COMMENT "Generating API documentation with Doxygen"
            VERBATIM)
    endif()
endif()

if(BUILD_PYBINDS)
    add_subdirectory(bindings/python/basisSplines)
endif()