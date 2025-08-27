FetchContent_Declare(
  eigen
  URL https://gitlab.com/libeigen/eigen/-/archive/3.4/eigen-3.4.zip
  DOWNLOAD_EXTRACT_TIMESTAMP NEW
)
set(BUILD_TESTING OFF)
set(EIGEN_BUILD_TESTING OFF)
set(EIGEN_MPL2_ONLY ON)
set(EIGEN_BUILD_PKGCONFIG OFF)
set(EIGEN_BUILD_DOC OFF)
FetchContent_MakeAvailable(eigen)


# make cache variables for install destinations
include(GNUInstallDirs)

add_library(basisSplines INTERFACE)
target_link_libraries(basisSplines INTERFACE eigen)

target_include_directories(basisSplines
  INTERFACE
  $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

include(CMakePackageConfigHelpers)
configure_package_config_file (
  ${PROJECT_SOURCE_DIR}/cmake/Config.cmake.in
  ${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
  INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME}
)

export(
  TARGETS basisSplines eigen
  NAMESPACE BasisSplines::
  FILE ${PROJECT_BINARY_DIR}/${PROJECT_NAME}Targets.cmake
)