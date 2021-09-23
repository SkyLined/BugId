import json, os, re, sys;

import mRegistry;
from mConsole import oConsole;

from mColorsAndChars import *;
import mJITDebuggerRegistry;

def fxGetCurrentJITDebuggerCommandLine():
  # Returns a string with the current JIT debugger command line
  # or None if no JIT debugger is installed.
  # or False if the registry could not be read or the value makes no sense.
  oRegistryHiveKey = mRegistry.cRegistryHiveKey(
    sHiveName = mJITDebuggerRegistry.sComandLineHiveName,
    sKeyPath = mJITDebuggerRegistry.sComandLineKeyPath,
  );
  try:
    oRegistryValue = oRegistryHiveKey.foGetValueForName(sValueName = "Debugger");
  except WindowsError as oException:
    return False;
  if oRegistryValue.sTypeName != "REG_SZ":
    return False;
  return oRegistryValue.xValue;