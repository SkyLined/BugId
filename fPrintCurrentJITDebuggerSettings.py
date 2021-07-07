
from mConsole import oConsole;

from fsCreateBugIdCommandLine import fsCreateBugIdCommandLine;
from fxGetCurrentJITDebuggerCommandLine import fxGetCurrentJITDebuggerCommandLine;
from mColors import *;

def fPrintCurrentJITDebuggerSettings():
  oConsole.fLock();
  try:
    oConsole.fOutput(
      "\u250C\u2500 ", INFO, "Current JIT Debugger", NORMAL, " ", sPadding = "\u2500",
    );
    xCurrentJITDebuggerCommandLine = fxGetCurrentJITDebuggerCommandLine();
    if xCurrentJITDebuggerCommandLine is None:
      oConsole.fOutput(
        "\u2502 \u2219 JIT debugger: None.",
      );
    elif xCurrentJITDebuggerCommandLine is False:
      oConsole.fOutput(
        "\u2502 \u2219 JIT debugger: ", ERROR_INFO, "Unknown", NORMAL, " (unable to read registry).",
      );
    else:
      sBugIdJITDebuggerCommandLineStartsWith = fsCreateBugIdCommandLine();
      if xCurrentJITDebuggerCommandLine.startswith(sBugIdJITDebuggerCommandLineStartsWith):
        oConsole.fOutput("\u2502 \u2219 JIT debugger: ", INFO, "BugId", NORMAL, ".");
        sArguments = xCurrentJITDebuggerCommandLine[len(sBugIdJITDebuggerCommandLineStartsWith) + 1:];
        oConsole.fOutput(
          "\u2502   Arguments: ", INFO, sArguments, NORMAL, ".",
        );
      else:
        oConsole.fOutput("\u2502 \u2219 JIT debugger: ", WARNING_INFO, "Other", NORMAL, ".");
        oConsole.fOutput(
          "\u2502   Command line: ", INFO, xCurrentJITDebuggerCommandLine, NORMAL, ".",
        );
    oConsole.fOutput("\u2514", sPadding = "\u2500");
  finally:
    oConsole.fUnlock();
