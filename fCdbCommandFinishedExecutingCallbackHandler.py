from dxConfig import dxConfig;
from foConsoleLoader import foConsoleLoader;
from mColorsAndChars import *;
oConsole = foConsoleLoader();

def fCdbCommandFinishedExecutingCallbackHandler(oBugId, sCommand, uAttempt, uTries, s0Comment):
  if dxConfig["bQuiet"]:
    return;
  oConsole.fStatus("");
