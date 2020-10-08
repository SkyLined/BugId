import sys;

from mColors import *;
from oConsole import oConsole;
from fPrintVersionInformation import fPrintVersionInformation;
from mDebugOutput import fConsoleOutputExceptionDetails;

def fPrintExceptionInformation(oException, oTraceback):
  fConsoleOutputExceptionDetails(oException, o0Traceback = oTraceback);
  oConsole.fLock();
  try:
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
    if not any([sVerbose in sys.argv[1:] for sVerbose in ["-v", "/v", "-V", "/V", "--verbose=true"]]):
      oConsole.fPrint("If you can reproduce the issue, it would help a lot if you can run BugId in");
      oConsole.fPrint("verbose mode by adding the ", INFO, "--verbose", NORMAL, " command-line argument.");
      oConsole.fPrint("as in: ", HILITE, "BugId -v ", " ".join(sys.argv[1:]));
      oConsole.fPrint();
    fPrintVersionInformation(
      bCheckForUpdates = False,
      bCheckAndShowLicenses = False,
      bShowInstallationFolders = False,
    );
    oConsole.fPrint("Thank you in advance for helping to improve BugId!");
  finally:
    oConsole.fUnlock();
