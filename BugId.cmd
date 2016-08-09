@ECHO OFF
SETLOCAL
IF NOT DEFINED PYTHON (
  SET PYTHON="%SystemDrive%\Python27\python.exe"
) ELSE (
  SET PYTHON="%PYTHON:"=%"
)
IF NOT EXIST %PYTHON% (
  ECHO - Cannot find Python at %PYTHON%, please set the "PYTHON" environment variable to the correct path.
  EXIT /B 1
)

%PYTHON% "%~dpn0.py" %*
EXIT /B %ERRORLEVEL%
