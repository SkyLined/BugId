import os;
from dxConfig import dxConfig;
from fsFirstExistingFile import fsFirstExistingFile;
from mWindowsAPI import oWindowsVersion;
import mFileSystem;

sLocalAppData = os.getenv("LocalAppData");

dxConfigSettings = {
  "bApplicationTerminatesWithMainProcess": True,
  "cBugId.bIgnoreCPPExceptions": True,
  "cBugId.bIgnoreWinRTExceptions": True,
};

sEdgeRecoveryPath = mFileSystem.fsPath(os.getenv("LocalAppData"), \
    "Packages", "Microsoft.MicrosoftEdge_8wekyb3d8bbwe", "AC", "MicrosoftEdge", "User", "Default", "Recovery", "Active");

def fEdgeCleanup():
  if mFileSystem.fbIsFolder(sEdgeRecoveryPath):
    mFileSystem.fbDeleteChildrenFromFolder(sEdgeRecoveryPath);

def fEdgeVersionCheck():
  if oWindowsVersion.uCurrentBuild < 15063:
    oConsole.fPrint(ERROR, "Debugging Microsoft Edge directly using BugId is only supported on Windows");
    oConsole.fPrint(ERROR, "builds ", ERROR_INFO, "15063", ERROR, " and higher, and you are running build ", \
        ERROR_INFO, oWindowsVersion.sCurrentBuild, ERROR, ".");
    oConsole.fPrint();
    oConsole.fPrint("You could try using the ", INFO, "EdgeBugId.cmd", NORMAL, " script that comes with EdgeDbg,");
    oConsole.fPrint("which you can download from ", INFO, "https://github.com/SkyLined/EdgeDbg", NORMAL, ".");
    oConsole.fPrint("It can be used to debug Edge in BugId on Windows versions before 10.0.15063.");
    os._exit(4);

def fasGetEdgeOptionalArguments(bForHelp = False):
  return bForHelp and ["<dxConfig.sDefaultBrowserTestURL>"] or [dxConfig["sDefaultBrowserTestURL"]];


ddxMicrosoftEdgeSettings_by_sKeyword = {
  "edge": {
    "fCheckApplication": fEdgeVersionCheck,
    "dxUWPApplication": {
      "sPackageName": "Microsoft.MicrosoftEdge",
      "sId": "MicrosoftEdge",
    },
    "asApplicationAttachToProcessesForExecutableNames": ["browser_broker.exe"],
    "fasGetOptionalArguments": fasGetEdgeOptionalArguments,
    "fCleanup": fEdgeCleanup,
    "dxConfigSettings": dxConfigSettings,
  },
};