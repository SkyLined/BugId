from mRegistry import cRegistryHiveKey;
from mNotProvided import zNotProvided;

from foConsoleLoader import foConsoleLoader;
from mColorsAndChars import *;
import mJITDebuggerRegistry;
oConsole = foConsoleLoader();

def fxGetCurrentJITDebuggerCommandLine(sOSISA, sTargetBinaryISA):
  dsCommandLineKeyPath = mJITDebuggerRegistry.ddsCommandLineKeyPath_by_sTargetBinaryISA_by_sOSISA[osISA][sTargetBinaryISA];
  # Returns a string with the current JIT debugger command line
  # or zNotProvided if no JIT debugger is installed.
  # or None if the registry could not be read or the value makes no sense.
  oRegistryHiveKey = cRegistryHiveKey(
    sHiveName = dsCommandLineKeyPath.sCommandLineHiveName,
    sKeyPath = dsCommandLineKeyPath.sCommandLineKeyPath,
  );
  o0RegistryValue = oRegistryHiveKey.fo0GetValueForName(sValueName = "Debugger");
  if o0RegistryValue is None:
    return zNotProvided;
  if o0RegistryValue.sTypeName != "REG_SZ":
    return None;
  return o0RegistryValue.xValue;