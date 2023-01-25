from foConsoleLoader import foConsoleLoader;
from mColorsAndChars import *;
oConsole = foConsoleLoader();

def fCollateralCannotIgnoreBugCallbackHandler(oBugId, sReason):
  oConsole.fOutput(
    COLOR_ERROR, CHAR_ERROR,
    COLOR_NORMAL, " This bug cannot be ignored: ",
    COLOR_INFO, sReason,
    COLOR_NORMAL, ".",
  );
  