@ECHO OFF
FSUTIL dirty query %systemdrive% >nul
IF ERRORLEVEL 1 (
  ECHO Please run as an administrator.
  EXIT /B 1
)

IF "%~1" == "ON" (
  ECHO * Enabling MemGC...
  REG ADD "HKCU\SOFTWARE\Microsoft\Internet Explorer\Main" /v "OverrideMemoryProtectionSetting" /t REG_DWORD /d 3 /f >nul
) ELSE IF "%~1" == "OFF" (
  ECHO * Disabling MemGC...
  REG ADD "HKCU\SOFTWARE\Microsoft\Internet Explorer\Main" /v "OverrideMemoryProtectionSetting" /t REG_DWORD /d 0 /f >nul
) ELSE (
  ECHO Usage: MemGC.cmd [ON^|OFF]
  EXIT /B 1
)
IF ERRORLEVEL 1 GOTO :ERROR

EXIT /B 0
:ERROR
  ECHO - Error %ERRORLEVEL%.
  PAUSE
  EXIT /B %ERRORLEVEL%
