@ECHO OFF
IF "%~1" == "ON" (
  ECHO NOTE: Firefox has its own heap manager. Turning page heap ON will not benefit you.
)
CALL PageHeap.cmd firefox.exe %1
CALL PageHeap.cmd plugin-container.exe %1
