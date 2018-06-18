@ECHO OFF

IF "%~1" == "" (
  CALL :SHOW_USAGE
) ELSE IF "%~1" == "-?" (
  CALL :SHOW_USAGE
) ELSE IF "%~1" == "-h" (
  CALL :SHOW_USAGE
) ELSE IF "%~1" == "/?" (
  CALL :SHOW_USAGE
) ELSE IF "%~1" == "/h" (
  CALL :SHOW_USAGE
) ELSE IF "%~1" == "ON" (
  ECHO * Enabling MemGC...
  "%WinDir%\System32\reg.exe" ADD "HKCU\SOFTWARE\Microsoft\Internet Explorer\Main" /v "OverrideMemoryProtectionSetting" /t REG_DWORD /d 3 /f >nul
  IF ERRORLEVEL 1 GOTO :ERROR
  CALL :SHOW_STATE
  IF ERRORLEVEL 1 GOTO :ERROR
) ELSE IF "%~1" == "OFF" (
  ECHO * Disabling MemGC...
  "%WinDir%\System32\reg.exe" ADD "HKCU\SOFTWARE\Microsoft\Internet Explorer\Main" /v "OverrideMemoryProtectionSetting" /t REG_DWORD /d 0 /f >nul
  IF ERRORLEVEL 1 GOTO :ERROR
  CALL :SHOW_STATE
  IF ERRORLEVEL 1 GOTO :ERROR
) ELSE IF "%~1" == "?" (
  CALL :SHOW_STATE
  IF ERRORLEVEL 1 GOTO :ERROR
) ELSE (
  CALL :SHOW_USAGE
)
EXIT /B 0

:SHOW_USAGE
  ECHO Usage:
  ECHO   %~nx0 [ON^|OFF]
  ECHO   To enable or disable MemGC.
  ECHO Or:
  ECHO   %~nx0 ?
  ECHO    To query the current state of MemGC without modifying it.
  EXIT /B 0

:SHOW_STATE
  REM Query the MemGC setting and display the current state if known.
  "%WinDir%\System32\reg.exe" QUERY "HKCU\SOFTWARE\Microsoft\Internet Explorer\Main" /v "OverrideMemoryProtectionSetting" 2>&1 | "%WinDir%\System32\find.exe" "ERROR: The system was unable to find the specified registry key or value." >nul
  IF %ERRORLEVEL% == 0 (
    ECHO + MemGC is enabled ^(default setting^).
    EXIT /B 0
  )

  "%WinDir%\System32\reg.exe" QUERY "HKCU\SOFTWARE\Microsoft\Internet Explorer\Main" /v "OverrideMemoryProtectionSetting" | "%WinDir%\System32\find.exe" "0x3" >nul
  IF %ERRORLEVEL% == 0 (
    ECHO + MemGC is enabled.
    EXIT /B 0
  )
  "%WinDir%\System32\reg.exe" QUERY "HKCU\SOFTWARE\Microsoft\Internet Explorer\Main" /v "OverrideMemoryProtectionSetting" | "%WinDir%\System32\find.exe" "0x2" >nul
  IF %ERRORLEVEL% == 0 (
    ECHO - MemGC is disabled, Memory protector is enabled with forced mark-and-reclaim.
    EXIT /B 0
  )
  "%WinDir%\System32\reg.exe" QUERY "HKCU\SOFTWARE\Microsoft\Internet Explorer\Main" /v "OverrideMemoryProtectionSetting" | "%WinDir%\System32\find.exe" "0x1" >nul
  IF %ERRORLEVEL% == 0 (
    ECHO - MemGC is disabled, Memory protector is enabled.
    EXIT /B 0
  )
  "%WinDir%\System32\reg.exe" QUERY "HKCU\SOFTWARE\Microsoft\Internet Explorer\Main" /v "OverrideMemoryProtectionSetting" | "%WinDir%\System32\find.exe" "0x0" >nul
  IF %ERRORLEVEL% == 0 (
    ECHO - MemGC and Memory protector are disabled.
    EXIT /B 0
  )
  ECHO - Error: Unknown "OverrideMemoryProtectionSetting" value:
  "%WinDir%\System32\reg.exe" QUERY "HKCU\SOFTWARE\Microsoft\Internet Explorer\Main" /v "OverrideMemoryProtectionSetting" | "%WinDir%\System32\find.exe" "OverrideMemoryProtectionSetting"
  PAUSE
  EXIT /B 1

:ERROR
  ECHO - Error %ERRORLEVEL%.
  PAUSE
  EXIT /B %ERRORLEVEL%
