@ECHO OFF
IF NOT "%~2" == "ON" IF NOT "%~2" == "OFF" GOTO :DO_NOT_REQUIRE_ADMIN
REM Setting the value requires administrator priviledges.
FSUTIL dirty query %systemdrive% >nul
IF ERRORLEVEL 1 (
  ECHO Please run as an administrator with elevated privileges.
  EXIT /B 1
)
:DO_NOT_REQUIRE_ADMIN

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
) ELSE IF "%~1" == "aoo-writer" (
  CALL :SET_OR_SHOW_PAGE_HEAP "swriter.exe" "%~2"
) ELSE IF "%~1" == "acrobat" (
  CALL :SET_OR_SHOW_PAGE_HEAP "AcroRd32.exe" "%~2"
) ELSE IF "%~1" == "acrobatdc" (
  CALL :SET_OR_SHOW_PAGE_HEAP "AdobeARM.exe" "%~2"
  CALL :SET_OR_SHOW_PAGE_HEAP "AcroRd32.exe" "%~2"
) ELSE IF "%~1" == "chrome" (
  IF "%~2" == "ON" (
    SET CHROME_ALLOCATOR=winheap
    "%WinDir%\System32\reg.exe" ADD "HKCU\Environment" /v "CHROME_ALLOCATOR" /t REG_SZ /d "winheap" /f
    IF ERRORLEVEL 1 (
      ECHO - Cannot set CHROME_ALLOCATOR enironment variable in the registry.
    )
  ) ELSE (
    SET CHROME_ALLOCATOR=
    "%WinDir%\System32\reg.exe" QUERY "HKCU\Environment" /v "CHROME_ALLOCATOR" >nul 2>&1
    IF NOT ERRORLEVEL 1 (
      "%WinDir%\System32\reg.exe" DELETE "HKCU\Environment" /v "CHROME_ALLOCATOR" /f >nul
      IF ERRORLEVEL 1 (
        ECHO - Cannot remove CHROME_ALLOCATOR enironment variable from the registry.
      )
    )
  )
  ECHO Note: switching page heap on or off for Chrome requires the CHROME_ALLOCATOR
  ECHO environment variable to be set to "winheap" or be unset respectively. This
  ECHO change has been applied through the registry and in the current process'
  ECHO environment, but you may want to log off and on again to make sure this is
  ECHO applied to all processes.
  CALL :SET_OR_SHOW_PAGE_HEAP "chrome.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_OR_SHOW_PAGE_HEAP "software_reporter_tool.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
) ELSE IF "%~1" == "edge" (
  CALL :SET_OR_SHOW_PAGE_HEAP "ApplicationFrameHost.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_OR_SHOW_PAGE_HEAP "browser_broker.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_OR_SHOW_PAGE_HEAP "MicrosoftEdge.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_OR_SHOW_PAGE_HEAP "MicrosoftEdgeCP.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_OR_SHOW_PAGE_HEAP "RuntimeBroker.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
) ELSE IF "%~1" == "firefox" (
  CALL :SET_OR_SHOW_PAGE_HEAP "firefox.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_OR_SHOW_PAGE_HEAP "helper.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_OR_SHOW_PAGE_HEAP "updater.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_OR_SHOW_PAGE_HEAP "plugin-container.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_OR_SHOW_PAGE_HEAP "pingsender.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  REM Firefox uses regsvr32.exe to register AccessibleHandler.dll
  CALL :SET_OR_SHOW_PAGE_HEAP "regsvr32.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  IF "%~1" == "ON" (
    ECHO NOTE: Firefox has its own heap manager, so heap corruption detection is not as
    ECHO good as it could be.
  )
) ELSE IF "%~1" == "flash" (
  FOR %%I IN ("%SystemRoot%\SysWOW64\Macromed\Flash\FlashPlayerPlugin_*.exe", "%SystemRoot%\System32\Macromed\Flash\FlashPlayerPlugin_*.exe") DO (
    CALL :SET_OR_SHOW_PAGE_HEAP ""%%~nxI.exe" %1
    IF ERRORLEVEL 1 EXIT /B 1
  )
) ELSE IF "%~1" == "foxit" (
  CALL :SET_OR_SHOW_PAGE_HEAP "FoxitReader.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_OR_SHOW_PAGE_HEAP "FoxitReader_Lib_Full.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
) ELSE IF "%~1" == "java" (
  CALL :SET_OR_SHOW_PAGE_HEAP "java.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
) ELSE IF "%~1" == "msie" (
  CALL :SET_OR_SHOW_PAGE_HEAP "iexplore.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  REM I saw iexplore.exe spawn rundll32.exe once, so I'm adding it:
  CALL :SET_OR_SHOW_PAGE_HEAP "rundll32.exe" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
) ELSE (
  CALL :SET_OR_SHOW_PAGE_HEAP "%~1" "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
)
EXIT /B 0

