@ECHO OFF
SETLOCAL
SET REDIRECT_STDOUT_FILE_PATH=%TEMP%\BugId Test stdout %RANDOM%.txt

ECHO   * Test usage help...
CALL "%~dp0\..\BugId.cmd" --help >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR
ECHO   * Test version info...
CALL "%~dp0\..\BugId.cmd" --version >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR
ECHO   * Test version check...
CALL "%~dp0\..\BugId.cmd" --version-check >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR
ECHO   * Test license info...
CALL "%~dp0\..\BugId.cmd" --license >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR
ECHO   * Test license update...
CALL "%~dp0\..\BugId.cmd" --license-update >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR

SET _NT_SYMBOL_PATH=

ECHO   * Test verbose mode with redirected output... 
CALL "%~dp0\..\BugId.cmd" --verbose %ComSpec% --cBugId.bEnsurePageHeap=false -- /C "@ECHO OFF" >"%REDIRECT_STDOUT_FILE_PATH%"
REM See `mExitCodes.py` for expected exit code.
IF NOT "%ERRORLEVEL%" == "11" GOTO :ERROR

ECHO   * Test repeat in fast mode...
CALL "%~dp0\..\BugId.cmd" --repeat=2 --fast %ComSpec% --cBugId.bEnsurePageHeap=false -- /C "@ECHO OFF" >"%REDIRECT_STDOUT_FILE_PATH%"
REM See `mExitCodes.py` for expected exit code.
IF NOT "%ERRORLEVEL%" == "11" GOTO :ERROR
IF EXIST "%~dp0\Reproduction statistics.txt" DEL "%~dp0\Reproduction statistics.txt"

ECHO   * Test internal error reporting...
CALL "%~dp0\..\BugId.cmd" --test-internal-error >"%REDIRECT_STDOUT_FILE_PATH%"
REM See `mExitCodes.py` for expected exit code.
IF NOT "%ERRORLEVEL%" == "1" GOTO :ERROR

IF "%~1" == "--all" (
  ECHO   * Test debugging Google Chrome...
  CALL "%~dp0\..\BugId.cmd" chrome --nApplicationMaxRunTimeInSeconds=10
  REM See `mExitCodes.py` for expected exit code.
  IF NOT "%ERRORLEVEL%" == "11" GOTO :ERROR
  ECHO   * Test debugging Microsoft Edge...
  CALL "%~dp0\..\BugId.cmd" edge --nApplicationMaxRunTimeInSeconds=10
  REM See `mExitCodes.py` for expected exit code.
  IF NOT "%ERRORLEVEL%" == "11" GOTO :ERROR
  ECHO   * Test debugging Mozilla Firefox...
  CALL "%~dp0\..\BugId.cmd" firefox --nApplicationMaxRunTimeInSeconds=10
  REM See `mExitCodes.py` for expected exit code.
  IF NOT "%ERRORLEVEL%" == "11" GOTO :ERROR
  ECHO   * Test debugging Microsoft Internet Explorer...
  CALL "%~dp0\..\BugId.cmd" msie --nApplicationMaxRunTimeInSeconds=10
  REM See `mExitCodes.py` for expected exit code.
  IF NOT "%ERRORLEVEL%" == "11" GOTO :ERROR
)

ECHO   * Test MemGC.cmd...
CALL "%~dp0\..\MemGC.cmd" ? >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test PageHeap.cmd...
CALL "%~dp0\..\PageHeap.cmd" %ComSpec% ? >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR

DEL "%REDIRECT_STDOUT_FILE_PATH%" /Q

ECHO + Test.cmd completed.
ENDLOCAL
EXIT /B 0

:ERROR
  ECHO     - Failed with error level %ERRORLEVEL%
  CALL :CLEANUP
  ENDLOCAL
  EXIT /B 3

:CLEANUP
  IF EXIST "%REDIRECT_STDOUT_FILE_PATH%" (
    POWERSHELL $OutputEncoding = New-Object -Typename System.Text.UTF8Encoding; Get-Content -Encoding utf8 '"%REDIRECT_STDOUT_FILE_PATH%"'
    DEL "%REDIRECT_STDOUT_FILE_PATH%" /Q
  )
