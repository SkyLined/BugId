
import mRegistry, mWindowsAPI;
from mNotProvided import fbIsProvided;

from foConsoleLoader import foConsoleLoader;
from fsCreateBugIdCommandLine import fsCreateBugIdCommandLine;
from mColorsAndChars import *;
import mJITDebuggerRegistry;
oConsole = foConsoleLoader();

def fOutputCurrentJITDebuggerSettings():
  sOSISA = mWindowsAPI.oSystemInfo.sOSISA;
  dsCommandLineKeyPath_by_sTargetBinaryISA = mJITDebuggerRegistry.ddsCommandLineKeyPath_by_sTargetBinaryISA_by_sOSISA[sOSISA];
  oConsole.fLock();
  try:
    oConsole.fOutput(
      "┌───[ ",
      COLOR_INFO, "Current JIT Debugger", "s" if len(dsCommandLineKeyPath_by_sTargetBinaryISA) > 1 else "",
      COLOR_NORMAL, " ]",
      sPadding = "─"
    );
    dsCommandLineKeyPath_by_sTargetBinaryISA = mJITDebuggerRegistry.ddsCommandLineKeyPath_by_sTargetBinaryISA_by_sOSISA[sOSISA];
    for (sTargetBinaryISA, sCommandLineKeyPath) in dsCommandLineKeyPath_by_sTargetBinaryISA.items():
      # Get the current JIT debugger command line for the target binary ISA if one is installed.
      oRegistryHiveKey = mRegistry.cRegistryHiveKey(
        sHiveName = mJITDebuggerRegistry.sCommandLineHiveName,
        sKeyPath = sCommandLineKeyPath,
      );
      o0RegistryValue = oRegistryHiveKey.fo0GetValueForName(sValueName = "Debugger");
      if o0RegistryValue is None:
        oConsole.fOutput(
          "│ ",
          COLOR_WARNING, CHAR_WARNING,
          COLOR_NORMAL, " ",
          COLOR_INFO, sTargetBinaryISA,
          COLOR_NORMAL, " JIT debugger: ",
          COLOR_INFO, "None",
          COLOR_NORMAL, ".",
        );
      elif o0RegistryValue.sTypeName != "REG_SZ":
        oConsole.fOutput(
          "│ ",
          COLOR_ERROR, CHAR_ERROR,
          COLOR_NORMAL, " ",
          COLOR_INFO, sTargetBinaryISA,
          COLOR_NORMAL, " JIT debugger: ",
          COLOR_INFO, "Unknown",
          COLOR_NORMAL, " (registry value not a string).",
        );
      else:
        sCurrentJITDebuggerCommandLine = o0RegistryValue.xValue;
        sBugIdJITDebuggerCommandLineStartsWith = fsCreateBugIdCommandLine();
        if sCurrentJITDebuggerCommandLine.startswith(sBugIdJITDebuggerCommandLineStartsWith):
          oConsole.fOutput(
            "│ ",
            COLOR_OK, CHAR_OK,
            COLOR_NORMAL, " ",
            COLOR_INFO, sTargetBinaryISA,
            COLOR_NORMAL, " JIT debugger: ",
            COLOR_INFO, "BugId",
            COLOR_NORMAL, ".",
          );
          sArguments = sCurrentJITDebuggerCommandLine[len(sBugIdJITDebuggerCommandLineStartsWith) + 1:];
          oConsole.fOutput(
            "│   Arguments: ",
            COLOR_INFO, sArguments,
          );
        else:
          oConsole.fOutput(
            "│ ",
            COLOR_INFO, CHAR_INFO,
            COLOR_NORMAL, " ",
            COLOR_INFO, sTargetBinaryISA,
            COLOR_NORMAL, " JIT debugger: ",
            COLOR_INFO, "Other",
            COLOR_NORMAL, ".",
          );
          oConsole.fOutput(
            "│   Command line: ",
            COLOR_INFO, sCurrentJITDebuggerCommandLine,
          );
    oConsole.fOutput("└", sPadding = "─");
  finally:
    oConsole.fUnlock();
