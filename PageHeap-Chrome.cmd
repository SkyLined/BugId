@ECHO OFF
IF "%~1" == "ON" (
  REG ADD "HKCU\Environment" /v "CHROME_ALLOCATOR" /t REG_SZ /d "winheap" /f
  SET CHROME_ALLOCATOR=winheap
) ELSE (
  REG DEL "HKCU\Environment" /v "CHROME_ALLOCATOR" /f
  SET CHROME_ALLOCATOR=
)
CALL PageHeap.cmd chrome.exe %1
ECHO Note that page heap for Chrome requires an environment variable to be set.
ECHO You may need to log off and on again to make sure this is done.