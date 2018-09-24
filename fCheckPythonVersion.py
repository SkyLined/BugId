import platform;
from faxListOutput import faxListOutput;
from mColors import *;
from oConsole import oConsole;

def fCheckPythonVersion(sApplicationName, asTestedPythonVersions, sBugURL):
  sPythonVersion = platform.python_version();
  uMajorVersion, uMinorVersion, uMicroVersion = [long(s) for s in sPythonVersion.split(".")];
  auTestedMajorVersions = set();
  bRunningInTestedMajorVersion = False;
  bRunningInTestedVersion = False;
  bRunningInOlderVersion = False;
  for sTestedPythonVersion in asTestedPythonVersions:
    uTestedMajorVersion, uTestedMinorVersion, uTestedMicroVersion = [long(s) for s in sTestedPythonVersion.split(".")];
    auTestedMajorVersions.add(uTestedMajorVersion);
    if uMajorVersion == uTestedMajorVersion:
      bRunningInTestedMajorVersion = True;
      if uMinorVersion == uTestedMinorVersion:
        if uMicroVersion == uTestedMicroVersion:
          # We are running in a tested Python version.
          bRunningInTestedVersion = True;
        elif uMicroVersion < uTestedMicroVersion:
          # This application was tested in a later version, so the version we are running in is outdated.
          bRunningInOlderVersion = True;
      elif uMinorVersion < uTestedMinorVersion:
        # This application was tested in a later version, so the version we are running in is outdated.
        bRunningInOlderVersion = True;
  if not bRunningInTestedMajorVersion:
    asTestedMayorVersions = [str(u) for u in auTestedMajorVersions];
    oConsole.fPrint(ERROR, "Error: rs requires ", ERROR_INFO, "Python %s" % faxListOutput(asMayorVersions, "or", ERROR_INFO, ERROR), ".");
    os._exit(3);
  if not bRunningInTestedVersion:
    oConsole.fLock();
    try:
      oConsole.fPrint(WARNING, u"\u250C\u2500", WARNING_INFO, " Warning ", WARNING, sPadding = u"\u2500");
      oConsole.fPrint(WARNING, u"\u2502 You are running ", "an older" if bRunningInOlderVersion else "a newer", " version of Python (", WARNING_INFO, sPythonVersion, WARNING,
          ") in which this version of");
      oConsole.fPrint(WARNING, u"\u2502 ", sApplicationName, " ", "was never tested" if bRunningInOlderVersion else "has not been tested yet", ". The following Python versions have been tested:");
      oConsole.fPrint(WARNING, u"\u2502   ", faxListOutput(asTestedPythonVersions, "and", WARNING_INFO, WARNING), ".");
      if bRunningInOlderVersion:
        oConsole.fPrint(WARNING, u"\u2502 Please update Python to the latest version!");
      else:
        oConsole.fPrint(WARNING, u"\u2502 Please report this so %s can be tested with this version of Python at:" % sApplicationName);
        oConsole.fPrint(WARNING, u"\u2502   ", WARNING_INFO | UNDERLINE, sBugURL);
      oConsole.fPrint(WARNING, u"\u2514", sPadding = u"\u2500");
    finally:
      oConsole.fUnlock();
  elif bRunningInOlderVersion:
    oConsole.fLock();
    try:
      oConsole.fPrint(WARNING, u"\u250C\u2500", WARNING_INFO, " Warning ", WARNING, sPadding = u"\u2500");
      oConsole.fPrint(WARNING, u"\u2502 You are running Python ", WARNING_INFO, sPythonVersion, WARNING, ", which is outdated.");
      oConsole.fPrint(WARNING, u"\u2502 Please update Python to the latest version!");
      oConsole.fPrint(WARNING, u"\u2514", sPadding = u"\u2500");
    finally:
      oConsole.fUnlock();
