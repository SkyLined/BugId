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
  CALL :SET_PAGE_HEAP swriter.exe "%~2"
) ELSE IF "%~1" == "acrobat" (
  CALL :SET_PAGE_HEAP AcroRd32.exe "%~2"
) ELSE IF "%~1" == "acrobatdc" (
  CALL :SET_PAGE_HEAP AdobeARM.exe "%~2"
  CALL :SET_PAGE_HEAP AcroRd32.exe "%~2"
) ELSE IF "%~1" == "chrome" (
  IF "%~2" == "ON" (
    SET CHROME_ALLOCATOR=winheap
    REG ADD "HKCU\Environment" /v "CHROME_ALLOCATOR" /t REG_SZ /d "winheap" /f
    IF ERRORLEVEL 1 (
      ECHO - Cannot set CHROME_ALLOCATOR enironment variable in the registry.
    )
  ) ELSE (
    SET CHROME_ALLOCATOR=
    REG QUERY "HKCU\Environment" /v "CHROME_ALLOCATOR" >nul 2>&1
    IF NOT ERRORLEVEL 1 (
      REG DELETE "HKCU\Environment" /v "CHROME_ALLOCATOR" /f >nul
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
  CALL :SET_PAGE_HEAP chrome.exe "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_PAGE_HEAP software_reporter_tool.exe "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
) ELSE IF "%~1" == "edge" (
  CALL :SET_PAGE_HEAP ApplicationFrameHost.exe "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_PAGE_HEAP browser_broker.exe "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_PAGE_HEAP MicrosoftEdge.exe "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_PAGE_HEAP MicrosoftEdgeCP.exe "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_PAGE_HEAP RuntimeBroker.exe "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
) ELSE IF "%~1" == "firefox" (
  CALL :SET_PAGE_HEAP firefox.exe "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_PAGE_HEAP helper.exe "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_PAGE_HEAP updater.exe "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_PAGE_HEAP plugin-container.exe "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  IF "%~1" == "ON" (
    ECHO NOTE: Firefox has its own heap manager, so heap corruption detection is not as
    ECHO good as it could be.
  )
) ELSE IF "%~1" == "flash" (
  FOR %%I IN ("%SystemRoot%\SysWOW64\Macromed\Flash\FlashPlayerPlugin_*.exe", "%SystemRoot%\System32\Macromed\Flash\FlashPlayerPlugin_*.exe") DO (
    CALL :SET_PAGE_HEAP "%%~nxI.exe" %1
    IF ERRORLEVEL 1 EXIT /B 1
  )
) ELSE IF "%~1" == "foxit" (
  CALL :SET_PAGE_HEAP FoxitReader.exe "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :SET_PAGE_HEAP FoxitReader_Lib_Full.exe "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
) ELSE IF "%~1" == "msie" (
  CALL :SET_PAGE_HEAP iexplore.exe "%~2"
  IF ERRORLEVEL 1 EXIT /B 1
) ELSE (
  CALL :SET_PAGE_HEAP "%~1" "%~2"
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

:SET_PAGE_HEAP
  IF "%~2" == "OFF" (
    ECHO * Disabling page heap for binary %1...
    %GFlags% -i %1 -FFFFFFFF >nul
    IF ERRORLEVEL 1 GOTO :ERROR
  ) ELSE IF "%~2" == "ON" (
    ECHO * Enabling page heap for binary %1...
    %GFlags% -i %1 -FFFFFFFF >nul
    IF ERRORLEVEL 1 GOTO :ERROR
    REM 00000010 Enable heap tail checking
    REM 00000020 Enable heap free checking
    REM 00000040 Enable heap parameter checking
    REM 00000800 Enable heap tagging
    REM 00001000 Create user mode stack trace database
    REM 00008000 Enable heap tagging by DLL
    REM 00100000 Enable system critical breaks
    REM 02000000 Enable page heap (full page heap)
    REM ----------
    REM 02109870
    REM The following flags were considered but not enabled:
    REM 00000080 Enable heap validation on call ## disabled because of overhead
    REM 00000100 Enable application verifier ## disabled because of idunno
    REM 00200000 Disable heap coalesce on free ## superfluous: page heap is enabled
    REM 00400000 Enable close exception ## I don't think this is useful
    %GFlags% -i %1 +02109870 >nul
    IF ERRORLEVEL 1 GOTO :ERROR
  ) ELSE IF "%~2" == "" (
    %GFlags% -i %1
    IF ERRORLEVEL 1 GOTO :ERROR
  ) ELSE (
    CALL :SHOW_USAGE
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