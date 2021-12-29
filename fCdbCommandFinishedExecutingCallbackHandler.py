from mConsole import oConsole;

from dxConfig import dxConfig;
from mColorsAndChars import *;

def fCdbCommandFinishedExecutingCallbackHandler(oBugId, sCommand, uAttempt, uTries, s0Comment):
  if dxConfig["bQuiet"]:
    return;
  oConsole.fStatus("");
