import mRegistry;
from oConsole import oConsole;

from fsCreateBugIdCommandLine import fsCreateBugIdCommandLine;
from mColors import *;
import mJITDebuggerRegistry;

def fbInstallAsJITDebugger(asArguments):
  sBugIdCommandLine = fsCreateBugIdCommandLine(
    [
      "--pid=%ld",
      "--handle-jit-event=%ld",
    ] +
    asArguments
  );
  oRegistryHiveKey = mRegistry.cRegistryHiveKey(
    sHiveName = mJITDebuggerRegistry.sRegistryHiveName,
    sKeyName = mJITDebuggerRegistry.sComandLineKeyPath,
  );
  oConsole.fStatus("* Installing as JIT debugger...");
  for (sName, sValue) in {
    "Auto": "1",
    "Debugger": sBugIdCommandLine
  }.items():
    try:
      oRegistryHiveKey.foSetNamedValue(sValueName = sName, sTypeName = "SZ", xValue = sValue);
    except WindowsError, oException:
      if oException.winerror == 5:
        oConsole.fOutput(ERROR, "- BugId cannot be installed as the default JIT debugger.");
        oConsole.fOutput(ERROR, "  Access to the relevant registry keys is denied.");
        oConsole.fOutput(ERROR, "  Please try again with elevated priviledges.");
        return False;
      raise;
  oConsole.fOutput("+ BugId is now installed as the default JIT debugger.");
  oConsole.fOutput("  Command line: ", INFO, sBugIdCommandLine);
  return True;