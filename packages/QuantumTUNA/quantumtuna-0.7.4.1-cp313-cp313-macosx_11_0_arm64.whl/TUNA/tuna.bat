@echo off
SETLOCAL
BREAK OFF  REM Disable Ctrl+C prompt

set "scriptDir=%~dp0"

if "%1"=="--version" (
    for /f "tokens=2 delims== " %%i in ('findstr /r /c:__version__ "%scriptDir%__init__.py"') do (
        set "version=%%i"
        call :stripQuotes
    )
) else (
	REM Run Python without showing Ctrl+C prompt
    python "%scriptDir%tuna.py" %*
)

endlocal
goto :eof

:stripQuotes

set "version=%version:"=%"
echo %version%
goto :eof
