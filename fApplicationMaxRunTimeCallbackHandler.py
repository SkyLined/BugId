from mConsole import oConsole;

from dxConfig import dxConfig;
from mColorsAndChars import *;

def fApplicationMaxRunTimeCallbackHandler(oBugId):
  oConsole.fOutput(
    COLOR_INFO, CHAR_INFO,
    COLOR_NORMAL, " T+",
    COLOR_INFO, "%.1f" % oBugId.fnApplicationRunTimeInSeconds(),
    COLOR_NORMAL, " The application has been running for ",
    COLOR_INFO, "%.1f" % dxConfig["n0ApplicationMaxRunTimeInSeconds"],
    COLOR_NORMAL, " seconds without crashing.",
  );
  oConsole.fOutput();
  oConsole.fStatus(COLOR_BUSY, CHAR_BUSY, COLOR_NORMAL, " BugId is stopping...");
  oBugId.fStop();
