import os;

import mRegistry;
from mConsole import oConsole;

from dxConfig import dxConfig;
from fsCreateBugIdCommandLine import fsCreateBugIdCommandLine;
from mColors import *;
import mJITDebuggerRegistry;

def fbInstallAsJITDebugger(asAdditionalArguments):
  # When BugId gets started as a JIT debugger, we can use the string "%ld" in the arguments twice, which will get 
  # replaced by the process id and the JIT event number, in order. We will add arguments to that effect at the start
  # of the arument list provided by the user (later).
  asDefaultArguments = [
    # '%' gets escaped to avoid environment variable expansion. However, here we do want a '%' in the command line.
    # We can use '%%' to do so '%':
    "--pid=%%ld", 
    "--handle-jit-event=%%ld",
  ];
  # To prevent the user from accidentally providing these arguments themselves, we scan the arguments provided by the
  # user for for these and report an error and return false if we find them. We will also check if the user has provided
  # a report folder path.
  s0BugIdReportsFolder = dxConfig["sReportFolderPath"];
  for sArgument in asAdditionalArguments:
    if sArgument.startswith("--") and "=" in sArgument:
      (sName, sValue) = sArgument[2:].split("=");
      if sName in ["pid", "pids", "handle-jit-event"]:
        oConsole.fOutput(ERROR, "- You cannot use ", ERROR_INFO, sArgument, ERROR, " in combination with ", ERROR_INFO, "-I", ERROR, " in the arguments.");
        return False;
      if sName in ["report", "reports", "report-folder", "reports-folder", "report-folder-path", "reports-folder-path", "sReportFolderPath"]:
        s0BugIdReportsFolder = sValue;
  # By default the python process hosting BugId will be run in the Windows System32 folder. We cannot save bug
  # reports there. To make sure we will save bug reports somewhere we can write and where the user will likely find
  # them, we will add an argument
  if s0BugIdReportsFolder is None:
    sBugIdReportsFolder = "%s\\BugId reports" % os.getenv("USERPROFILE");
    asDefaultArguments.append("--reports=%s" % sBugIdReportsFolder);
  else:
    sBugIdReportsFolder = s0BugIdReportsFolder;
  
  sBugIdCommandLine = fsCreateBugIdCommandLine(
    asDefaultArguments + asAdditionalArguments
  );
  oRegistryHiveKey = mRegistry.cRegistryHiveKey(
    sHiveName = mJITDebuggerRegistry.sComandLineHiveName,
    sKeyPath = mJITDebuggerRegistry.sComandLineKeyPath,
  );
  oConsole.fStatus("* Installing as JIT debugger...");
  bSettingsChanged = False;
  for (sName, sValue) in {
    "Auto": "1",
    "Debugger": sBugIdCommandLine
  }.items():
    # Check if the value is already set correctly:
    try:
      oRegistryValue = oRegistryHiveKey.foGetValueForName(sValueName = "Debugger");
    except WindowsError as oException:
      pass;
    else:
      if oRegistryValue.sTypeName == "REG_SZ" and oRegistryValue.xValue == sValue:
        continue; # Yes; no need to modify it.
    try:
      oRegistryHiveKey.foSetValueForName(sValueName = sName, sTypeName = "SZ", xValue = sValue);
    except WindowsError as oException:
      if oException.winerror == 5:
        oConsole.fOutput(ERROR, "\xd7 ", ERROR_INFO, "BugId cannot be installed as the default JIT debugger.");
        oConsole.fOutput(ERROR, "  ", ERROR_INFO, "Access to the relevant registry keys is denied.");
        oConsole.fOutput(ERROR, "  Please try again with ", ERROR_INFO, "elevated priviledges", ERROR, ".");
        return False;
      raise;
    bSettingsChanged = True;
  if bSettingsChanged:
    oConsole.fOutput("\u221A BugId is now installed as the default JIT debugger.");
    oConsole.fOutput("  Command line: ", INFO, sBugIdCommandLine);
    oConsole.fOutput("  Reports folder: ", INFO, sBugIdReportsFolder);
  else:
    oConsole.fOutput("\u2022 BugId is already installed as the default JIT debugger.");
    oConsole.fOutput("  Command line: ", INFO, sBugIdCommandLine);
    oConsole.fOutput("  Reports folder: ", INFO, sBugIdReportsFolder);
  return True;