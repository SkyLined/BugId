from cBugId import cBugId;
from mColors import *;
import mFileSystem;
import mWindowsAPI;
from oConsole import oConsole;
from oVersionInformation import oVersionInformation;

def fVersionCheck():
  import os, platform, sys;
  oConsole.fLock();
  try:
    oConsole.fPrint("+ ", INFO, "Windows", NORMAL, " version: ", INFO, mWindowsAPI.oWindowsVersion.sProductName, \
      NORMAL, " release ", INFO, mWindowsAPI.oWindowsVersion.sReleaseId, NORMAL, ", build ", INFO, \
      mWindowsAPI.oWindowsVersion.sCurrentBuild, NORMAL, " ", INFO, mWindowsAPI.oWindowsVersion.sISA, NORMAL, ".");
    oConsole.fPrint("+ ", INFO, "Python", NORMAL, " version: ", INFO, str(platform.python_version()), NORMAL, " ", \
      INFO, mWindowsAPI.fsGetPythonISA(), NORMAL, ".");
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
        oConsole.fPrint("  You are running a ", HILITE, "pre-release", NORMAL, " version: ",
            "the latest release version is ", INFO, oModuleVersionInformation.sLatestVersion, NORMAL, ".");
      elif not oModuleVersionInformation.bUpToDate:
        oConsole.fPrint("  Version ", HILITE, oModuleVersionInformation.sLatestVersion, NORMAL,
            " is available at ", HILITE, oModuleVersionInformation.sUpdateURL, NORMAL, ".");
      uCounter += 1;
    oConsole.fPrint();
  finally:
    oConsole.fUnlock();
