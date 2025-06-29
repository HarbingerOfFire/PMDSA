#!/bin/bash

# Python script to execute
PYTHON_SCRIPT="PMDSA.py"

# Check that at least a directory was passed
if [ $# -lt 1 ]; then
    echo "Usage: $0 <directory> [extra python args]"
    exit 1
fi

# Extract the first argument as the directory
INPUT_DIR="$1"

# Shift so that "$@" now contains only the extra arguments
shift

# Header
echo "Index,Filename,Seperation,Angle,Dmag"

COUNT=0
for FILE in "$INPUT_DIR"/*; do
    FILENAME=$(basename "$FILE")
    
    # Run python script with FILE and any extra args
    OUTPUT=$(python3 "$PYTHON_SCRIPT" "$FILE" "$@")
    
    echo "$COUNT,$FILENAME,$OUTPUT"
    
    ((COUNT++))
done
