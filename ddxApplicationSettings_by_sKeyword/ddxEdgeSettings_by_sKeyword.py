import os;
from dxConfig import dxConfig;
from fsFirstExistingFile import fsFirstExistingFile;
from mWindowsAPI import oWindowsVersion;
import mFileSystem;

sLocalAppData = os.getenv("LocalAppData");

dxConfigSettings = {
  # Settings used by all browsers (these should eventually be fine-tuned for each browser)
  "bApplicationTerminatesWithMainProcess": True,
  "nExcessiveCPUUsageCheckInitialTimeout": 30.0, # Give browser some time to load repro
  "cBugId.nExcessiveCPUUsageCheckInterval": 30.0, # Browser may be busy for a bit, but no longer than 30 seconds.
  "cBugId.nExcessiveCPUUsagePercent": 95,      # Browser msust be very, very busy.
  "cBugId.nExcessiveCPUUsageWormRunTime": 0.5, # Any well written function should return within half a second IMHO.
  "cBugId.bIgnoreCPPExceptions": True,
  "cBugId.bIgnoreWinRTExceptions": True,
};

sEdgeRecoveryPath = mFileSystem.fsPath(os.getenv("LocalAppData"), \
    "Packages", "Microsoft.MicrosoftEdge_8wekyb3d8bbwe", "AC", "MicrosoftEdge", "User", "Default", "Recovery", "Active");

def fEdgeCleanup():
  if mFileSystem.fbIsFolder(sEdgeRecoveryPath):
    mFileSystem.fbDeleteChildrenFromFolder(sEdgeRecoveryPath);

def fasGetEdgeStaticArguments(bForHelp):
  if not bForHelp:
    # We don't really return any arguments, but we do check that we can run this
    # version of Edge...
    if oWindowsVersion.uCurrentBuild < 15063:
      oConsole.fPrint(ERROR, "Debugging Microsoft Edge directly using BugId is only supported on Windows");
      oConsole.fPrint(ERROR, "builds ", ERROR_INFO, "15063", ERROR, " and higher, and you are running build ", \
          ERROR_INFO, oWindowsVersion.sCurrentBuild, ERROR, ".");
      oConsole.fPrint();
      oConsole.fPrint("You could try using the ", INFO, "EdgeBugId.cmd", NORMAL, " script that comes with EdgeDbg,");
      oConsole.fPrint("which you can download from ", INFO, "https://github.com/SkyLined/EdgeDbg", NORMAL, ".");
      oConsole.fPrint("It can be used to debug Edge in BugId on Windows versions before 10.0.15063.");
      os._exit(4);
  return [];

def fasGetEdgeOptionalArguments(bForHelp = False):
  return bForHelp and ["<dxConfig.sDefaultBrowserTestURL>"] or [dxConfig["sDefaultBrowserTestURL"]];


ddxEdgeSettings_by_sKeyword = {
  "edge": {
    "dxUWPApplication": {
      "sPackageName": "Microsoft.MicrosoftEdge",
      "sId": "MicrosoftEdge",
    },
    "asApplicationAttachToProcessesForExecutableNames": ["browser_broker.exe"],
    "fasGetStaticArguments": fasGetEdgeStaticArguments,
    "fasGetOptionalArguments": fasGetEdgeOptionalArguments,
    "fCleanup": fEdgeCleanup,
    "dxConfigSettings": dxConfigSettings,
  },
};