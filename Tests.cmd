@ECHO OFF

ECHO * Running unit-tests...

ECHO   * Test if BugId can debug cmd.exe...
CALL "BugId.cmd" %ComSpec% --nApplicationMaxRunTime=1 --cBugId.bEnsurePageHeap=false %*
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test if BugId can debug Google Chrome...
CALL "BugId.cmd" chrome --nApplicationMaxRunTime=10 %*
IF ERRORLEVEL 1 GOTO :ERROR
ECHO   * Test if BugId can debug Microsoft Edge...
CALL "BugId.cmd" edge --nApplicationMaxRunTime=10 %*
IF ERRORLEVEL 1 GOTO :ERROR
ECHO   * Test if BugId can debug Mozilla Firefox...
CALL "BugId.cmd" firefox --nApplicationMaxRunTime=10 %*
IF ERRORLEVEL 1 GOTO :ERROR
ECHO   * Test if BugId can debug Microsoft Internet Explorer...
CALL "BugId.cmd" msie --nApplicationMaxRunTime=10 %*
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test if BugId can run with redirected output...
CALL "BugId.cmd" %* >nul
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test if version checks work...
CALL "BugId.cmd" --version %* >nul
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test if usage help work...
CALL "BugId.cmd" --help %* >nul
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test if internal error reporting works...
CALL "BugId.cmd" --test-internal-error %* >nul
IF NOT ERRORLEVEL == 3 GOTO :ERROR

ECHO   * Test if MemGC.cmd can query MemGC settings...
CALL "MemGC.cmd" ? >nul
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test if PageHeap.cmd can query page heap settings...
CALL "PageHeap.cmd" %ComSpec% ? >nul
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   + Passed unit-tests.
EXIT /B 0

:ERROR
  ECHO     - Failed with error level %ERRORLEVEL%
  ENDLOCAL & EXIT /B %ERRORLEVEL%
