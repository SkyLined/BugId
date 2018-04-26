@ECHO OFF

ECHO * Running unit-tests...

ECHO   * Test version check...
CALL "%~dp0BugId.cmd" --version %*
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test verbose mode with redirected output... 
CALL "%~dp0BugId.cmd" --verbose %ComSpec% --cBugId.bEnsurePageHeap=false -- /C "@ECHO OFF" >nul
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test repeat in fast mode...
CALL "%~dp0BugId.cmd" --repeat=2 --fast %ComSpec% --cBugId.bEnsurePageHeap=false -- /C "@ECHO OFF" >nul
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test usage help...
CALL "%~dp0BugId.cmd" --help %* >nul
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test internal error reporting...
CALL "%~dp0BugId.cmd" --test-internal-error %* >nul
IF NOT ERRORLEVEL == 3 GOTO :ERROR

IF "%~1" == "--extended" (
  ECHO   * Test debugging Google Chrome...
  CALL "%~dp0BugId.cmd" chrome --nApplicationMaxRunTime=10 %*
  IF ERRORLEVEL 1 GOTO :ERROR
  ECHO   * Test debugging Microsoft Edge...
  CALL "%~dp0BugId.cmd" edge --nApplicationMaxRunTime=10 %*
  IF ERRORLEVEL 1 GOTO :ERROR
  ECHO   * Test debugging Mozilla Firefox...
  CALL "%~dp0BugId.cmd" firefox --nApplicationMaxRunTime=10 %*
  IF ERRORLEVEL 1 GOTO :ERROR
  ECHO   * Test debugging Microsoft Internet Explorer...
  CALL "%~dp0BugId.cmd" msie --nApplicationMaxRunTime=10 %*
  IF ERRORLEVEL 1 GOTO :ERROR
)

ECHO   * Test MemGC.cmd...
CALL "%~dp0MemGC.cmd" ? >nul
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test PageHeap.cmd...
CALL "%~dp0PageHeap.cmd" %ComSpec% ? >nul
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   + Passed unit-tests.
EXIT /B 0

:ERROR
  ECHO     - Failed with error level %ERRORLEVEL%
  ENDLOCAL & EXIT /B %ERRORLEVEL%
