@ECHO OFF
SETLOCAL
NET SESSION >nul 2>&1
IF ERRORLEVEL 1 (
  ECHO - Must be run as administrator.
  EXIT /B 1
)
IF NOT DEFINED GFlags (
  CALL :SET_GFLAGS_%PROCESSOR_ARCHITECTURE%
  IF NOT DEFINED GFlags (
    ECHO - Cannot find gflags.exe, please set the "GFlags" environment variable to the correct path.
    EXIT /B 1
  )
) ELSE (
  SET GFlags="%GFlags:"=%"
)
IF NOT EXIST %GFlags% (
  ECHO - Cannot find gflags.exe at %GFlags%, please set the "GFlags" environment variable to the correct path.
  EXIT /B 1
)

IF "%~2" == "OFF" (
  ECHO * Disabling page heap for %1...
  %GFlags% -i %1 -FFFFFFFF >nul
  IF ERRORLEVEL 1 GOTO :ERROR
) ELSE IF "%~2" == "ON" (
  ECHO * Enabling page heap for %1...
  %GFlags% -i %1 -FFFFFFFF >nul
  IF ERRORLEVEL 1 GOTO :ERROR
  %GFlags% -i %1 +02109870 >nul
  IF ERRORLEVEL 1 GOTO :ERROR
) ELSE (
  ECHO Usage:
  ECHO   %~nx0 ^<binary file name^> [ON^|OFF]
)
EXIT /B 0

:SET_GFLAGS_AMD64
  CALL :SET_GFLAGS_IF_EXISTS "%ProgramFiles%\Windows Kits\10\Debuggers\x64\gflags.exe"
  CALL :SET_GFLAGS_IF_EXISTS "%ProgramFiles(x86)%\Windows Kits\10\Debuggers\x64\gflags.exe"
  CALL :SET_GFLAGS_IF_EXISTS "%ProgramFiles%\Windows Kits\8.1\Debuggers\x64\gflags.exe"
  CALL :SET_GFLAGS_IF_EXISTS "%ProgramFiles(x86)%\Windows Kits\8.1\Debuggers\x64\gflags.exe"
  CALL :SET_GFLAGS_IF_EXISTS "%ProgramFiles%\Windows Kits\8.0\Debuggers\x64\gflags.exe"
  CALL :SET_GFLAGS_IF_EXISTS "%ProgramFiles(x86)%\Windows Kits\8.0\Debuggers\x64\gflags.exe"
  EXIT /B 0

:SET_GFLAGS_x86
  CALL :SET_GFLAGS_IF_EXISTS "%ProgramFiles%\Windows Kits\10\Debuggers\x86\gflags.exe"
  CALL :SET_GFLAGS_IF_EXISTS "%ProgramFiles%\Windows Kits\8.1\Debuggers\x86\gflags.exe"
  CALL :SET_GFLAGS_IF_EXISTS "%ProgramFiles%\Windows Kits\8.0\Debuggers\x86\gflags.exe"
  EXIT /B 0

:SET_GFLAGS_IF_EXISTS
  IF NOT DEFINED GFlags (
    IF EXIST "%~1" (
      SET GFlags="%~1"
    )
  )
  EXIT /B 0

:ERROR
  ECHO - Error code %ERRORLEVEL%.
  EXIT /B %ERRORLEVEL%