@ECHO OFF
SETLOCAL
SET _NT_SYMBOL_PATH=

IF "%~1" == "--all" (
  REM If you can add the x86 and x64 binaries of python to the path, or add links to the local folder, tests will be run
  REM in both
  WHERE PYTHON_X86 >nul 2>&1
  IF NOT ERRORLEVEL 0 (
    ECHO - PYTHON_X86 was not found; not testing both x86 and x64 ISAs.
  ) ELSE (
    WHERE PYTHON_X64 >nul 2>&1
    IF NOT ERRORLEVEL 0 (
      ECHO - PYTHON_X64 was not found; not testing both x86 and x64 ISAs.
    ) ELSE (
      GOTO :TEST_BOTH_ISAS
    )
  )
)

WHERE PYTHON 2>&1 >nul
IF ERRORLEVEL 1 (
  ECHO - PYTHON was not found!
  ENDLOCAL
  EXIT /B 1
)

ECHO * Running tests...
CALL PYTHON "%~dpn0\%~n0.py" %*
IF ERRORLEVEL 1 GOTO :ERROR
ENDLOCAL
GOTO :ADDITIONAL_TESTS

:TEST_BOTH_ISAS
  ECHO * Running tests in x86 build of Python...
  CALL PYTHON_X86 "%~dpn0\%~n0.py" %*
  IF ERRORLEVEL 1 GOTO :ERROR
  ECHO * Running tests in x64 build of Python...
  CALL PYTHON_X64 "%~dpn0\%~n0.py" %*
  IF ERRORLEVEL 1 GOTO :ERROR
  ENDLOCAL
  EXIT /B 0

:ADDITIONAL_TESTS
SET REDIRECT_STDOUT_FILE_PATH=%TEMP%\BugId Test stdout %RANDOM%.txt

ECHO   * Test version check...
CALL "%~dp0BugId.cmd" --version
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test verbose mode with redirected output... 
CALL "%~dp0BugId.cmd" --verbose %ComSpec% --cBugId.bEnsurePageHeap=false -- /C "@ECHO OFF" >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test repeat in fast mode...
CALL "%~dp0BugId.cmd" --repeat=2 --fast %ComSpec% --cBugId.bEnsurePageHeap=false -- /C "@ECHO OFF" >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR
IF EXIST "%~dp0Reproduction statistics.txt" DEL "%~dp0Reproduction statistics.txt"

ECHO   * Test usage help...
CALL "%~dp0BugId.cmd" --help >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test internal error reporting...
CALL "%~dp0BugId.cmd" --test-internal-error >"%REDIRECT_STDOUT_FILE_PATH%"
IF NOT ERRORLEVEL == 3 GOTO :ERROR
    DEL "%REDIRECT_STDOUT_FILE_PATH%" /Q

IF "%~1" == "--all" (
  ECHO   * Test debugging Google Chrome...
  CALL "%~dp0BugId.cmd" chrome --nApplicationMaxRunTimeInSeconds=10
  IF ERRORLEVEL 1 GOTO :ERROR
  ECHO   * Test debugging Microsoft Edge...
  CALL "%~dp0BugId.cmd" edge --nApplicationMaxRunTimeInSeconds=10
  IF ERRORLEVEL 1 GOTO :ERROR
  ECHO   * Test debugging Mozilla Firefox...
  CALL "%~dp0BugId.cmd" firefox --nApplicationMaxRunTimeInSeconds=10
  IF ERRORLEVEL 1 GOTO :ERROR
  ECHO   * Test debugging Microsoft Internet Explorer...
  CALL "%~dp0BugId.cmd" msie --nApplicationMaxRunTimeInSeconds=10
  IF ERRORLEVEL 1 GOTO :ERROR
)

ECHO   * Test MemGC.cmd...
CALL "%~dp0MemGC.cmd" ? >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test PageHeap.cmd...
CALL "%~dp0PageHeap.cmd" %ComSpec% ? >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR

DEL "%REDIRECT_STDOUT_FILE_PATH%" /Q

ECHO   + Passed unit-tests.
ENDLOCAL
EXIT /B 0

:ERROR
  ECHO     - Failed with error level %ERRORLEVEL%
  IF EXIST "%REDIRECT_STDOUT_FILE_PATH%" (
    TYPE "%REDIRECT_STDOUT_FILE_PATH%"
    DEL "%REDIRECT_STDOUT_FILE_PATH%" /Q
  )
  ENDLOCAL
  EXIT /B 3
