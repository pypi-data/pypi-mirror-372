FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11
  GIT_TAG v3.0.0
  DOWNLOAD_EXTRACT_TIMESTAMP NEW
)
FetchContent_MakeAvailable(pybind11)

FILE(GLOB
    MAIN_FILES
    *.cpp
)

pybind11_add_module(_core basisSplines.cpp)
target_link_libraries(
  _core
  PUBLIC
  basisSplines
)
install(TARGETS _core DESTINATION basisSplines)

# install stubs if available
if(EXISTS $ENV{PATH_PYSTUBS})
  install(DIRECTORY $ENV{PATH_PYSTUBS}/ DESTINATION basisSplines)
endif()