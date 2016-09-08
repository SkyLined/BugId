@ECHO OFF
FOR %%I IN (%SystemRoot%\SysWOW64\Macromed\Flash\FlashPlayerPlugin_*.exe,%SystemRoot%\System32\Macromed\Flash\FlashPlayerPlugin_*.exe) DO (
  CALL PageHeap.cmd "%%~nxI.exe" %1
  IF ERRORLEVEL 1 EXIT /B 1
)
