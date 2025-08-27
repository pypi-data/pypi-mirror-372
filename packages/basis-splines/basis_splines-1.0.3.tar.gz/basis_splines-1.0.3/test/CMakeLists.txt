include(GoogleTest)

FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/v1.16.0.zip
  DOWNLOAD_EXTRACT_TIMESTAMP NEW
)
FetchContent_MakeAvailable(googletest)

FILE(GLOB
    MAIN_FILES
    *Test.cpp
)

foreach(item ${MAIN_FILES})
    get_filename_component(LIB_FILE ${item} NAME_WE)
    add_executable(
        ${LIB_FILE}
        ${item}
    )

    target_include_directories(
        ${LIB_FILE}
        PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
    )

    target_link_libraries(
        ${LIB_FILE}
        PRIVATE
        basisSplines
        GTest::gtest_main
        eigen
    )

    gtest_discover_tests(${LIB_FILE})
endforeach()