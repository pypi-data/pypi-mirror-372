#!/bin/bash

PATH_BUILD="build"

HELP_STRING=$'Usage
    source setup.bash [options]

Setup environment variables for running benchmarks and examples.

Options
    -h|--help   Help message.
    -b|--build  Build directory.\n'

# parse arugments
while [[ $# -gt 0 ]]; do
  case $1 in
    # set build directory
    -b|--build)
        PATH_BUILD="$2"
        shift
        shift
      ;;
    # print help string
    -h|--help)
        echo "$HELP_STRING"
        exit 1
        ;;
    # unknown option
    -*|--*)
        echo "Unknown option $1"
        exit 1
        ;;
  esac
done

export PATH_WORKING_DIR=$(pwd)
export PATH_BUILD=$PATH_WORKING_DIR/$PATH_BUILD
export PATH_BENCHMARK_BINS=$PATH_BUILD/benchmarks
export PATH_EXAMPLE_BINS=$PATH_BUILD/examples/cpp
export PATH_PYBINDS=$PATH_WORKING_DIR/bindings/python
export PATH_PYSTUBS=$PATH_PYBINDS/basisSplinesStubs