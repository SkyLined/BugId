from dxConfig import dxConfig;
from foConsoleLoader import foConsoleLoader;
from mColorsAndChars import *;
oConsole = foConsoleLoader();

def fLogMessageCallbackHandler(oBugId, sMessage, dsData = None):
  if dxConfig["bQuiet"]:
    return;
  sData = dsData and ", ".join(["%s: %s" % (sName, sValue) for (sName, sValue) in dsData.items()]);
  oConsole.fOutput(
    COLOR_DIM, "log>", sMessage, sData and " (%s)" % sData or [],
  );
