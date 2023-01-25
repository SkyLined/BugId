import sys;

try:
  import mDebugOutput as m0DebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  m0DebugOutput = None;

from mColorsAndChars import *;
from foConsoleLoader import foConsoleLoader;
from fOutputVersionInformation import fOutputVersionInformation;
from fdsGetAdditionalVersionByName import fdsGetAdditionalVersionByName;
oConsole = foConsoleLoader();

def fOutputExceptionInformation(oException, oTraceback):
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
      oConsole.fOutput("  ", COLOR_INFO, oException.__class__.__name__, COLOR_NORMAL, "(");
      try:
        for xArg in oException.args:
          oConsole.fOutput("    ", COLOR_INFO, repr(xArg), COLOR_NORMAL, ",");
      except:
        oConsole.fOutput("    ", COLOR_INFO, repr(oException));
      oConsole.fOutput("  ", COLOR_NORMAL, ")");
    except:
      oConsole.fUnlock();
      raise;
  try:
    oConsole.fOutput();
    oConsole.fOutput("Please report the above details at the below web-page so it can be addressed:");
    oConsole.fOutput("    ", COLOR_INFO, "https://github.com/SkyLined/BugId/issues/new");
    oConsole.fOutput("If you do not have a github account, or you want to report this issue");
    oConsole.fOutput("privately, you can also send an email to:");
    oConsole.fOutput("    ", COLOR_INFO, "BugId@skylined.nl");
    oConsole.fOutput();
    oConsole.fOutput("In your report, please ", COLOR_HILITE, "copy ALL the information about the exception reported");
    oConsole.fOutput(COLOR_HILITE, "above, as well as the stack trace and BugId version information", COLOR_NORMAL, ". This makes");
    oConsole.fOutput("it easier to determine the cause of this issue and makes for faster fixes.");
    oConsole.fOutput();
    if not any([sVerbose in sys.argv[1:] for sVerbose in ["-v", "/v", "-V", "/V", "--verbose=true"]]):
      oConsole.fOutput("If you can reproduce the issue, it would help a lot if you can run BugId in");
      oConsole.fOutput("verbose mode by adding the ", COLOR_INFO, "--verbose", COLOR_NORMAL, " command-line argument.");
      oConsole.fOutput("as in: ", COLOR_HILITE, "BugId -v ", " ".join(sys.argv[1:]));
      oConsole.fOutput();
    fOutputVersionInformation(
      bCheckForUpdates = False,
      bShowInstallationFolders = False,
      dsAdditionalVersion_by_sName = fdsGetAdditionalVersionByName(),
    );
    oConsole.fOutput("Thank you in advance for helping to improve BugId!");
  finally:
    oConsole.fUnlock();
