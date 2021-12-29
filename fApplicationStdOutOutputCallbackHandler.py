from dxConfig import dxConfig;
from fOutputMessageForProcess import fOutputMessageForProcess;
from mColorsAndChars import *;

def fApplicationStdOutOutputCallbackHandler(oBugId, oConsoleProcess, bIsMainProcess, sMessage):
  if dxConfig["bQuiet"]:
    return;
  fOutputMessageForProcess(
    COLOR_OUTPUT, CHAR_OUTPUT,
    oConsoleProcess, bIsMainProcess,
    COLOR_INFO, "stdout",
    COLOR_NORMAL, ">", sMessage,
  );
