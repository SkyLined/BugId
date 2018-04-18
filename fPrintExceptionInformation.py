from cBugId import cBugId;
from mColors import *;
import mFileSystem;
import mWindowsAPI;
from oConsole import oConsole;
from fPrintVersionInformation import fPrintVersionInformation;

def fPrintExceptionInformation(oException, oTraceBack):
  import os, sys, traceback;
  oConsole.fLock();
  try:
    oConsole.fPrint(ERROR, u"\u250C\u2500", ERROR_INFO, " An internal exception has occured ", ERROR, sPadding = u"\u2500");
    oConsole.fPrint(ERROR, u"\u2502 ", ERROR_INFO, repr(oException));
    oConsole.fPrint(ERROR, u"\u2502");
    oConsole.fPrint(ERROR, u"\u2502  Stack:");
    atxStack = traceback.extract_tb(oTraceBack);
    uFrameIndex = 0;
    for (sFileName, uLineNumber, sFunctionName, sCode) in reversed(atxStack):
      asSource = [ERROR_INFO, sFileName, ERROR, "/", str(uLineNumber)];
      if sFunctionName != "<module>":
        asSource = [HILITE, sFunctionName, ERROR, " @ "] + asSource;
      oConsole.fPrint(ERROR, u"\u2502 %3d " % uFrameIndex, *asSource);
      if sCode:
        oConsole.fPrint(ERROR, u"\u2502      > ", NORMAL, sCode.strip(), uConvertTabsToSpaces = 2);
      uFrameIndex += 1;
    oConsole.fPrint(ERROR, u"\u2514", sPadding = u"\u2500");
    oConsole.fPrint();
    oConsole.fPrint("Please report the above details at the below web-page so it can be addressed:");
    oConsole.fPrint(INFO, "    https://github.com/SkyLined/BugId/issues/new");
    oConsole.fPrint("If you do not have a github account, or you want to report this issue");
    oConsole.fPrint("privately, you can also send an email to:");
    oConsole.fPrint(INFO, "    BugId@skylined.nl");
    oConsole.fPrint();
    oConsole.fPrint("In your report, please copy the information about the exception reported");
    oConsole.fPrint("above, as well as the stack trace and BugId version information. This makes");
    oConsole.fPrint("it easier to determine the cause of this issue and makes for faster fixes.");
    oConsole.fPrint();
    if "-v" not in sys.argv[1:] and "/v" not in sys.argv[1:] and "--verbose=true" not in sys.argv[1:]:
      oConsole.fPrint("If you can reproduce the issue, it would help a lot if you can run BugId in");
      oConsole.fPrint("verbose mode by adding the ", INFO, "--verbose", NORMAL, " command-line argument.");
      oConsole.fPrint("as in: ", HILITE, "BugId -v ", " ".join(sys.argv[1:]));
      oConsole.fPrint();
    fPrintVersionInformation(
      bCheckForUpdates = False,
      bCheckAndShowLicenses = False,
      bShowInstallationFolders = False,
    );
    oConsole.fPrint();
    oConsole.fPrint("Thank you in advance for helping to improve BugId!");
  finally:
    oConsole.fUnlock();
