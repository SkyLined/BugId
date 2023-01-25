import platform, sys;

from mConsole import oConsole;

from faxListOutput import faxListOutput;
from mColorsAndChars import \
  CHAR_ERROR, \
  COLOR_ERROR, \
  COLOR_INFO, \
  COLOR_NORMAL, \
  CONSOLE_UNDERLINE, \
  COLOR_WARNING;
from mExitCodes import \
  guExitCodeInternalError;

def fCheckPythonVersion(sApplicationName, asTestedPythonVersions, sBugURL):
  sPythonVersion = platform.python_version();
  uMajorVersion, uMinorVersion, uMicroVersion = [int(s) for s in sPythonVersion.split(".")];
  auTestedMajorVersions = set();
  bRunningInTestedMajorVersion = False;
  bRunningInTestedVersion = False;
  bRunningInOlderVersion = False;
  for sTestedPythonVersion in asTestedPythonVersions:
    uTestedMajorVersion, uTestedMinorVersion, uTestedMicroVersion = [int(s) for s in sTestedPythonVersion.split(".")];
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
    asTestedMayorVersions = sorted(str(u) for u in auTestedMajorVersions);
    oConsole.fOutput(
      COLOR_ERROR, CHAR_ERROR,
      COLOR_NORMAL, " ", sApplicationName, " requires Python version ",
      faxListOutput(asTestedMayorVersions, "or", asTestedMayorVersions, COLOR_INFO, COLOR_NORMAL),
      COLOR_NORMAL, ".",
    );
    sys.exit(guExitCodeInternalError);
  if not bRunningInTestedVersion:
    oConsole.fLock();
    try:
      oConsole.fOutput("┌───[", COLOR_WARNING, " Warning ", COLOR_NORMAL, "]", sPadding = "─");
      oConsole.fOutput(
        "│ You are running a", "n older" if bRunningInOlderVersion else " newer", " version of Python (",
        COLOR_INFO, sPythonVersion,
        COLOR_NORMAL, ") in which this version of",
      );
      oConsole.fOutput(
        "│ ",
        COLOR_INFO, sApplicationName,
        COLOR_NORMAL, " ", "was never tested" if bRunningInOlderVersion else "has not been tested yet",
        ".",
      );
      oConsole.fOutput(
        "│ The following Python versions have been tested:",
      );
      oConsole.fOutput(
        "│   ",
        faxListOutput(asTestedPythonVersions, "and", asTestedPythonVersions, COLOR_INFO, COLOR_NORMAL),
        COLOR_NORMAL, ".",
      );
      if bRunningInOlderVersion:
        oConsole.fOutput(
          "│ Please update Python to the latest version!",
        );
      else:
        oConsole.fOutput(
          "│ Please report this so ", sApplicationName, " can be tested with this version of Python at the following URL:",
        );
        oConsole.fOutput(
          "│   ",
          COLOR_INFO | CONSOLE_UNDERLINE, sBugURL,
        );
      oConsole.fOutput("└", sPadding = "─");
    finally:
      oConsole.fUnlock();
  elif bRunningInOlderVersion:
    oConsole.fLock();
    try:
      oConsole.fOutput("┌───[",  COLOR_WARNING, " Warning ", COLOR_NORMAL, "]", sPadding = "─");
      oConsole.fOutput("│ You are running Python ", COLOR_INFO, sPythonVersion, COLOR_NORMAL, ", which is outdated.");
      oConsole.fOutput("│ Please update Python to the latest version!");
      oConsole.fOutput("└", sPadding = "─");
    finally:
      oConsole.fUnlock();
