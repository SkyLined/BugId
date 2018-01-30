import os, platform, sys;
from cBugId import cBugId;
from mColors import *;
import mFileSystem;
import mWindowsAPI;
from mWindowsAPI import oWindowsVersion;
from oConsole import oConsole;
from oVersionInformation import oVersionInformation;

def fPrintVersionInformation():
  oConsole.fLock();
  try:
    oConsole.fPrint(NORMAL, u"\u250C\u2500", INFO, " Version information ", NORMAL, sPadding = u"\u2500");
    oConsole.fPrint(
      u"\u2502 ", INFO, "Windows",
      NORMAL, " version: ", INFO, oWindowsVersion.sProductName,
      NORMAL, " release ", INFO, oWindowsVersion.sReleaseId,
      NORMAL, ", build ", INFO, oWindowsVersion.sCurrentBuild,
      NORMAL, " ", INFO, oWindowsVersion.sISA,
      NORMAL, ", installed at ", INFO, oWindowsVersion.sPath, NORMAL, ".",
    );
    oConsole.fPrint(
      u"\u2502 ", INFO, "Python", NORMAL, " version: ", INFO, str(platform.python_version()),
      NORMAL, " ", INFO, mWindowsAPI.fsGetPythonISA(),
      NORMAL, ", installed at ", INFO, os.path.dirname(sys.executable), NORMAL, ".",
    );
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
      oConsole.fPrint(
        u"\u2502 ", INFO, oModuleVersionInformation.sProjectName,
        NORMAL, " version: ", INFO, oModuleVersionInformation.sCurrentVersion,
        NORMAL, ", installed at ", INFO, sInstallationPath, NORMAL, ".",
      );
      oConsole.fProgressBar(uCounter * 1.0 / len(axModules), \
          "* Checking %s for updates..." % oModuleVersionInformation.sProjectName);
      if oModuleVersionInformation.bPreRelease:
        oConsole.fPrint(u"\u2502  ", DIM, u"\u2516\u2500", NORMAL, " You are running a ", HILITE, "pre-release", NORMAL, " version: ",
            "the latest release version is ", INFO, oModuleVersionInformation.sLatestVersion, NORMAL, ".");
      elif oModuleVersionInformation.bUpToDate:
        pass;
      elif oModuleVersionInformation.sError:
        oConsole.fPrint(u"\u2502   ", ERROR, oModuleVersionInformation.sError, NORMAL, ".");
      else:
        oConsole.fPrint(u"\u2502   Version ", HILITE, oModuleVersionInformation.sLatestVersion, NORMAL,
            " is available at ", HILITE, oModuleVersionInformation.sUpdateURL, NORMAL, ".");
      uCounter += 1;
    oConsole.fPrint(u"\u2516", sPadding = u"\u2500");
    oConsole.fPrint();
  finally:
    oConsole.fUnlock();
