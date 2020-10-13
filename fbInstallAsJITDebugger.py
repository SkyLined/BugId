import json, os, re, sys;

import mRegistry;
from oConsole import oConsole;
from mColors import *;
sJITDebuggerComandLineRegistryHiveName = "HKLM";
sJITDebuggerComandLineRegistryKeyPath = r"Software\Microsoft\Windows NT\CurrentVersion\AEDebug";
# Command line arguments that contain only alphanumeric chars, underscores and a select set of other chars do not need quotes.
rArgumentThatDoesNotRequireQuotesAndEscapesInCommandLine = re.compile(
  r"^[\w!#\$\+,\-\.\/:=@\[\\\]\{\}~`]+$", 
);

def fsAddQuotesAndEscapesIfNeededInCommandLine(sString):
  # Arguments with spaces and/or special characters will need to be quoted and some
  # special chars need to be 'escaped'. It's not technically escaping but they do need
  # to be replaced with a set of chars to make sure they will be interpretted correctly.
  if rArgumentThatDoesNotRequireQuotesAndEscapesInCommandLine.match(sString):
    return sString;
  return '"%s"' % (sString
    .replace('"', '""') # double up quotes inside quotes to escape them
    .replace('%', '"%"') # move '%' out of the quotes to avoid environment variable expansion.
    .replace(r'\\', r'"\\"'), # move '\\' out of the quotes AND double up to avoid it being interpreted as an escape char.
  );

def fbInstallAsJITDebugger(asArguments):
  sPythonExecutableFilePath = sys.executable;
  sBugIdMainScriptFilePath = os.path.join(os.path.dirname(__file__), "BugId.py");
  sBugIdCommandLine = " ".join([s for s in (
    [
      fsAddQuotesAndEscapesIfNeededInCommandLine(sPythonExecutableFilePath,),
      fsAddQuotesAndEscapesIfNeededInCommandLine(sBugIdMainScriptFilePath,),
      "--pid=%ld",
      "--handle-jit-event=%ld",
    ] + [
      fsAddQuotesAndEscapesIfNeededInCommandLine(sArgument)
      for sArgument in asArguments
    ]
  ) if s ]);
  oRegistryHiveKey = mRegistry.cRegistryHiveKey(
    sHiveName = sJITDebuggerComandLineRegistryHiveName,
    sKeyName = sJITDebuggerComandLineRegistryKeyPath,
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