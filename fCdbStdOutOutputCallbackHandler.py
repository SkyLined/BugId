from mConsole import oConsole;

from dxConfig import dxConfig;
from mColorsAndChars import *;

def fCdbStdOutOutputCallbackHandler(oBugId, sbOutput):
  if dxConfig["bQuiet"]:
    return;
  oConsole.fOutput(
    COLOR_OUTPUT, "stdout>",
    COLOR_NORMAL, str(sbOutput, 'latin1'),
    uConvertTabsToSpaces = 8,
  );
