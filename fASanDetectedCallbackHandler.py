from dxConfig import dxConfig;
from fOutputMessageForProcess import fOutputMessageForProcess;
from mColorsAndChars import *;

def fASanDetectedCallbackHandler(oBugId, oProcess, bIsMainProcess):
  if dxConfig["bQuiet"]:
    return;
  fOutputMessageForProcess(
    COLOR_OK, CHAR_OK,
    oProcess, bIsMainProcess, 
    " has ",
    COLOR_INFO, "Address Sanitizer",
    COLOR_NORMAL, " enabled."
  );
