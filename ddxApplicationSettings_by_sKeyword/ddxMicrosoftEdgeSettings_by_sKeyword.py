import os, sys;

from mWindowsAPI import fauProcessesIdsForExecutableNames, fbTerminateForProcessId, oSystemInfo;
from mConsole import oConsole;
from mFileSystemItem import cFileSystemItem;

from mColors import *;
from .fsFirstExistingFile import fsFirstExistingFile;

sLocalAppData = os.getenv("LocalAppData");

dxConfigSettings = {
  "bApplicationTerminatesWithMainProcess": True,
  "cBugId.bIgnoreCPPExceptions": True,
  "cBugId.bIgnoreWinRTExceptions": True,
};

oEdgeRecoveryFolder = cFileSystemItem(os.path.join(
  os.getenv("LocalAppData"), \
  "Packages", "Microsoft.MicrosoftEdge_8wekyb3d8bbwe", "AC", "MicrosoftEdge", "User", "Default", "Recovery", "Active"
));

def fEdgeSetup(bFirstRun):
  if bFirstRun:
    if oSystemInfo.uOSBuild < 15063:
      oConsole.fOutput(ERROR, "Debugging Microsoft Edge directly using BugId is only supported on Windows");
      oConsole.fOutput(ERROR, "builds ", ERROR_INFO, "15063", ERROR, " and higher, and you are running build ", \
          ERROR_INFO, oSystemInfo.sOSBuild, ERROR, ".");
      oConsole.fOutput();
      oConsole.fOutput("You could try using the ", INFO, "EdgeBugId.cmd", NORMAL, " script that comes with EdgeDbg,");
      oConsole.fOutput("which you can download from ", INFO, "https://github.com/SkyLined/EdgeDbg", NORMAL, ".");
      oConsole.fOutput("It can be used to debug Edge in BugId on Windows versions before 10.0.15063.");
      os._exit(4);
  # Cleanup in case Edge is currently running or there is state data from a previous run.
  fEdgeCleanup();

def fEdgeCleanup():
  # RuntimeBroker.exe can apparently hang with dbgsrv.exe attached, preventing Edge from opening new pages. Killing
  # all processes running either exe appears to resolve this issue.
  for uProcessId in fauProcessesIdsForExecutableNames(["dbgsrv.exe", "RuntimeBroker.exe"]):
    fbTerminateForProcessId(uProcessId);
  
  # Delete the recovery path to prevent conserving state between different runs of the application.
  if not oEdgeRecoveryFolder.fbIsFolder():
    return;
  if oEdgeRecoveryFolder.fbDelete():
    return;
  # Microsoft Edge will have a lock on these files if its running; terminate it.
  oConsole.fOutput(WARNING, "Microsoft Edge appears to be running because the recovery files cannot be");
  oConsole.fOutput(WARNING, "deleted. All running Microsoft Edge processes will now be terminated to try");
  oConsole.fOutput(WARNING, "to fix this...");
  # Microsoft Edge may attempt to restart killed processes, so we do this in a loop until there are no more processes
  # running.
  while 1:
    auProcessIds = fauProcessesIdsForExecutableNames(["MicrosoftEdge.exe", "MicrosoftEdgeCP.exe"])
    if not auProcessIds:
      break;
    for uProcessId in auProcessIds:
      fbTerminateForProcessId(uProcessId);
  if oEdgeRecoveryFolder.fbDelete():
    return;
  oConsole.fOutput(ERROR, "The recovery files still cannot be deleted. Please manually terminated all");
  oConsole.fOutput(ERROR, "processes related to Microsoft Edge and try to delete everything in");
  oConsole.fOutput(ERROR_INFO, oEdgeRecoveryFolder.sPath, ERROR, ".");
  os._exit(4);

def fasGetOptionalArguments(dxConfig, bForHelp = False):
  return bForHelp and ["<dxConfig.sDefaultBrowserTestURL>"] or [dxConfig["sDefaultBrowserTestURL"]];


ddxMicrosoftEdgeSettings_by_sKeyword = {
  "edge": {
    "dxUWPApplication": {
      "sPackageName": "Microsoft.MicrosoftEdge",
      "sId": "MicrosoftEdge",
    },
    "asApplicationAttachForProcessExecutableNames": ["browser_broker.exe"],
    "fasGetOptionalArguments": fasGetOptionalArguments,
    "fSetup": fEdgeSetup,
    "fCleanup": fEdgeCleanup,
    "dxConfigSettings": dxConfigSettings,
  },
};