from mConsole import oConsole;

from dxConfig import dxConfig;
from mColorsAndChars import *;

def fCdbStdInInputCallbackHandler(oBugId, sbInput):
  if dxConfig["bQuiet"]:
    return;
  oConsole.fOutput(
    COLOR_INPUT, "<stdin<",
    COLOR_NORMAL, str(sbInput, 'latin1'),
    uConvertTabsToSpaces = 8,
  );
