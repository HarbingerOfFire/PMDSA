@echo off
setlocal enabledelayedexpansion

:: Python script to execute
set "PYTHON_SCRIPT=PMDSA.py"

:: Print header
echo Index,Filename,Separation,Angle,Dmag

:: Initialize counter
set COUNT=0

:: Loop through all files in the specified directory
for %%F in ("%~1\*") do (
    set "FILENAME=%%~nxF"
    
    :: Execute the Python script with the file as an argument and capture the output
    for /f "delims=" %%O in ('python "%PYTHON_SCRIPT%" "%%F"') do set "OUTPUT=%%O"

    :: Print the file number, filename, and Python output separated by commas
    echo !COUNT!,!FILENAME!,!OUTPUT!

    :: Increment counter
    set /a COUNT+=1
)

endlocal
