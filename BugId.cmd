@ECHO OFF
SETLOCAL
IF DEFINED PYTHON (
  CALL :CHECK_PYTHON
  IF NOT ERRORLEVEL 1 GOTO :RUN_PYTHON
)
REM Try to detect the location of python automatically
FOR /F "usebackq delims=" %%I IN (`where "python" 2^>nul`) DO (
  SET PYTHON="%%~fI"
  CALL :CHECK_PYTHON
  IF NOT ERRORLEVEL 1 GOTO :RUN_PYTHON
)
REM Check if python is found in its default installation path.
FOR /D %%I IN ("%LOCALAPPDATA%\Programs\Python\*") DO (
  SET PYTHON="%%~fI\python.exe"
  CALL :CHECK_PYTHON
  IF NOT ERRORLEVEL 1 GOTO :RUN_PYTHON
)
ECHO - Cannot find python.exe, please set the "PYTHON" environment variable to the
ECHO   correct path, or add Python to the "PATH" environment variable.
EXIT /B 1

:CHECK_PYTHON
  REM Make sure path is quoted and check if it exists.
  SET PYTHON="%PYTHON:"=%"
  IF NOT EXIST %PYTHON% EXIT /B 1
  EXIT /B 0

:RUN_PYTHON
  CALL %PYTHON% "%~dpn0.py" %*
  ENDLOCAL & EXIT /B %ERRORLEVEL%
