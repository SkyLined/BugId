from dxConfig import dxConfig;
from foConsoleLoader import foConsoleLoader;
from mColorsAndChars import *;
oConsole = foConsoleLoader();

def fCdbStdErrOutputCallbackHandler(oBugId, sbOutput):
  if dxConfig["bQuiet"]:
    return;
  oConsole.fOutput(
    COLOR_ERROR, "stderr>",
    COLOR_NORMAL, str(sbOutput, 'latin1'),
    uConvertTabsToSpaces = 8,
  );
