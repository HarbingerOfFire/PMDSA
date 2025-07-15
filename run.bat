@echo off
setlocal enabledelayedexpansion

set PYTHON_SCRIPT=PMDSA.py

if "%~1"=="" (
    echo Usage: %~nx0 ^<root_directory^> [extra python args]
    exit /b 1
)

set ROOT_DIR=%~1
shift
set PY_ARGS=%*

:: === Recurse into subdirs ===
for /r "%ROOT_DIR%" %%D in (.) do (
    pushd "%%D" >nul

    set "SUBDIR=%%~fD"
    set "BASENAME=%%~nxD"
    set "CSV_NAME=!SUBDIR:%ROOT_DIR%=!"
    if "!CSV_NAME!"=="" set "CSV_NAME=!BASENAME!"
    set "CSV_FILE=!CSV_NAME!.csv"

    :: Clean previous file if exists
    > "!CSV_FILE!" echo Index,Filename,Seperation,Angle,Dmag

    set /a COUNT=0

    for %%F in (*.*) do (
        if exist "%%F" (
            set "FILENAME=%%~nxF"
            for /f "delims=" %%O in ('python "%PYTHON_SCRIPT%" "%%~fF" %PY_ARGS%') do (
                set "LINE=!COUNT!,!FILENAME!,%%O"
                >> "!CSV_FILE!" echo !LINE!
                set /a COUNT+=1
            )
        )
    )

    popd >nul
)

endlocal
