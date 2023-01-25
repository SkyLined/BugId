import json;

from foConsoleLoader import foConsoleLoader;
from mColorsAndChars import *;
oConsole = foConsoleLoader();

def fOutputApplicationKeyWordHelp(sApplicationKeyword, dxApplicationSettings):
  oConsole.fLock();
  try:
    oConsole.fOutput("Known application settings for ", COLOR_INFO, sApplicationKeyword);
    if "sBinaryPath" in dxApplicationSettings:
      sBinaryPath = dxApplicationSettings["sBinaryPath"];
      if sBinaryPath is None:
        oConsole.fOutput(
          COLOR_WARNING, CHAR_WARNING,
          COLOR_NORMAL, " The application cannot be found on your system.",
        );
      else:
        oConsole.fOutput("  Binary path: ", COLOR_INFO, sBinaryPath);
    elif "dxUWPApplication" in dxApplicationSettings:
      dxUWPApplication = dxApplicationSettings["dxUWPApplication"];
      oConsole.fOutput("  UWP Application information:");
      oConsole.fOutput("    Package name: ", COLOR_INFO, dxUWPApplication["sPackageName"]);
      oConsole.fOutput("    Id: ", COLOR_INFO, dxUWPApplication["sId"]);
    if "asApplicationAttachToProcessesForExecutableNames" in dxApplicationSettings:
      asApplicationAttachToProcessesForExecutableNames = dxApplicationSettings["asApplicationAttachToProcessesForExecutableNames"];
      oConsole.fOutput("  Attach to additional processes running any of the following binaries:");
      for sBinaryName in asApplicationAttachToProcessesForExecutableNames:
        oConsole.fOutput("    ", COLOR_INFO, sBinaryName);
    if "fasGetStaticArguments" in dxApplicationSettings:
      fasGetApplicationStaticArguments = dxApplicationSettings["fasGetStaticArguments"];
      asApplicationStaticArguments = fasGetApplicationStaticArguments(bForHelp = True);
      oConsole.fOutput("  Default static arguments:");
      oConsole.fOutput("    ", COLOR_INFO, " ".join(asApplicationStaticArguments));
    if "fasGetOptionalArguments" in dxApplicationSettings:
      fasGetOptionalArguments = dxApplicationSettings["fasGetOptionalArguments"];
      asApplicationOptionalArguments = fasGetOptionalArguments(bForHelp = True);
      oConsole.fOutput("  Default optional arguments:");
      oConsole.fOutput("    ", COLOR_INFO, " ".join(asApplicationOptionalArguments));
    if "dxConfigSettings" in dxApplicationSettings:
      dxApplicationConfigSettings = dxApplicationSettings["dxConfigSettings"];
      if dxApplicationConfigSettings:
        oConsole.fOutput("  Application specific settings:");
        for sSettingName, xValue in dxApplicationConfigSettings.items():
          oConsole.fOutput("    ", COLOR_INFO, sSettingName, COLOR_NORMAL, ": ", COLOR_INFO, json.dumps(xValue));
  finally:
    oConsole.fUnlock();
