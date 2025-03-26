#!/bin/bash

# Python script to execute
PYTHON_SCRIPT="main.py"

# Loop through all files in the directory

echo "Index,Filename,Seperation,Angle,Dmag"

COUNT=0
for FILE in "$1"/*; do
    # Extract just the filename
    FILENAME=$(basename "$FILE")
    
    # Execute the Python script with the file as an argument and capture the output
    OUTPUT=$(python3 "$PYTHON_SCRIPT" "$FILE")
    
    # Print the file number, filename, and Python output separated by commas
    echo "$COUNT,$FILENAME,$OUTPUT"
    
    # Increment file count
    ((COUNT++))
done
