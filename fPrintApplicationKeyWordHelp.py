import json;
from mConsole import oConsole;

from mColors import *;

def fPrintApplicationKeyWordHelp(sApplicationKeyword, dxApplicationSettings):
  oConsole.fLock();
  try:
    oConsole.fOutput("Known application settings for ", INFO, sApplicationKeyword);
    if "sBinaryPath" in dxApplicationSettings:
      sBinaryPath = dxApplicationSettings["sBinaryPath"];
      if sBinaryPath is None:
        oConsole.fOutput(ERROR, "  The application cannot be found on your system.");
      else:
        oConsole.fOutput("  Binary path: ", INFO, sBinaryPath);
    elif "dxUWPApplication" in dxApplicationSettings:
      dxUWPApplication = dxApplicationSettings["dxUWPApplication"];
      oConsole.fOutput("  UWP Application information:");
      oConsole.fOutput("    Package name: ", INFO, dxUWPApplication["sPackageName"]);
      oConsole.fOutput("    Id: ", INFO, dxUWPApplication["sId"]);
    if "asApplicationAttachToProcessesForExecutableNames" in dxApplicationSettings:
      asApplicationAttachToProcessesForExecutableNames = dxApplicationSettings["asApplicationAttachToProcessesForExecutableNames"];
      oConsole.fOutput("  Attach to additional processes running any of the following binaries:");
      for sBinaryName in asApplicationAttachToProcessesForExecutableNames:
        oConsole.fOutput("    ", INFO, sBinaryName);
    if "fasGetStaticArguments" in dxApplicationSettings:
      fasGetApplicationStaticArguments = dxApplicationSettings["fasGetStaticArguments"];
      asApplicationStaticArguments = fasGetApplicationStaticArguments(bForHelp = True);
      oConsole.fOutput("  Default static arguments:");
      oConsole.fOutput("    ", INFO, " ".join(asApplicationStaticArguments));
    if "fasGetOptionalArguments" in dxApplicationSettings:
      fasGetOptionalArguments = dxApplicationSettings["fasGetOptionalArguments"];
      asApplicationOptionalArguments = fasGetOptionalArguments(bForHelp = True);
      oConsole.fOutput("  Default optional arguments:");
      oConsole.fOutput("    ", INFO, " ".join(asApplicationOptionalArguments));
    if "dxConfigSettings" in dxApplicationSettings:
      dxApplicationConfigSettings = dxApplicationSettings["dxConfigSettings"];
      if dxApplicationConfigSettings:
        oConsole.fOutput("  Application specific settings:");
        for sSettingName, xValue in dxApplicationConfigSettings.items():
          oConsole.fOutput("    ", INFO, sSettingName, NORMAL, ": ", INFO, json.dumps(xValue));
  finally:
    oConsole.fUnlock();
