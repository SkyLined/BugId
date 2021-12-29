from mConsole import oConsole;

from dxConfig import dxConfig;
from mColorsAndChars import *;

def fApplicationResumedCallbackHandler(oBugId):
  if dxConfig["bQuiet"]:
    return;
  oConsole.fStatus(
    COLOR_BUSY, CHAR_BUSY,
    COLOR_NORMAL, " T+",
    COLOR_INFO, "%.1f" % oBugId.fnApplicationRunTimeInSeconds(),
    COLOR_NORMAL, " The application is running...",
  );
