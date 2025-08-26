#!/bin/bash
set -euo pipefail

executable=${1:?Usage: run_memviz.sh <path-to-binary>}
exe_name=$(basename "$executable")
path="$exe_name.txt"



# check if valgrind exists
if ! command -v valgrind &> /dev/null; then
    IMAGE="memviz-env"

    # check if docker exists
    if ! command -v docker &> /dev/null; then
        echo "Unable to run valgrind, please either:"
        echo "  1. Install valgrind: https://valgrind.org/downloads/current.html"
        echo "  2. Or install Docker: https://www.docker.com/"
        exit 1
    fi

    echo "[memviz] Running inside Docker..."
    docker run --rm -v "$(pwd)":/workspace $IMAGE \
        bash -c "valgrind --tool=cachegrind /workspace/$executable > /dev/null 2> /workspace/$path && rm -f /workspace/cachegrind.out.*"
else
    echo "[memviz] Running valgrind locally..."
    valgrind --tool=cachegrind "$executable" > /dev/null 2> "$path"
    rm -f cachegrind.out.*
fi
