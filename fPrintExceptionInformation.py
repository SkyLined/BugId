import sys;

try:
  import mDebugOutput as m0DebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  m0DebugOutput = None;

from mConsole import oConsole;

from mColors import *;
from fPrintVersionInformation import fPrintVersionInformation;

def fPrintExceptionInformation(oException, oTraceback):
  if m0DebugOutput:
    m0DebugOutput.fConsoleOutputExceptionDetails(oException, o0Traceback = oTraceback);
    oConsole.fLock();
  else:
    oConsole.fLock();
    try:
      oConsole.fOutput("An internal exception has happened but the 'mDebugOutput' module is not");
      oConsole.fOutput("available to show advanced details. Please download this module to get");
      oConsole.fOutput("more detailed information about this issue.");
      oConsole.fOutput();
      oConsole.fOutput("Here's the exception:");
      oConsole.fOutput("  ", ERROR_INFO, oException.__class__.__name__, ERROR, "(");
      try:
        for xArg in oException.args:
          oConsole.fOutput("    ", ERROR_INFO, repr(xArg), ERROR, ",");
      except:
        oConsole.fOutput("    ", ERROR_INFO, repr(oException));
      oConsole.fOutput("  ", ERROR, ")");
    except:
      oConsole.fUnlock();
      raise;
  try:
    oConsole.fOutput();
    oConsole.fOutput("Please report the above details at the below web-page so it can be addressed:");
    oConsole.fOutput(INFO, "    https://github.com/SkyLined/BugId/issues/new");
    oConsole.fOutput("If you do not have a github account, or you want to report this issue");
    oConsole.fOutput("privately, you can also send an email to:");
    oConsole.fOutput(INFO, "    BugId@skylined.nl");
    oConsole.fOutput();
    oConsole.fOutput("In your report, please ", HILITE, "copy ALL the information about the exception reported");
    oConsole.fOutput(HILITE, "above, as well as the stack trace and BugId version information", NORMAL, ". This makes");
    oConsole.fOutput("it easier to determine the cause of this issue and makes for faster fixes.");
    oConsole.fOutput();
    if not any([sVerbose in sys.argv[1:] for sVerbose in ["-v", "/v", "-V", "/V", "--verbose=true"]]):
      oConsole.fOutput("If you can reproduce the issue, it would help a lot if you can run BugId in");
      oConsole.fOutput("verbose mode by adding the ", INFO, "--verbose", NORMAL, " command-line argument.");
      oConsole.fOutput("as in: ", HILITE, "BugId -v ", " ".join(sys.argv[1:]));
      oConsole.fOutput();
    fPrintVersionInformation(
      bCheckForUpdates = False,
      bShowInstallationFolders = False,
    );
    oConsole.fOutput("Thank you in advance for helping to improve BugId!");
  finally:
    oConsole.fUnlock();
