@ECHO OFF
IF "%~1" == "ON" (
  SET CHROME_ALLOCATOR=winheap
  REG ADD "HKCU\Environment" /v "CHROME_ALLOCATOR" /t REG_SZ /d "winheap" /f
) ELSE (
  SET CHROME_ALLOCATOR=
  REG DELETE "HKCU\Environment" /v "CHROME_ALLOCATOR" /f
)
IF ERRORLEVEL 1 (
  ECHO - Cannot set CHROME_ALLOCATOR enironment variable in the registry.
)
CALL PageHeap.cmd chrome.exe %1
ECHO Note: switching page heap on or off for Chrome requires the CHROME_ALLOCATOR
ECHO environment variable to be set to "winheap" or be unset respectively. This
ECHO change has been applied through the registry and in the current process'
ECHO environment, but you may want to log off and on again to make sure this is
ECHO applied to all processes.