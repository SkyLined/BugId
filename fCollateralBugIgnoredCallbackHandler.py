from mConsole import oConsole;

from dxConfig import dxConfig;
from mColorsAndChars import *;

def fCollateralBugIgnoredCallbackHandler(oBugId, sReason):
  if not dxConfig["bQuiet"]:
    oConsole.fOutput(
      COLOR_OK, CHAR_OK,
      COLOR_NORMAL, " This bug was ignored: ",
      COLOR_INFO, sReason,
      COLOR_NORMAL, ".",
    );
    