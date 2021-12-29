from mConsole import oConsole;

from dxConfig import dxConfig;
from mColorsAndChars import *;

def fCdbCommandStartedExecutingCallbackHandler(oBugId, sCommand, uAttempt, uTries, s0Comment):
  if dxConfig["bQuiet"]:
    return;
  oConsole.fStatus(
    COLOR_BUSY, CHAR_BUSY,
    COLOR_NORMAL, " T+",
    COLOR_INFO, "%.1f" % oBugId.fnApplicationRunTimeInSeconds(),
    COLOR_NORMAL, " executing command ",
    COLOR_INFO, sCommand,
    [
      COLOR_NORMAL, " (",
      COLOR_INFO, s0Comment,
      COLOR_NORMAL, ")",
    ] if s0Comment else [],
    [ 
      COLOR_NORMAL, " #",
      COLOR_INFO, uAttempt,
      COLOR_NORMAL, "/",
      COLOR_INFO, uTries,
    ] if uTries > 1 else [],
    COLOR_NORMAL, "...",
  );
