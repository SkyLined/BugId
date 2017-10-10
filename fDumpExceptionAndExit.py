from cBugId import cBugId;
from mColors import *;
import mFileSystem;
import mWindowsAPI;
from oConsole import oConsole;
from oVersionInformation import oVersionInformation;

def fDumpExceptionAndExit(oException, oTraceBack):
  import platform, os, sys, traceback;
  oConsole.fPrint(ERROR, "-" * 80);
  oConsole.fPrint(ERROR, "- An internal exception has occured:");
  oConsole.fPrint(ERROR, "  %s" % repr(oException));
  oConsole.fPrint(ERROR,"  Stack:");
  atxStack = traceback.extract_tb(oTraceBack);
  uFrameIndex = len(atxStack) - 1;
  for (sFileName, uLineNumber, sFunctionName, sCode) in reversed(atxStack):
    sSource = "%s/%d" % (sFileName, uLineNumber);
    if sFunctionName != "<module>":
      sSource = "%s (%s)" % (sFunctionName, sSource);
    oConsole.fPrint(ERROR,"  %3d %s" % (uFrameIndex, sSource));
    if sCode:
      oConsole.fPrint(ERROR,"      > %s" % sCode.strip());
    uFrameIndex -= 1;
  oConsole.fPrint(ERROR,"  Windows version %s" % platform.version());
  oConsole.fPrint(ERROR,"  BugId version %s" % oVersionInformation.sCurrentVersion);
  for (sModule, xModule) in [
    ("mWindowsAPI", mWindowsAPI),
    ("mFileSystem", mFileSystem),
    ("oConsole", oConsole),
    ("cBugId", cBugId),
  ]:
    if hasattr(xModule, "oVersionInformation"):
      oConsole.fPrint(ERROR,"  %s version %s" % (sModule, xModule.oVersionInformation.sCurrentVersion));
    elif hasattr(xModule, "sVersion"):
      oConsole.fPrint(ERROR,"  %s version %s" % (sModule, xModule.sVersion));
    else:
      oConsole.fPrint(ERROR,"  %s version unknown" % sModule);
  oConsole.fPrint(ERROR, "-" * 80);
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
    oConsole.fPrint("as in:", HILITE, "BugId -v ", " ".join(sys.argv[1:]));
    oConsole.fPrint();
  oConsole.fPrint("Thank you in advance for helping to improve BugId!");
  os._exit(3);

