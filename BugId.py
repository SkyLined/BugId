import codecs, json, re, os, sys, threading;
# Prevent unicode strings from throwing exceptions when output to the console.
sys.stdout = codecs.getwriter("cp437")(sys.stdout, "replace");
# The CWD may not be this script's folder; make sure it looks there for modules first:
sBaseFolderPath = os.path.dirname(__file__);
for sPath in [sBaseFolderPath] + [os.path.join(sBaseFolderPath, x) for x in ["modules"]]:
  sys.path.insert(0, sPath);

from dxConfig import dxConfig;
from cBugId import cBugId;
try:
  import FileSystem;
except:
  print "*" * 80;
  print "BugId.py depends on FileSystem, which you can download at https://github.com/SkyLined/FileSystem/";
  print "*" * 80;
  raise;

# Rather than a command line, a known application keyword can be provided. The default command line for such applications can be provided below and will
# be used if the keyword is provided as the command line by the user:
sProgramFilesPath = os.getenv("ProgramFiles");
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");
gasApplicationCommandLine_by_sKnownApplicationKeyword = {
  "chrome": [r"%s\Google\Chrome\Application\chrome.exe" % sProgramFilesPath_x86, "%test%", "--disable-default-apps", "--disable-extensions", "--disable-popup-blocking", "--disable-prompt-on-repost", "--force-renderer-accessibility", "--no-sandbox"],
  "firefox": [r"%s\Mozilla Firefox\firefox.exe" % sProgramFilesPath_x86, "%test%", "--no-remote", "-profile", "%s\Firefox-profile" % os.getenv("TEMP")],
  "nightly": [r"%s\Mozilla Firefox Nightly\build\dist\bin\firefox.exe" % os.getenv("LocalAppData"), "%test%", "--no-remote", "-profile", r"%s\Firefox-nightly-profile" % os.getenv("TEMP")], # has no default path; this is what I use.
  "msie": [r"%s\Internet Explorer\iexplore.exe" % sProgramFilesPath, "%test%"],
  "msie64": [r"%s\Internet Explorer\iexplore.exe" % sProgramFilesPath_x64, "%test%"],
  "msie86": [r"%s\Internet Explorer\iexplore.exe" % sProgramFilesPath_x86, "%test%"],
  "foxit": [r"%s\Foxit Software\Foxit Reader\FoxitReader.exe" % sProgramFilesPath_x86, "%test%"],
};

# Known applications can have regular expressions that map source file paths in its output to URLs, so the details HTML for any detected bug can have clickable
# links to an online source repository:
srMozillaCentralSourceURLMappings = "".join([
  r"c:[\\/]builds[\\/]moz2_slave[\\/][^\\/]+[\\/]build[\\/](?:src[\\/])?", # absolute file path
  r"(?P<path>[^:]+\.\w+)", # relative file path
  r"(:| @ |, line )", # separator
  r"(?P<lineno>\d+)",  # line number
]);
gdsURLTemplate_by_srSourceFilePath_by_sKnownApplicationKeyword = {
  "firefox": {srMozillaCentralSourceURLMappings: "https://mxr.mozilla.org/mozilla-central/source/%(path)s#%(lineno)s"},
  "nightly": {srMozillaCentralSourceURLMappings: "https://dxr.mozilla.org/mozilla-central/source/%(path)s#%(lineno)s"},
};
# Known applications can also have regular expressions that detect important lines in its stdout/stderr output. These will be shown prominently in the details
# HTML for any detected bug.
grImportantStdOutLines_by_sKnownApplicationKeyword = {};
grImportantStdErrLines_by_sKnownApplicationKeyword = {
  "nightly": re.compile("^((\?h)+: C)*(%s)$" % "|".join([
    r"Assertion failure: .*",
    r"Hit MOZ_CRASH: .*",
    r"\[Child \w+\] ###!!!ABORT: .*",
  ])),
};

