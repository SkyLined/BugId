from mConsole import oConsole;

from dxConfig import dxConfig;
from mColorsAndChars import *;

def fCdbStdErrOutputCallbackHandler(oBugId, sbOutput):
  if dxConfig["bQuiet"]:
    return;
  oConsole.fOutput(
    COLOR_ERROR, "stderr>",
    COLOR_NORMAL, str(sbOutput, 'latin1'),
    uConvertTabsToSpaces = 8,
  );
