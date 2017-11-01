from cBugId import cBugId;
from mColors import *;
import mFileSystem;
import mWindowsAPI;
from oConsole import oConsole;
from oVersionInformation import oVersionInformation;

def fVersionCheck():
  import os, sys;
  axModules = [
    ("BugId",             "__main__",           oVersionInformation),
    ("cBugId",            "cBugId",             cBugId.oVersionInformation),
    ("mFileSystem",       "mFileSystem",        mFileSystem.oVersionInformation),
    ("mWindowsAPI",       "mWindowsAPI",        mWindowsAPI.oVersionInformation),
    ("oConsole",          "oConsole",           oConsole.oVersionInformation),
  ];
  uCounter = 0;
  for (sModuleName, sSysModuleName, oModuleVersionInformation) in axModules:
    assert sModuleName == oModuleVersionInformation.sProjectName, \
        "Module %s reports that it is called %s" % (sModuleName, oModuleVersionInformation.sProjectName);
    sInstallationPath = os.path.dirname(sys.modules[sSysModuleName].__file__);
    oConsole.fPrint("+ ", INFO, oModuleVersionInformation.sProjectName, NORMAL, " version: ", INFO, \
        oModuleVersionInformation.sCurrentVersion, NORMAL, ", installed at ", INFO, sInstallationPath, NORMAL, ".");
    oConsole.fProgressBar(uCounter * 1.0 / len(axModules), \
        "* Checking %s for updates..." % oModuleVersionInformation.sProjectName);
    if oModuleVersionInformation.bPreRelease:
      oConsole.fPrint("  + You are running a ", HILITE, "pre-release", NORMAL, " version. ",
          "The latest release version is ", INFO, oModuleVersionInformation.sLatestVersion, NORMAL, ".");
    elif not oModuleVersionInformation.bUpToDate:
      oConsole.fPrint("  + Version ", INFO, oModuleVersionInformation.sLatestVersion, NORMAL,
          " is available at ", INFO, oModuleVersionInformation.sUpdateURL, NORMAL, ".");
    uCounter += 1;
  oConsole.fPrint("+ Windows version: ", INFO, str(mWindowsAPI.oWindowsVersion), NORMAL, ".");
  oConsole.fPrint();

