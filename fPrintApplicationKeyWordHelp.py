import json;
from mColors import *;
from oConsole import oConsole;

def fPrintApplicationKeyWordHelp(sApplicationKeyword, dxApplicationSettings):
  oConsole.fLock();
  try:
    oConsole.fPrint("Known application settings for ", INFO, sApplicationKeyword);
    if "sBinaryPath" in dxApplicationSettings:
      sBinaryPath = dxApplicationSettings["sBinaryPath"];
      if sBinaryPath is None:
        oConsole.fPrint(ERROR, "  The application cannot be found on your system.");
      else:
        oConsole.fPrint("  Binary path: ", INFO, sBinaryPath);
    elif "dxUWPApplication" in dxApplicationSettings:
      dxUWPApplication = dxApplicationSettings["dxUWPApplication"];
      oConsole.fPrint("  UWP Application information:");
      oConsole.fPrint("    Package name: ", INFO, dxUWPApplication["sPackageName"]);
      oConsole.fPrint("    Id: ", INFO, dxUWPApplication["sId"]);
    if "asApplicationAttachToProcessesForExecutableNames" in dxApplicationSettings:
      asApplicationAttachToProcessesForExecutableNames = dxApplicationSettings["asApplicationAttachToProcessesForExecutableNames"];
      oConsole.fPrint("  Attach to additional processes running any of the following binaries:");
      for sBinaryName in asApplicationAttachToProcessesForExecutableNames:
        oConsole.fPrint("    ", INFO, sBinaryName);
    if "fasGetStaticArguments" in dxApplicationSettings:
      fasGetApplicationStaticArguments = dxApplicationSettings["fasGetStaticArguments"];
      asApplicationStaticArguments = fasGetApplicationStaticArguments(bForHelp = True);
      oConsole.fPrint("  Default static arguments:");
      oConsole.fPrint("    ", INFO, " ".join(asApplicationStaticArguments));
    if "fasGetOptionalArguments" in dxApplicationSettings:
      fasGetOptionalArguments = dxApplicationSettings["fasGetOptionalArguments"];
      asApplicationOptionalArguments = fasGetOptionalArguments(bForHelp = True);
      oConsole.fPrint("  Default optional arguments:");
      oConsole.fPrint("    ", INFO, " ".join(asApplicationOptionalArguments));
    if "dxConfigSettings" in dxApplicationSettings:
      dxApplicationConfigSettings = dxApplicationSettings["dxConfigSettings"];
      if dxApplicationConfigSettings:
        oConsole.fPrint("  Application specific settings:");
        for sSettingName, xValue in dxApplicationConfigSettings.items():
          oConsole.fPrint("    ", INFO, sSettingName, NORMAL, ": ", INFO, json.dumps(xValue));
  finally:
    oConsole.fUnlock();
