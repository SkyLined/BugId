from dxConfig import dxConfig;
from foConsoleLoader import foConsoleLoader;
from mColorsAndChars import *;
oConsole = foConsoleLoader();

def fCdbStdInInputCallbackHandler(oBugId, sbInput):
  if dxConfig["bQuiet"]:
    return;
  oConsole.fOutput(
    COLOR_INPUT, "<stdin<",
    COLOR_NORMAL, str(sbInput, 'latin1'),
    uConvertTabsToSpaces = 8,
  );
