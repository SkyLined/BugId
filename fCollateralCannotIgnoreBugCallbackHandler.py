from mConsole import oConsole;

from mColorsAndChars import *;

def fCollateralCannotIgnoreBugCallbackHandler(oBugId, sReason):
  oConsole.fOutput(
    COLOR_ERROR, CHAR_ERROR,
    COLOR_NORMAL, " This bug cannot be ignored: ",
    COLOR_INFO, sReason,
    COLOR_NORMAL, ".",
  );
  