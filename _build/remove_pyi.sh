#!/bin/zsh
set -e

find src/ -type f -name '*.pyi' -exec rm {} +
echo "Done"