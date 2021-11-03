
from mConsole import oConsole;
from mNotProvided import fbIsProvided;

from fsCreateBugIdCommandLine import fsCreateBugIdCommandLine;
from fxGetCurrentJITDebuggerCommandLine import fxGetCurrentJITDebuggerCommandLine;
from mColorsAndChars import *;

def fOutputCurrentJITDebuggerSettings():
  oConsole.fLock();
  try:
    oConsole.fOutput("┌───[", COLOR_INFO, " Current JIT Debugger ", COLOR_NORMAL, "]", sPadding = "─");
    xCurrentJITDebuggerCommandLine = fxGetCurrentJITDebuggerCommandLine();
    if not fbIsProvided(xCurrentJITDebuggerCommandLine):
      oConsole.fOutput(
        "│ ",
        COLOR_INFO, CHAR_INFO,
        COLOR_NORMAL, "JIT debugger: ",
        COLOR_INFO, "None",
        COLOR_NORMAL, ".",
      );
    elif xCurrentJITDebuggerCommandLine is None:
      oConsole.fOutput(
        "│ ",
        COLOR_ERROR, CHAR_ERROR,
        COLOR_NORMAL, " JIT debugger: ",
        COLOR_INFO, "Unknown",
        COLOR_NORMAL, " (unable to read registry).",
      );
    else:
      sBugIdJITDebuggerCommandLineStartsWith = fsCreateBugIdCommandLine();
      if xCurrentJITDebuggerCommandLine.startswith(sBugIdJITDebuggerCommandLineStartsWith):
        oConsole.fOutput(
          "│ ",
          COLOR_OK, CHAR_OK,
          COLOR_NORMAL, " JIT debugger: ",
          COLOR_INFO, "BugId",
          COLOR_NORMAL, ".",
        );
        sArguments = xCurrentJITDebuggerCommandLine[len(sBugIdJITDebuggerCommandLineStartsWith) + 1:];
        oConsole.fOutput(
          "│   Arguments: ",
          COLOR_INFO, sArguments,
        );
      else:
        oConsole.fOutput(
          "│ ",
          COLOR_WARNING, CHAR_WARNING,
          COLOR_NORMAL, " JIT debugger: ",
          COLOR_INFO, "Other",
          COLOR_NORMAL, ".",
        );
        oConsole.fOutput(
          "│   Command line: ",
          COLOR_INFO, xCurrentJITDebuggerCommandLine,
        );
    oConsole.fOutput("└", sPadding = "─");
  finally:
    oConsole.fUnlock();
