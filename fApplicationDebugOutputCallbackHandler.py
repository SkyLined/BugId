from dxConfig import dxConfig;
from foConsoleLoader import foConsoleLoader;
from fOutputMessageForProcess import fOutputMessageForProcess;
from mColorsAndChars import *;
oConsole = foConsoleLoader();

def fApplicationDebugOutputCallbackHandler(oBugId, oProcess, bIsMainProcess, asbMessages):
  if dxConfig["bQuiet"]:
    return;
  uLineNumber = 0;
  sDebug = "debug";
  oConsole.fLock();
  for sbMessage in asbMessages:
    uLineNumber += 1;
    if uLineNumber == 1:
      # we will create a box shape to show which messages belong together.
      # On the first line we will branch down and right if the message is multi-line.
      sPrefix = " " if len(asbMessages) == 1 else "";
    else:
      # if more lines folow, show a vertical stripe, otherwise bend right on the last line
      sPrefix = "" if uLineNumber == len(asbMessages) else "";
    fOutputMessageForProcess(
      COLOR_OUTPUT, CHAR_OUTPUT if uLineNumber == 1 else None,
      oProcess, bIsMainProcess,
      COLOR_INFO, "debug",
      COLOR_NORMAL, sPrefix,
      COLOR_HILITE, str(sbMessage, 'latin1'),
    );
    sDebug = "     ";
  oConsole.fUnlock();

