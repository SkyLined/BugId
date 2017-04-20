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
  :: 00000010 Enable heap tail checking
  :: 00000020 Enable heap free checking
  :: 00000040 Enable heap parameter checking
  :: 00000800 Enable heap tagging
  :: 00001000 Create user mode stack trace database
  :: 00008000 Enable heap tagging by DLL
  :: 00100000 Enable system critical breaks
  :: 02000000 Enable page heap (full page heap)
  :: ----------
  :: 02109870
  :: The following flags were considered but not enabled:
  :: 00000080 Enable heap validation on call ## disabled because of overhead
  :: 00000100 Enable application verifier ## disabled because of idunno
  :: 00200000 Disable heap coalesce on free ## superfluous: page heap is enabled
  :: 00400000 Enable close exception ## I don't think this is useful
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