if __name__ == "__main__":
  asArguments = sys.argv[1:];
  if len(asArguments) == 0:
    print "Usage:";
    print "  BugId.py [options] \"path\\to\\binary.exe\" [arguments]";
    print "    Start the executable in the debugger with the provided arguments.";
    print "";
    print "  BugId.py [options] \"known application id\" [test url or file path]";
    print "    Start a known application and open the given url or file.";
    print "    Valid ids: %s" % ", ".join(sorted(gasApplicationCommandLine_by_sKnownApplicationKeyword.keys()));
    print "";
    print "  BugId.py [options] --pids=[comma separated list of process ids]";
    print "    Attach debugger to the process(es) provided in the list. The processes must";
    print "    all have been suspended, as they will be resumed by the debugger.";
    print "";
    print "Options:";
    print "  --bSaveReport=false";
    print "    Do not save a HTML formatted crash report.";
    print "  --BugId.bSaveDump=true";
    print "    Save a dump file when a crash is detected.";
    print "  --BugId.bOutputStdIn=true, --BugId.bOutputStdOut=true, --BugId.bOutputStdErr=true";
    print "    Show verbose cdb input / output during debugging.";
    print "  --BugId.asSymbolServerURLs=[\"http://msdl.microsoft.com/download/symbols\"]";
    print "    Use http://msdl.microsoft.com/download/symbols as a symbol server.";
    print "  --BugId.asSymbolCachePaths=[\"C:\\Symbols\"]";
    print "    Use C:\\Symbols to cache symbol files.";
    print "  See dxConfig.py and srv\dxBugIdConfig.py for a list of settings that you can";
    print "  change. All values must be valid JSON of the appropriate type. No checks are";
    print "  made to ensure this. Providing illegal values may result in exceptions at any";
    print "  time during execution. You have been warned.";
    os._exit(0);
  auApplicationProcessIds = None;
  while len(asArguments) and asArguments[0].startswith("--"):
    if asArguments[0].startswith("--pids="):
      auApplicationProcessIds = [int(x) for x in asArguments[0].split("=", 1)[1].split(",")];
    else:
      sSettingName, sValue = asArguments[0][2:].split("=", 1);
      xValue = json.loads(sValue);
      asGroupNames = sSettingName.split("."); # last element is not a group name
      sFullName = ".".join(asGroupNames);
      sSettingName = asGroupNames.pop();          # so pop it.
      dxConfigGroup = dxConfig;
      asHandledGroupNames = [];
      for sGroupName in asGroupNames:
        asHandledGroupNames.append(sGroupName);
        assert sGroupName in dxConfigGroup, \
            "Unknown config group %s in setting name %s." % (repr(".".join(asHandledGroupNames)), repr(sFullName));
        dxConfigGroup = dxConfigGroup.get(sGroupName, {});
      assert sSettingName in dxConfigGroup, \
          "Unknown setting name %s%s." % (sSettingName, \
              len(asHandledGroupNames) > 0 and " in config group %s" % ".".join(asHandledGroupNames) or "");
      if json.dumps(dxConfigGroup[sSettingName]) == json.dumps(xValue):
        print "* The default value for config setting %s is %s." % (sFullName, repr(dxConfigGroup[sSettingName]));
      else:
        print "+ Changed config setting %s from %s to %s." % (sFullName, repr(dxConfigGroup[sSettingName]), repr(xValue));
        dxConfigGroup[sSettingName] = xValue;
    asArguments.pop(0);
  asApplicationCommandLine = len(asArguments) and asArguments or None;
  # Rather than a command line, a known application keyword can be provided:
  sKnownApplicationKeyword = asApplicationCommandLine and asApplicationCommandLine[0].lower() or None; 
  if sKnownApplicationKeyword in gasApplicationCommandLine_by_sKnownApplicationKeyword:
    if len(asApplicationCommandLine) == 2:
      dxConfig["sTest"] = asApplicationCommandLine[1];
    elif len(asApplicationCommandLine) > 2:
      print "- Superfluous arguments after known application keyword: %s" % " ".join(asApplicationCommandLine[2:]);
      os._exit(-1);
    # Translate known application keyword to its command line:
    asApplicationCommandLine = gasApplicationCommandLine_by_sKnownApplicationKeyword[sKnownApplicationKeyword];
    # Get source file path to URL translation rules for known application:
    dsURLTemplate_by_srSourceFilePath = gdsURLTemplate_by_srSourceFilePath_by_sKnownApplicationKeyword.get(sKnownApplicationKeyword, {});
    # Get important stdout/stderr lines rules for known application:
    rImportantStdOutLines = grImportantStdOutLines_by_sKnownApplicationKeyword.get(sKnownApplicationKeyword);
    rImportantStdErrLines = grImportantStdErrLines_by_sKnownApplicationKeyword.get(sKnownApplicationKeyword);
  else:
    dsURLTemplate_by_srSourceFilePath = {};
    rImportantStdOutLines = None;
    rImportantStdErrLines = None;
  if asApplicationCommandLine is not None:
    # replace "%test%" with dxConfig["sTest"] in the command line
    asApplicationCommandLine = [s.replace("%test%", dxConfig["sTest"]) for s in asApplicationCommandLine];
  
  oBugId = None;
  
  bApplicationIsStarted = asApplicationCommandLine is None; # if we're attaching the application is already started.
  bCheckForExcessiveCPUUsageTimeoutSet = False;
  def fApplicationRunningHandler():
    global bApplicationIsStarted, bCheckForExcessiveCPUUsageTimeoutSet;
    if not bApplicationIsStarted:
      # Running for the first time after being started.
      bApplicationIsStarted = True;
      print "+ The application was started successfully and is running...";
      if dxConfig["nApplicationMaxRunTime"] is not None:
        oBugId.fxSetTimeout(dxConfig["nApplicationMaxRunTime"], fHandleApplicationRunTimeout);
    else:
      # Running after being resumed.
      print "  * T+%.1f The application was resumed successfully and is running..." % oBugId.fnApplicationRunTime();
    if not bCheckForExcessiveCPUUsageTimeoutSet:
      # Start checking for excessive CPU usage
      bCheckForExcessiveCPUUsageTimeoutSet = True;
      oBugId.fSetCheckForExcessiveCPUUsageTimeout(dxConfig["nExcessiveCPUUsageCheckInitialTimeout"]);
  
  def fExceptionDetectedHandler(uCode, sDescription):
    print "  * T+%.1f Exception code 0x%X (%s) was detected and is being analyzed..." % (oBugId.fnApplicationRunTime(), uCode, sDescription);
  
  def fHandleApplicationRunTimeout():
    print "  * T+%.1f Terminating the application because it has been running for %.1f seconds without crashing." % \
        (oBugId.fnApplicationRunTime(), dxConfig["nApplicationMaxRunTime"]);
    oBugId.fStop();
  
  def fApplicationExitHandler():
    print "  * T+%.1f The application has exited..." % oBugId.fnApplicationRunTime();
    oBugId.fStop();
  
  if asApplicationCommandLine:
    print "+ The debugger is starting the application...";
    print "  Command line: %s" % " ".join(asApplicationCommandLine);
  else:
    print "+ The debugger is attaching to the application...";
  oBugId = cBugId(
    asApplicationCommandLine = asApplicationCommandLine,
    auApplicationProcessIds = auApplicationProcessIds,
    asSymbolServerURLs = dxConfig["asSymbolServerURLs"],
    dsURLTemplate_by_srSourceFilePath = dsURLTemplate_by_srSourceFilePath,
    rImportantStdOutLines = rImportantStdOutLines,
    rImportantStdErrLines = rImportantStdErrLines,
    bGetDetailsHTML = dxConfig["bSaveReport"],
    fApplicationRunningCallback = fApplicationRunningHandler,
    fExceptionDetectedCallback = fExceptionDetectedHandler,
    fApplicationExitCallback = fApplicationExitHandler,
  );
  oBugId.fWait();
  if oBugId.oBugReport:
    print "+ A bug was detected in the application.";
    print;
    print "  Id:               %s" % oBugId.oBugReport.sId;
    print "  Description:      %s" % oBugId.oBugReport.sBugDescription;
    print "  Location:         %s" % oBugId.oBugReport.sBugLocation;
    if oBugId.oBugReport.sBugSourceLocation:
      print "  Source:           %s" % oBugId.oBugReport.sBugSourceLocation;
    print "  Security impact:  %s" % oBugId.oBugReport.sSecurityImpact;
    print "  Run time:         %f seconds" % long(oBugId.fnApplicationRunTime() * 1000) / 1000.0;
    if dxConfig["bSaveReport"]:
      sReportFileName = "%s @ %s.html" % (oBugId.oBugReport.sId, oBugId.oBugReport.sBugLocation);
      eWriteDataToFileResult = FileSystem.feWriteDataToFile(
        oBugId.oBugReport.sDetailsHTML,
        FileSystem.fsLocalPath(FileSystem.fsTranslateToValidName(sReportFileName)),
        fbRetryOnFailure = lambda: False,
      );
      if eWriteDataToFileResult:
        print "  Bug report:       Cannot be saved (%s)" % repr(eWriteDataToFileResult);
      else:
        print "  Bug report:       %s (%d bytes)" % (sReportFileName, len(oBugId.oBugReport.sDetailsHTML));
  else:
    print "- The application has terminated without crashing.";
    print "  Run time:         %f seconds" % long(oBugId.fnApplicationRunTime() * 1000) / 1000.0;
  
  if dxConfig["bShowLincenseAndDonationInfo"]:
    print;
    print "This version of BugId is provided free of charge for non-commercial use only.";
    print "If you find it useful and would like to make a donation, you can send bitcoin";
    print "to 183yyxa9s1s1f7JBpPHPmzQ346y91Rx5DX. Please contact the author if you wish to";
    print "use BugId commercially. Contact and licensing information can be found at";
    print "https://github.com/SkyLined/BugId#license.";
