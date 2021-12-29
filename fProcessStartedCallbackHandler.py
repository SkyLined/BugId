from dxConfig import dxConfig;
from fOutputMessageForProcess import fOutputMessageForProcess;
from mColorsAndChars import *;

def fProcessStartedCallbackHandler(oBugId, oConsoleProcess, bIsMainProcess):
  if dxConfig["bVerbose"]:
    fOutputMessageForProcess(
      COLOR_ADD, CHAR_ADD,
      oConsoleProcess, bIsMainProcess,
      "Started (",
      COLOR_INFO, oConsoleProcess.sCommandLine,
      COLOR_NORMAL, ").",
    );
