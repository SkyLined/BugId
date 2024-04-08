import os;

import mRegistry, mWindowsAPI;

from foConsoleLoader import foConsoleLoader;
from fsCreateBugIdCommandLine import fsCreateBugIdCommandLine;
from mColorsAndChars import *;
import mJITDebuggerRegistry;
oConsole = foConsoleLoader();

def fbInstallAsJITDebugger(asAdditionalArguments):
  # To prevent the user from accidentally providing these arguments themselves, we scan the arguments provided by the
  # user for these and report an error and return false if we find them. We will also check if the user has provided
  # a report folder path.
  bBugIdReportsFolderArgumentPresent = False;
  asPauseArguments = [];
  asFilteredAdditionalArguments = [];
  for sArgument in asAdditionalArguments:
    if sArgument.startswith("--"):
      tsNameAndValue = sArgument[2:].split("=");
      sName = tsNameAndValue[0];
      if sName in ["pid", "pids", "handle-jit-event"]:
        oConsole.fOutput(
          COLOR_ERROR, CHAR_ERROR,
          COLOR_NORMAL, " You cannot use ",
          COLOR_INFO, sArgument,
          COLOR_NORMAL, " in combination with ",
          COLOR_INFO, "-I",
          COLOR_NORMAL, " in the arguments.",
        );
        return False;
      if sName in ["p", "pause"]:
        # We want to set the pause flag as early as possible to catch any exceptions.
        asPauseArguments.append(sArgument);
        # So we will remove
        continue;
      if sName in ["report", "reports", "report-folder", "reports-folder", "report-folder-path", "reports-folder-path", "sReportFolderPath"]:
        bBugIdReportsFolderArgumentPresent = True;
    asFilteredAdditionalArguments.append(sArgument);
  
  sOSISA = mWindowsAPI.oSystemInfo.sOSISA;
  dsCommandLineKeyPath_by_sTargetBinaryISA = mJITDebuggerRegistry.ddsCommandLineKeyPath_by_sTargetBinaryISA_by_sOSISA[sOSIA];
  for (sTargetBinaryISA, sCommandLineKeyPath) in dsCommandLineKeyPath_by_sTargetBinaryISA.items():
    sBugIdCommandLine = fsCreateBugIdCommandLine(
      (
        # We want to set the pause flag as early as possible to catch any exceptions.
        asPauseArguments or ["--pause"] # If no pause argument is provided, default to pausing
      ) + [
        # When BugId gets started as a JIT debugger, we can use the string "%ld" in the arguments twice, which will get 
        # replaced by the process id and the JIT event number, in order. We will add arguments to that effect at the start
        # of the argument list provided by the user (later).
        # '%' gets escaped to avoid environment variable expansion. However, here we do want a '%' in the command line.
        # We can use '%%' to do so '%':
        "--pid=%%ld", 
        "--handle-jit-event=%%ld",
        "--isa=%s" % sTargetBinaryISA,
      ] + (
        # By default the python process hosting BugId will be run in the Windows System32 folder. We cannot save bug
        # reports there. To make sure we will save bug reports somewhere we can write and where the user will likely find
        # them, we will add an argument
        ["--reports-folder-path=%s\\BugId reports" % os.getenv("USERPROFILE")]
            if not bBugIdReportsFolderArgumentPresent else []
      ) + (
        asFilteredAdditionalArguments
      )
    );
    
    oRegistryHiveKey = mRegistry.cRegistryHiveKey(
      sHiveName = mJITDebuggerRegistry.sCommandLineHiveName,
      sKeyPath = sCommandLineKeyPath,
    );
    
    oConsole.fStatus("* Installing as JIT debugger for %s binaries..." % sTargetBinaryISA);
    bSettingsForTargetBinaryISAChanged = False;
    for (sName, sValue) in {
      "Auto": "1",
      "Debugger": sBugIdCommandLine
    }.items():
      # Check if the value is already set correctly:
      o0RegistryValue = oRegistryHiveKey.fo0GetValueForName(sValueName = "Debugger");
      
      if o0RegistryValue and o0RegistryValue.sTypeName == "REG_SZ" and o0RegistryValue.xValue == sValue:
        continue; # Yes; no need to modify it.
      
      try:
        oRegistryHiveKey.foSetValueForName(sValueName = sName, sTypeName = "SZ", xValue = sValue);
      except WindowsError as oException:
        if oException.winerror == 5:
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " BugId cannot be installed as the default JIT debugger for 64-bit binaries..");
          oConsole.fOutput("  Access to the relevant registry keys is denied.");
          oConsole.fOutput("  Please try again with ", COLOR_INFO, "elevated privileges", COLOR_NORMAL, ".");
          return False;
        raise;
      bSettingsForTargetBinaryISAChanged = True;
    oConsole.fOutput(
      COLOR_OK, CHAR_OK,
      COLOR_NORMAL, " BugId is ", "already" if bSettingsForTargetBinaryISAChanged else "now", " installed as the default JIT debugger for 64-bit binaries.");
    oConsole.fOutput("  Command line: ", COLOR_INFO, sBugIdCommandLine);
  return True;