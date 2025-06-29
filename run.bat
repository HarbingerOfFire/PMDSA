@echo off
setlocal enabledelayedexpansion

:: Check for at least one argument
if "%~1"=="" (
    echo Usage: %~nx0 ^<directory^> [extra python args]
    exit /b 1
)

:: First argument is the input directory
set "INPUT_DIR=%~1"
shift /1

:: Collect all extra arguments into a single variable
set "EXTRA_ARGS="
:loop
shift /1
if "%~1"=="" goto start_loop
set "EXTRA_ARGS=!EXTRA_ARGS! %~1"
goto loop

:start_loop
echo Index,Filename,Seperation,Angle,Dmag

set COUNT=0
for %%F in ("%INPUT_DIR%\*") do (
    set "FILENAME=%%~nxF"
    for /f "delims=" %%O in ('python PMDSA.py "%%F"!EXTRA_ARGS!') do (
        echo !COUNT!,!FILENAME!,%%O
    )
    set /a COUNT+=1
)

endlocal