:SHOW_USAGE
  ECHO Usage:
  ECHO   %~nx0 ^<binary file name^> [ON^|OFF]
  ECHO Or:
  ECHO   %~nx0 ^<known application^> [ON^|OFF]
  ECHO Where known application is one of:
  ECHO   aoo-writer       Apache OpenOffice Writer
  ECHO   acrobat          Adobe Acrobat Reader
  ECHO   acrobatdc        Adobe Acrobat Reader DC
  ECHO   chrome           Google Chrome
  ECHO   edge             Microsoft Edge
  ECHO   firefox          Mozilla Firefox
  ECHO   flash            Adobe Flash
  ECHO   foxit            Foxit Reader
  ECHO   msie             Microsoft Internet Explorer
  EXIT /B 0

:SET_OR_SHOW_PAGE_HEAP
  REM 00000010 Enable heap tail checking
  REM 00000020 Enable heap free checking
  REM 00000040 Enable heap parameter checking
  REM 00001000 Create user mode stack trace database
  REM 00008000 Enable heap tagging by DLL
  REM 00100000 Enable system critical breaks
  REM 02000000 Enable page heap (full page heap)
  REM ----------
  REM 02109870 =
  
  REM The following flags were considered but not enabled:
  REM 00000080 Enable heap validation on call ## disabled because of overhead
  REM 00000800 Enable heap tagging ## disabled because tags are not used.
  REM 00000100 Enable application verifier ## disabled because of idunno
  REM 00200000 Disable heap coalesce on free ## superfluous: page heap is enabled
  REM 00400000 Enable close exception ## I don't think this is useful
  IF "%~2" == "OFF" (
    ECHO * Disabling page heap for binary %~1...
    "%WinDir%\System32\reg.exe" ADD "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\%~1" /v "GlobalFlag" /t REG_SZ /d "0x00000000" /f >nul
    IF ERRORLEVEL 1 GOTO :ERROR
  ) ELSE IF "%~2" == "ON" (
    ECHO * Enabling page heap for binary %~1...
    "%WinDir%\System32\reg.exe" ADD "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\%~1" /v "GlobalFlag" /t REG_SZ /d "0x02109870" /f >nul
    IF ERRORLEVEL 1 GOTO :ERROR
  ) ELSE IF "%~2" == "" (
    ECHO * Querying current page heap flags for binary %~1...
    "%WinDir%\System32\reg.exe" QUERY "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\%~1" /v "GlobalFlag" >nul 2>nul
    IF ERRORLEVEL 1 (
      ECHO   - Page heap is OFF.
    ) ELSE (
      REM For some obscure reason I cannot put quotes around the reg.exe path because it causes an error:
      REM "The system cannot find the path specified."
      FOR /F "usebackq tokens=3" %%I IN (`%WinDir%\System32\reg.exe QUERY "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\%~1" /v "GlobalFlag" ^| "%WinDir%\System32\find.exe" "GlobalFlag"`) DO (
        IF "%%~I" == "0x02109870" (
          ECHO   + Page heap is ON ^(0x02109870^).
        ) ELSE IF "%%~I" == "0x00000000" (
          ECHO   - Page heap is OFF.
        ) ELSE (
          ECHO   * Page heap flags are %%~I.
        )
      )
    )
  ) ELSE IF "%~2" == "?" (
    CALL :SHOW_PAGE_HEAP "%~1"
  ) ELSE (
    CALL :SHOW_USAGE
    EXIT /B 1
  )
  EXIT /B 0

:SHOW_PAGE_HEAP
  "%WinDir%\System32\reg.exe" QUERY "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\%~1" /v "GlobalFlag" 2>nul >nul
  IF ERRORLEVEL 1 (
    ECHO - Page heap is disabled for binary %~1.
    EXIT /B 0
  )
  "%WinDir%\System32\reg.exe" QUERY "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\%~1" /v "GlobalFlag" | "%WinDir%\System32\find.exe" "0x02109870" > nul
  IF %ERRORLEVEL% == 0 (
    ECHO + Page heap is enabled for binary %~1.
    EXIT /B 0
  )
  "%WinDir%\System32\reg.exe" QUERY "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\%~1" /v "GlobalFlag" | "%WinDir%\System32\find.exe" "0x00000000" > nul
  IF %ERRORLEVEL% == 0 (
    ECHO - Page heap is disabled for binary %~1.
    EXIT /B 0
  )
  ECHO * Custom page heap settings are enabled for binary %~1:
  "%WinDir%\System32\reg.exe" QUERY "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\%~1" /v "GlobalFlag" | "%WinDir%\System32\find.exe" "GlobalFlag"
  EXIT /B 1

:ERROR
  ECHO - Error code %ERRORLEVEL%.
  EXIT /B %ERRORLEVEL%