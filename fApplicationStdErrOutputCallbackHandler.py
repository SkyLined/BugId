from dxConfig import dxConfig;
from fOutputMessageForProcess import fOutputMessageForProcess;
from mColorsAndChars import *;

def fApplicationStdErrOutputCallbackHandler(oBugId, oConsoleProcess, bIsMainProcess, sMessage):
  if dxConfig["bQuiet"]:
    return;
  fOutputMessageForProcess(
    COLOR_OUTPUT, CHAR_OUTPUT,
    oConsoleProcess, bIsMainProcess,
    COLOR_ERROR, "stderr",
    COLOR_NORMAL, ">",
    COLOR_ERROR, sMessage,
  );
