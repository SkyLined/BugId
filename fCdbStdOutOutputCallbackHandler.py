from dxConfig import dxConfig;
from foConsoleLoader import foConsoleLoader;
from mColorsAndChars import *;
oConsole = foConsoleLoader();

def fCdbStdOutOutputCallbackHandler(oBugId, sbOutput):
  if dxConfig["bQuiet"]:
    return;
  oConsole.fOutput(
    COLOR_OUTPUT, "stdout>",
    COLOR_NORMAL, str(sbOutput, 'latin1'),
    uConvertTabsToSpaces = 8,
  );
