#!/bin/bash

# default file extension .jpg
EXTENSION="jpg"

# declare empty array of positional arguments
declare -a POSITIONAL_ARGS

# define help string
HELP_STRING=$'Usage
    examples.bash [options] <source-file-names>
    echo | examples.bash [options] <source-file-names>

Specify the names of the source files to execute.

Options
    -h | --help         Help message.
    -e | --extension    File extension of output image (.jpg or .eps).
    -a | --all          Run all examples.\n'

# parse arugments
while [[ $# -gt 0 ]]; do
  case $1 in
        # file extension (.jpg or .eps)
    -e|--extension)
        EXTENSION="$2"
        shift
        shift
      ;;
    -h|--help)
        echo "$HELP_STRING"
        shift
        ;;
    -a|--all)
        for f in ./examples/cpp/*.cpp; do
            POSITIONAL_ARGS+=("$(basename "$f" .cpp)")
        done
        break
        ;;
    -*|--*)
        echo "Unknown option $1"
        exit 1
        ;;
    # executables as positional arguments
    *)
        POSITIONAL_ARGS+=("$1")
        shift
        ;;
  esac
done

OUT_DIRECTORY=$WORKING_DIRECTORY/examples/cpp/out
mkdir -p $OUT_DIRECTORY

for FILE in "${POSITIONAL_ARGS[@]}"; do
    $EXAMPLE_BINS/$FILE $OUT_DIRECTORY/$FILE $EXTENSION
done