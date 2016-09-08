@ECHO OFF
IF "%~1" == "ON" (
  ECHO NOTE: Chrome has its own heap manager. Turning page heap ON will not benefit you.
)
CALL PageHeap.cmd chrome.exe %1
