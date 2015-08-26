@ECHO OFF
IF "%PROCESSOR_ARCHITECTURE%" == "AMD64" (
  SET EdgeDbg=%~dp0..\..\C\EdgeDbg\Build\EdgeDbg_x64.exe
) ELSE (
  SET EdgeDbg=%~dp0..\..\C\EdgeDbg\Build\EdgeDbg_x86.exe
)
IF NOT EXIST "%PYTHON%" (
  ECHO Cannot find python at %PYTHON%.
  EXIT /B 1
)

IF NOT EXIST "%EdgeDbg%" (
  ECHO Cannot find EdgeDbg at %EdgeDbg%.
  EXIT /B 1
)
If "%~1" == "" (
  SET OpenURL=http://%COMPUTERNAME%:28876/
  SET CrashInfoArguments="--ci.bSaveReport=true"
) ELSE (
  SET OpenURL=%1
  SET CrashInfoArguments=%2 %3 %4 %5 %6 %7 %8 %9
)

ECHO * Terminating any running instancess of Microsoft Edge...
TASKKILL /F /IM MicrosoftEdge.exe 2>nul >nul
TASKKILL /F /IM browser_broker.exe 2>nul >nul
TASKKILL /F /IM RuntimeBroker.exe 2>nul >nul
TASKKILL /F /IM MicrosoftEdgeCP.exe 2>nul >nul

ECHO * Deleting crash recovery data...
DEL "%LOCALAPPDATA%\Packages\Microsoft.MicrosoftEdge_8wekyb3d8bbwe\AC\MicrosoftEdge\User\Default\Recovery\Active\*.*" /Q >nul

ECHO * Starting Microsoft Edge and CrashInfo...
ECHO   "%EdgeDbg%" %OpenURL% "%PYTHON%" %~dp0ci.py --pids=@ProcessIds@ %CrashInfoArguments%
"%EdgeDbg%" %OpenURL% "%PYTHON%" %~dp0ci.py --pids=@ProcessIds@ %CrashInfoArguments%