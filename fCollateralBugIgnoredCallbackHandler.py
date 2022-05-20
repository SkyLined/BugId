from mConsole import oConsole;

from dxConfig import dxConfig;
from mColorsAndChars import *;

def fCollateralBugIgnoredCallbackHandler(oBugId, sInstruction, asActions):
  if not dxConfig["bQuiet"]:
    oConsole.fOutput(
      COLOR_OK, CHAR_OK,
      COLOR_NORMAL, " This bug was ignored by skipping the ",
      COLOR_INFO, sInstruction,
      COLOR_NORMAL, " instruction:",
    );
    for uIndex in range(len(asActions)):
      sAction = asActions[uIndex];
      oConsole.fOutput(
        COLOR_NORMAL, "  ",
        COLOR_LIST, CHAR_LIST,
        COLOR_NORMAL, " ", sAction, "." if uIndex == len(asActions) - 1 else ",",
      );
    