@ECHO OFF
SETLOCAL
NET SESSION >nul 2>&1
IF ERRORLEVEL 1 (
  ECHO - Must be run as administrator.
  EXIT /B 1
)
IF NOT "%GFlags:~0,0%" == "" (
  IF "%PROCESSOR_ARCHITECTURE%" == "AMD64" (
    SET GFlags=C:\Program Files\Windows Kits\8.1\Debuggers\x64\gflags.exe
  ) ELSE (
    SET GFlags=C:\Program Files\Windows Kits\8.1\Debuggers\x86\gflags.exe
  )
)
IF NOT EXIST "%GFlags:"=%" (
  ECHO - Cannot find Global Flags at %GFlags%, please set the "GFlags" environment variable to the correct path.
  EXIT /B 1
)
IF "%~2" == "OFF" (
  "%GFlags%" -i %1 -FFFFFFFF
) ELSE (
  "%GFlags%" -i %1 -FFFFFFFF >nul
  "%GFlags%" -i %1 +02109870
)
