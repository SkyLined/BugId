from dxConfig import dxConfig;
from foConsoleLoader import foConsoleLoader;
from fOutputMessageForProcess import fOutputMessageForProcess;
from mColorsAndChars import *;
oConsole = foConsoleLoader();

def fProcessTerminatedCallbackHandler(oBugId, oProcess, bIsMainProcess):
  bStopBugId = bIsMainProcess and dxConfig["bApplicationTerminatesWithMainProcess"];
  if not dxConfig["bQuiet"]:
    fOutputMessageForProcess(
      COLOR_REMOVE, CHAR_REMOVE,
      oProcess, bIsMainProcess,
      "Terminated", bStopBugId and "; the application is considered to have terminated with it." or ".",
    );
  if bStopBugId:
    oConsole.fStatus(COLOR_BUSY, CHAR_BUSY, COLOR_NORMAL, " BugId is stopping because a main process terminated...");
    oBugId.fStop();
