#!/bin/bash

# Python script to execute
PYTHON_SCRIPT="PMDSA.py"

# Ensure at least directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <root_directory> [extra python args]"
    exit 1
fi

ROOT_DIR="$1"
shift

find "$ROOT_DIR" -type d | while read -r SUBDIR; do
    shopt -s nullglob
    FILES=("$SUBDIR"/*)
    shopt -u nullglob

    if [ ${#FILES[@]} -eq 0 ]; then continue; fi

    # Safe subdir name for CSV (relative path with slashes replaced)
    RELATIVE_NAME="${SUBDIR#$ROOT_DIR/}"
    CSV_NAME=$(echo "${RELATIVE_NAME:-$(basename "$ROOT_DIR")}")
    CSV_FILE="${CSV_NAME}.csv"

    echo "Writing to $CSV_FILE from $SUBDIR"

    # Write header
    echo "Index,Filename,Seperation,Angle,Dmag" > "$CSV_FILE"

    COUNT=0
    for FILE in "${FILES[@]}"; do
        if [ -f "$FILE" ]; then
            FILENAME=$(basename "$FILE")
            OUTPUT=$(python3 "$PYTHON_SCRIPT" "$FILE" "$@")
            echo "$COUNT,$FILENAME,$OUTPUT" >> "$CSV_FILE"
            ((COUNT++))
        fi
    done
done
