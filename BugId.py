import codecs, json, re, os, sys, threading, time;
# Prevent unicode strings from throwing exceptions when output to the console.
sys.stdout = codecs.getwriter("cp437")(sys.stdout, "replace");
# The CWD may not be this script's folder; make sure it looks there for modules first:
sBaseFolderPath = os.path.dirname(__file__);
for sPath in [sBaseFolderPath] + [os.path.join(sBaseFolderPath, x) for x in ["modules"]]:
  if sPath not in sys.path:
    sys.path.insert(0, sPath);

from dxConfig import dxConfig;
from sVersion import sVersion;
from fPrintUsage import fPrintUsage;
try:
  from cBugId import cBugId;
except:
  print "*" * 80;
  print "BugId.py depends on cBugId, which you can download at:";
  print "    https://github.com/SkyLined/cBugId/";
  print "After downloading, please copy the files to the \"modules\\cBugId\" folder.";
  print "*" * 80;
  raise;
try:
  import FileSystem;
except:
  print "*" * 80;
  print "BugId.py depends on FileSystem, which you can download at:";
  print "    https://github.com/SkyLined/FileSystem/";
  print "After downloading, please copy the files to the \"modules\\FileSystem\" folder.";
  print "*" * 80;
  raise;

# Rather than a command line, a known application keyword can be provided. The default command line for such applications can be provided below and will
# be used if the keyword is provided as the command line by the user:
sProgramFilesPath = os.getenv("ProgramFiles");
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");
# ISA = Instruction Set Architecture
sLocalAppData = os.getenv("LocalAppData");
from ChromePath import sChromePath_x64, sChromePath_x86, sChromePath, \
    sChromeSxSPath_x64, sChromeSxSPath_x86, sChromeSxSPath;
from FirefoxPath import sFirefoxPath_x64, sFirefoxPath_x86, sFirefoxPath, \
    sFirefoxDevPath_x64, sFirefoxDevPath_x86, sFirefoxDevPath;
from MSIEPath import sMSIEPath_x64, sMSIEPath_x86, sMSIEPath;
gdApplication_asCommandLine_by_sKeyword = {
  "aoo-writer": [r"%s\OpenOffice 4\program\swriter.exe" % sProgramFilesPath_x86, "-norestore", "-view", "-nologo", "-nolockcheck"],
  "acrobat": [r"%s\Adobe\Reader 11.0\Reader\AcroRd32.exe" % sProgramFilesPath_x86],
  "acrobatdc": [r"%s\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe" % sProgramFilesPath_x86],
  "chrome": [sChromePath, "--disable-default-apps", "--disable-extensions", "--disable-popup-blocking", "--disable-prompt-on-repost", "--force-renderer-accessibility", "--no-sandbox"],
  "chrome_x86": [sChromePath_x86, "--disable-default-apps", "--disable-extensions", "--disable-popup-blocking", "--disable-prompt-on-repost", "--force-renderer-accessibility", "--no-sandbox"],
  "chrome_x64": [sChromePath_x64, "--disable-default-apps", "--disable-extensions", "--disable-popup-blocking", "--disable-prompt-on-repost", "--force-renderer-accessibility", "--no-sandbox"],
  "chrome-sxs": [sChromeSxSPath, "--disable-default-apps", "--disable-extensions", "--disable-popup-blocking", "--disable-prompt-on-repost", "--force-renderer-accessibility", "--no-sandbox"],
  "chrome-sxs_x86": [sChromeSxSPath_x86, "--disable-default-apps", "--disable-extensions", "--disable-popup-blocking", "--disable-prompt-on-repost", "--force-renderer-accessibility", "--no-sandbox"],
  "chrome-sxs_x64": [sChromeSxSPath_x64, "--disable-default-apps", "--disable-extensions", "--disable-popup-blocking", "--disable-prompt-on-repost", "--force-renderer-accessibility", "--no-sandbox"],
  "firefox": [sFirefoxPath, "--no-remote", "-profile", "%s\Firefox-profile" % os.getenv("TEMP")],
  "firefox_x86": [sFirefoxPath_x86, "--no-remote", "-profile", "%s\Firefox-profile" % os.getenv("TEMP")],
  "firefox_x64": [sFirefoxPath_x64, "--no-remote", "-profile", "%s\Firefox-profile" % os.getenv("TEMP")],
  "firefox-dev": [sFirefoxDevPath, "--no-remote", "-profile", "%s\Firefox-profile" % os.getenv("TEMP")],
  "firefox-dev_x86": [sFirefoxDevPath_x86, "--no-remote", "-profile", "%s\Firefox-profile" % os.getenv("TEMP")],
  "firefox-dev_x64": [sFirefoxDevPath_x64, "--no-remote", "-profile", "%s\Firefox-profile" % os.getenv("TEMP")],
  "foxit": [r"%s\Foxit Software\Foxit Reader\FoxitReader.exe" % sProgramFilesPath_x86],
  "msie": [sMSIEPath],
  "msie_x86": [sMSIEPath_x86],
  "msie_x64": [sMSIEPath_x64],
  "nightly": [r"%s\Mozilla Firefox Nightly\build\dist\bin\firefox.exe" % os.getenv("LocalAppData"), "--no-remote", "-profile", r"%s\Firefox-nightly-profile" % os.getenv("TEMP")], # has no default path; this is what I use.
};
DEFAULT_BROWSER_TEST_URL = {}; # Placeholder for dxConfig["sDefaultBrowserTestURL"]
gdApplication_asDefaultAdditionalArguments_by_sKeyword = {
  "acrobat": ["repro.pdf"],
  "acrobatdc": ["repro.pdf"],
  "chrome": [DEFAULT_BROWSER_TEST_URL],
  "chrome_x86": [DEFAULT_BROWSER_TEST_URL],
  "chrome_x64": [DEFAULT_BROWSER_TEST_URL],
  "firefox": [DEFAULT_BROWSER_TEST_URL],
  "firefox_x86": [DEFAULT_BROWSER_TEST_URL],
  "firefox_x64": [DEFAULT_BROWSER_TEST_URL],
  "foxit": ["repro.pdf"],
  "msie": [DEFAULT_BROWSER_TEST_URL],
  "msie_x86": [DEFAULT_BROWSER_TEST_URL],
  "msie_x64": [DEFAULT_BROWSER_TEST_URL],
  "nightly": [DEFAULT_BROWSER_TEST_URL],
};
gdApplication_sISA_by_sKeyword = {
  # Applications will default to cBugId.sOSISA. Applications need only be added here if they can differ from that.
  "aoo-writer": "x86",
  "acrobat": "x86",
  "acrobatdc": "x86",
  "chrome_x86": "x86",
  "chrome_x64": "x64",
  "firefox_x86": "x86",
  "firefox_x64": "x64",
  "foxit": "x86",
  "msie_x86": "x86",
  "msie_x64": "x64",
  "nightly": "x86",
};
dxBrowserSettings = {
  # Settings used by all browsers (these should eventually be fine-tuned for each browser)
  "bApplicationTerminatesWithMainProcess": True,
  "nExcessiveCPUUsageCheckInitialTimeout": 30.0, # Give browser some time to load repro
  "cBugId.nExcessiveCPUUsageCheckInterval": 30.0, # Browser may be busy for a bit, but no longer than 30 seconds.
  "cBugId.nExcessiveCPUUsagePercent": 95,      # Browser msust be very, very busy.
  "cBugId.nExcessiveCPUUsageWormRunTime": 0.5, # Any well written function should return within half a second IMHO.
};

gdApplication_dxSettings_by_sKeyword = {
  "aoo-writer": {
    "bApplicationTerminatesWithMainProcess": True,
    "nApplicationMaxRunTime": 10.0, # Writer can be a bit slow to load, so give it some time.
    "nExcessiveCPUUsageCheckInitialTimeout": 10.0, # Give application some time to load repro
    "cBugId.nExcessiveCPUUsageCheckInterval": 5.0, # Application should not be busy for more than 5 seconds.
    "cBugId.nExcessiveCPUUsagePercent": 75,      # Application must be relatively busy.
    "cBugId.nExcessiveCPUUsageWormRunTime": 0.5, # Any well written function should return within half a second IMHO.
  },
  "acrobat": {
    "nApplicationMaxRunTime": 60.0, # Really slow.
    "nExcessiveCPUUsageCheckInitialTimeout": 30.0, # Give application some time to load repro
    "cBugId.nExcessiveCPUUsageCheckInterval": 5.0, # Application should not be busy for more than 5 seconds.
    "cBugId.nExcessiveCPUUsagePercent": 75,      # Application must be relatively busy.
    "cBugId.nExcessiveCPUUsageWormRunTime": 0.5, # Any well written function should return within half a second IMHO.
  },
  "acrobatdc": {
    "nApplicationMaxRunTime": 60.0, # Really slow.
    "nExcessiveCPUUsageCheckInitialTimeout": 30.0, # Give application some time to load repro
    "cBugId.nExcessiveCPUUsageCheckInterval": 5.0, # Application should not be busy for more than 5 seconds.
    "cBugId.nExcessiveCPUUsagePercent": 75,      # Application must be relatively busy.
    "cBugId.nExcessiveCPUUsageWormRunTime": 0.5, # Any well written function should return within half a second IMHO.
  },
  "chrome": dxBrowserSettings,
  "chrome_x86": dxBrowserSettings,
  "chrome_x64": dxBrowserSettings,
  "chrome": dxBrowserSettings,
  "edge": dxBrowserSettings,
  "firefox": dxBrowserSettings,
  "firefox_x86": dxBrowserSettings,
  "firefox_x64": dxBrowserSettings,
  "foxit": {
    "bApplicationTerminatesWithMainProcess": True,
    "nApplicationMaxRunTime": 10.0, # Normally loads within 2 seconds, but give it some more to be sure.
    "nExcessiveCPUUsageCheckInitialTimeout": 10.0, # Give application some time to load repro
    "cBugId.nExcessiveCPUUsageCheckInterval": 5.0, # Application should not be busy for more than 5 seconds.
    "cBugId.nExcessiveCPUUsagePercent": 75,      # Application must be relatively busy.
    "cBugId.nExcessiveCPUUsageWormRunTime": 0.5, # Any well written function should return within half a second IMHO.
  },
  "msie": dxBrowserSettings, 
  "msie_x86": dxBrowserSettings,
  "msie_x64": dxBrowserSettings,
};

# Known applications can have regular expressions that map source file paths in its output to URLs, so the details HTML for any detected bug can have clickable
# links to an online source repository:
srMozillaCentralSourceURLMappings = "".join([
  r"c:[\\/]builds[\\/]moz2_slave[\\/][^\\/]+[\\/]build[\\/](?:src[\\/])?", # absolute file path
  r"(?P<path>[^:]+\.\w+)", # relative file path
  r"(:| @ |, line )", # separator
  r"(?P<lineno>\d+)",  # line number
]);
gdApplication_sURLTemplate_by_srSourceFilePath_by_sKeyword = {
  "firefox": {srMozillaCentralSourceURLMappings: "https://mxr.mozilla.org/mozilla-central/source/%(path)s#%(lineno)s"},
  "firefox_x86": {srMozillaCentralSourceURLMappings: "https://mxr.mozilla.org/mozilla-central/source/%(path)s#%(lineno)s"},
  "firefox_x64": {srMozillaCentralSourceURLMappings: "https://mxr.mozilla.org/mozilla-central/source/%(path)s#%(lineno)s"},
  "nightly": {srMozillaCentralSourceURLMappings: "https://dxr.mozilla.org/mozilla-central/source/%(path)s#%(lineno)s"},
};
# Known applications can also have regular expressions that detect important lines in its stdout/stderr output. These will be shown prominently in the details
# HTML for any detected bug.
gdApplication_rImportantStdOutLines_by_sKeyword = {};
gdApplication_rImportantStdErrLines_by_sKeyword = {
  "nightly": re.compile("^((\?h)+: C)*(%s)$" % "|".join([
    r"Assertion failure: .*",
    r"Hit MOZ_CRASH: .*",
    r"\[Child \w+\] ###!!!ABORT: .*",
  ])),
};

asApplicationKeywords = sorted(list(set(
  gdApplication_asCommandLine_by_sKeyword.keys() +
  gdApplication_asDefaultAdditionalArguments_by_sKeyword.keys() +
  gdApplication_dxSettings_by_sKeyword.keys() +
  gdApplication_sURLTemplate_by_srSourceFilePath_by_sKeyword.keys() + 
  gdApplication_rImportantStdOutLines_by_sKeyword.keys() +
  gdApplication_rImportantStdErrLines_by_sKeyword.keys()
)));

def fuShowApplicationKeyWordHelp(sApplicationKeyword):
  if sApplicationKeyword not in asApplicationKeywords:
    print "- Unknown application keyword %s" % sApplicationKeyword;
    return 2;
  print "Known application settings for %s" % sApplicationKeyword;
  if sApplicationKeyword in gdApplication_asCommandLine_by_sKeyword:
    if gdApplication_asCommandLine_by_sKeyword[sApplicationKeyword][0] is None:
      print "  Not installed";
    else:
      print "  Base command-line:";
      print "    %s" % " ".join(gdApplication_asCommandLine_by_sKeyword[sApplicationKeyword]);
  if sApplicationKeyword in gdApplication_asDefaultAdditionalArguments_by_sKeyword:
    print "  Default additional arguments:";
    print "    %s" % " ".join([
      sArgument is DEFAULT_BROWSER_TEST_URL and dxConfig["sDefaultBrowserTestURL"] or sArgument
      for sArgument in gdApplication_asDefaultAdditionalArguments_by_sKeyword[sApplicationKeyword]
    ]);
  if sApplicationKeyword in gdApplication_dxSettings_by_sKeyword:
    print "  Application specific settings:";
    for sSettingName, xValue in gdApplication_dxSettings_by_sKeyword[sApplicationKeyword].items():
      print "    %s = %s" % (sSettingName, json.dumps(xValue));
  return 0;

def fApplyConfigSetting(sSettingName, xValue, sIndentation  = ""):
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
    print "%s* The default value for config setting %s is %s." % (sIndentation, sFullName, repr(dxConfigGroup[sSettingName]));
  else:
    print "%s+ Changed config setting %s from %s to %s." % (sIndentation, sFullName, repr(dxConfigGroup[sSettingName]), repr(xValue));
    dxConfigGroup[sSettingName] = xValue;

def fApplicationRunningHandler(oBugId):
  print "+ The application was started successfully and is running.";

def fApplicationSuspendedHandler(oBugId):
  print "  * T+%.1f The application is suspended..." % (oBugId.fnApplicationRunTime());

def fApplicationResumedHandler(oBugId):
  print "    * And resumed...";

def fApplicationRunTimeoutHandler(oBugId):
  print "  * T+%.1f The application has been running for %.1f seconds without crashing and will be terminated..." % \
      (oBugId.fnApplicationRunTime(), dxConfig["nApplicationMaxRunTime"]);
  oBugId.fStop();

def fMainProcessTerminatedHandler(oBugId):
  if dxConfig["bApplicationTerminatesWithMainProcess"]:
    print "  * T+%.1f One of the main processes has terminated, stopping..." % oBugId.fnApplicationRunTime();
    oBugId.fStop();
  else:
    print "  * T+%.1f One of the main processes has terminated." % oBugId.fnApplicationRunTime();

def fuMain(asArguments):
  # returns an exit code, values are:
  # 0 = executed successfully, no bugs found.
  # 1 = executed successfully, bug detected.
  # 2 = bad arguments
  # 3 = internal error
  # 4 = failed to start process or attach to process(es).
  # Parse all "--" arguments until we encounter a non-"--" argument.
  auApplicationProcessIds = [];
  sApplicationISA = None;
  bForever = False;
  dxUserProvidedConfigSettings = {};
  while asArguments and asArguments[0].startswith("--"):
    sArgument = asArguments.pop(0);
    if "=" in sArgument:
      sSettingName, sValue = sArgument[2:].split("=", 1);
    else:
      # "--bFlag" is an alias for "--bFlag=true"
      sSettingName = sArgument[2:];
      sValue = True;
    if sSettingName in ["pid", "pids"]:
      auApplicationProcessIds += [long(x) for x in sValue.split(",")];
    elif sSettingName == "isa":
      if sValue not in ["x86", "x64"]:
        print "- Unknown ISA %s" % repr(sValue);
        return 2;
      sApplicationISA = sValue;
    elif sSettingName == "fast":
      # Alias for these three settings:
      dxUserProvidedConfigSettings["bGenerateReportHTML"] = False;
      dxUserProvidedConfigSettings["asSymbolServerURLs"] = [];
      dxUserProvidedConfigSettings["cBugId.bUse_NT_SYMBOL_PATH"] = False;
    elif sSettingName == "forever":
      bForever = True;
    else:
      try:
        xValue = json.loads(sValue);
      except ValueError:
        print "- Cannot decode argument JSON value %s" % sValue;
        return 2;
      # User provided config settings must be applied after any keyword specific config settings:
      dxUserProvidedConfigSettings[sSettingName] = xValue;
  dsURLTemplate_by_srSourceFilePath = {};
  rImportantStdOutLines = None;
  rImportantStdErrLines = None;
  # If there are any additional arguments, it must be an application keyword followed by additional arguments
  # or an application command-line:
  if not asArguments:
    # No keyword or command line: process ids to attach to must be provided
    asApplicationCommandLine = None;
    if not auApplicationProcessIds:
      print "You must specify an application command-line, keyword or process ids";
      return 2;
  else:
    # First argument may be an application keyword
    sApplicationKeyword = None;
    sApplicationBinary = None;
    if "=" in asArguments[0]:
      # user provided an application keyword and binary
      sApplicationKeyword, sApplicationBinary = asArguments.pop(0).split("=", 1);
    elif asArguments[0] in asApplicationKeywords or asArguments[0][-1] == "?":
      # user provided an application keyword, or requested information on something that may be one:
      sApplicationKeyword = asArguments.pop(0);
    asApplicationCommandLine = None;
    if sApplicationKeyword:
      if sApplicationKeyword[-1] == "?":
        # User requested information about a possible keyword application
        return fuShowApplicationKeyWordHelp(sApplicationKeyword[:-1]);
      # Get application command line for keyword, if available:
      if sApplicationKeyword in gdApplication_asCommandLine_by_sKeyword:
        if auApplicationProcessIds:
          print "You cannot specify process ids for application %s" % sApplicationKeyword;
          return 2;
        asApplicationCommandLine = gdApplication_asCommandLine_by_sKeyword[sApplicationKeyword];
        if sApplicationBinary:
          # Replace binary with user provided value
          asApplicationCommandLine = [sApplicationBinary] + asApplicationCommandLine[1:];
        else:
          if asApplicationCommandLine[0] is None:
            print "Application %s does not appear to be installed";
            return 2;
        if asArguments:
          # Add user provided additional application arguments:
          asApplicationCommandLine += asArguments;
        elif sApplicationKeyword in gdApplication_asDefaultAdditionalArguments_by_sKeyword:
          # Add default additional application arguments:
          asApplicationCommandLine += [
            sArgument is DEFAULT_BROWSER_TEST_URL and dxConfig["sDefaultBrowserTestURL"] or sArgument
            for sArgument in gdApplication_asDefaultAdditionalArguments_by_sKeyword[sApplicationKeyword]
          ];
      
      elif asArguments:
        print "You cannot specify arguments for application keyword %s" % sApplicationKeyword;
        return 2;
      elif not auApplicationProcessIds:
        print "You must specify process ids for application keyword %s" % sApplicationKeyword;
        return 2;
      # Apply application specific settings
      if sApplicationKeyword in gdApplication_dxSettings_by_sKeyword:
        print "* Applying application specific settings:";
        for (sSettingName, xValue) in gdApplication_dxSettings_by_sKeyword[sApplicationKeyword].items():
          if sSettingName not in dxUserProvidedConfigSettings:
            fApplyConfigSetting(sSettingName, xValue, "  "); # Apply and show result indented.
      # Apply application specific source settings
      if sApplicationKeyword in gdApplication_sURLTemplate_by_srSourceFilePath_by_sKeyword:
        dsURLTemplate_by_srSourceFilePath = gdApplication_sURLTemplate_by_srSourceFilePath_by_sKeyword[sApplicationKeyword];
      # Apply application specific stdio settings:
      if sApplicationKeyword in gdApplication_rImportantStdOutLines_by_sKeyword:
        rImportantStdOutLines = gdApplication_rImportantStdOutLines_by_sKeyword[sApplicationKeyword];
      if sApplicationKeyword in gdApplication_rImportantStdErrLines_by_sKeyword:
        rImportantStdErrLines = gdApplication_rImportantStdErrLines_by_sKeyword[sApplicationKeyword];
      if not sApplicationISA and sApplicationKeyword in gdApplication_sISA_by_sKeyword:
        # Apply application specific ISA
        sApplicationISA = gdApplication_sISA_by_sKeyword[sApplicationKeyword];
    elif auApplicationProcessIds:
      # user provided an application command-line and process ids
      print "You cannot specify both an application command-line and process ids";
      return 2;
    else:
      # user provided an application command-line
      asApplicationCommandLine = asArguments;
  
  # Apply user provided settings:
  for (sSettingName, xValue) in dxUserProvidedConfigSettings.items():
    fApplyConfigSetting(sSettingName, xValue); # Apply and show result
  
  if bForever:
    duNumberOfRepros_by_sBugIdAndLocation = {};
    sValidStatisticsFileName = FileSystem.fsValidName("Reproduction statistics.txt");
  uRunCounter = 0;
  while 1: # Will only loop if bForever is True
    nStartTime = time.clock();
    uRunCounter += 1;
    if asApplicationCommandLine:
      print "+ The debugger is starting the application...";
      print "  Command line: %s" % " ".join(asApplicationCommandLine);
    else:
      print "+ The debugger is attaching to the application...";
    oBugId = cBugId(
      sCdbISA = sApplicationISA or cBugId.sOSISA,
      asApplicationCommandLine = asApplicationCommandLine or None,
      auApplicationProcessIds = auApplicationProcessIds or None,
      asLocalSymbolPaths = dxConfig["asLocalSymbolPaths"],
      asSymbolCachePaths = dxConfig["asSymbolCachePaths"], 
      asSymbolServerURLs = dxConfig["asSymbolServerURLs"],
      dsURLTemplate_by_srSourceFilePath = dsURLTemplate_by_srSourceFilePath,
      rImportantStdOutLines = rImportantStdOutLines,
      rImportantStdErrLines = rImportantStdErrLines,
      bGenerateReportHTML = dxConfig["bGenerateReportHTML"],
      fApplicationRunningCallback = fApplicationRunningHandler,
      fApplicationSuspendedCallback = fApplicationSuspendedHandler,
      fApplicationResumedCallback = fApplicationResumedHandler,
      fMainProcessTerminatedCallback = fMainProcessTerminatedHandler,
    );
    if dxConfig["nApplicationMaxRunTime"] is not None:
      oBugId.fxSetTimeout(dxConfig["nApplicationMaxRunTime"], fApplicationRunTimeoutHandler, oBugId);
    if dxConfig["nExcessiveCPUUsageCheckInitialTimeout"]:
      oBugId.fSetCheckForExcessiveCPUUsageTimeout(dxConfig["nExcessiveCPUUsageCheckInitialTimeout"]);
    oBugId.fStart();
    oBugId.fWait();
    if oBugId.oInternalException:
      print "-" * 80;
      print "- An error has occured in cBugId, which cannot be handled:";
      print "  %s" % repr(oBugId.oInternalException);
      print "  BugId version %s, cBugId version %s" % (sVersion, cBugId.sVersion);
      print "-" * 80;
      print;
      print "  Please report this issue at the below web-page so it can be addressed:";
      print "      https://github.com/SkyLined/BugId/issues/new";
      print "  If you do not have a github account, or you want to report this issue";
      print "  privately, you can also send an email to:";
      print "      BugId@skylined.nl";
      print;
      print "  In your report, please copy all the information about the error reported";
      print "  above, as well as the version information. This makes it easier to determine";
      print "  the cause of this issue. I will try to address the issues as soon as";
      print "  possible. Thank you in advance for helping to improve BugId!";
      return 3;
    if oBugId.sFailedToDebugApplicationErrorMessage is not None:
      print "-" * 80;
      print "- Failed to debug the application:"
      for sLine in oBugId.sFailedToDebugApplicationErrorMessage.split("\n"):
        print "  %s" % sLine.rstrip("\r");
      print "-" * 80;
      return 4;
    if oBugId.oBugReport is not None:
      print;
      print "  === BugId report (https://github.com/SkyLined/BugId) ".ljust(80, "=");
      print "  Id:               %s" % oBugId.oBugReport.sId;
      print "  Location:         %s" % oBugId.oBugReport.sBugLocation;
      print "  Description:      %s" % oBugId.oBugReport.sBugDescription;
      print "  Version:          %s" % oBugId.oBugReport.asVersionInformation[0]; # There is always the process' binary.
      for sVersionInformation in oBugId.oBugReport.asVersionInformation[1:]: # There may be two if the crash was in a
        print "                    %s" % sVersionInformation;                # different binary (e.g. a .dll)
      if oBugId.oBugReport.sBugSourceLocation:
        print "  Source:           %s" % oBugId.oBugReport.sBugSourceLocation;
      print "  Security impact:  %s" % oBugId.oBugReport.sSecurityImpact;
      print "  Application time: %s seconds" % (long(oBugId.fnApplicationRunTime() * 1000) / 1000.0);
      nOverheadTime = time.clock() - nStartTime - oBugId.fnApplicationRunTime();
      print "  BugId overhead:   %s seconds" % (long(nOverheadTime * 1000) / 1000.0);
      sBugIdAndLocation = "%s @ %s" % (oBugId.oBugReport.sId, oBugId.oBugReport.sBugLocation);
      if dxConfig["bGenerateReportHTML"]:
        # We'd like a report file name base on the BugId, but the later may contain characters that are not valid in a file name
        sDesiredReportFileName = "%s.html" % sBugIdAndLocation;
        # Thus, we need to translate these characters to create a valid filename that looks very similar to the BugId
        sValidReportFileName = FileSystem.fsValidName(sDesiredReportFileName, bUnicode = dxConfig["bUseUnicodeReportFileNames"]);
        if dxConfig["sReportFolderPath"] is not None:
          sReportFilePath = FileSystem.fsPath(dxConfig["sReportFolderPath"], sValidReportFileName);
        else:
          sReportFilePath = FileSystem.fsPath(sValidReportFileName);
        eWriteDataToFileResult = FileSystem.feWriteDataToFile(
          oBugId.oBugReport.sReportHTML,
          sReportFilePath,
          fbRetryOnFailure = lambda: False,
        );
        if eWriteDataToFileResult:
          print "  Bug report:       Cannot be saved (%s)" % repr(eWriteDataToFileResult);
        else:
          print "  Bug report:       %s (%d bytes)" % (sValidReportFileName, len(oBugId.oBugReport.sReportHTML));
      if not bForever: return 1;
    else:
      print;
      print "  === BugId report (https://github.com/SkyLined/BugId) ".ljust(80, "=");
      print "  Id:               None";
      print "  Description:      The application terminated before a bug was detected.";
      print "  Application time: %s seconds" % (long(oBugId.fnApplicationRunTime() * 1000) / 1000.0);
      nOverheadTime = time.clock() - nStartTime - oBugId.fnApplicationRunTime();
      print "  BugId overhead:   %s seconds" % (long(nOverheadTime * 1000) / 1000.0);
      if not bForever: return 0;
      sBugIdAndLocation = "No crash";
    duNumberOfRepros_by_sBugIdAndLocation.setdefault(sBugIdAndLocation, 0)
    duNumberOfRepros_by_sBugIdAndLocation[sBugIdAndLocation] += 1;
    sStatistics = "";
    auOrderedNumberOfRepros = sorted(list(set(duNumberOfRepros_by_sBugIdAndLocation.values())));
    auOrderedNumberOfRepros.reverse();
    for uNumberOfRepros in auOrderedNumberOfRepros:
      for sBugIdAndLocation in duNumberOfRepros_by_sBugIdAndLocation.keys():
        if duNumberOfRepros_by_sBugIdAndLocation[sBugIdAndLocation] == uNumberOfRepros:
          sStatistics += "%d x %s (%d%%)\r\n" % (uNumberOfRepros, sBugIdAndLocation, round(100.0 * uNumberOfRepros / uRunCounter));
    if dxConfig["sReportFolderPath"] is not None:
      sStatisticsFilePath = FileSystem.fsPath(dxConfig["sReportFolderPath"], sValidStatisticsFileName);
    else:
      sStatisticsFilePath = FileSystem.fsPath(sValidStatisticsFileName);
    eWriteDataToFileResult = FileSystem.feWriteDataToFile(
      sStatistics,
      sStatisticsFilePath,
      fbRetryOnFailure = lambda: False,
    );
    if eWriteDataToFileResult:
      print "  Statistics:       Cannot be saved (%s)" % repr(eWriteDataToFileResult);
    else:
      print "  Statistics:       %s (%d bytes)" % (sStatisticsFilePath, len(sStatistics));
    print; # and loop

if __name__ == "__main__":
  try:
    if len(sys.argv) == 1:
      fPrintUsage(asApplicationKeywords);
      uExitCode = 0;
    else:
      uExitCode = fuMain(sys.argv[1:]);
    
    if dxConfig["bShowLicenseAndDonationInfo"]:
      print;
      print "BugId version %s, cBugId version %s" % (sVersion, cBugId.sVersion);
      print "This version of BugId is provided free of charge for non-commercial use only.";
      print "If you find it useful and would like to make a donation, you can send bitcoin";
      print "to 183yyxa9s1s1f7JBpPHPmzQ346y91Rx5DX. Please contact the author if you wish to";
      print "use BugId commercially. Contact and licensing information can be found at";
      print "https://github.com/SkyLined/BugId#license.";
  except Exception as oException:
    print "+ An error has occured in BugId, which cannot be handled:";
    print "  %s" % repr(oException);
    print;
    print "  BugId version %s, cBugId version %s" % (sVersion, cBugId.sVersion);
    print;
    print "  Please report this issue at the below web-page so it can be addressed:";
    print "      https://github.com/SkyLined/BugId/issues/new";
    print "  If you do not have a github account, or you want to report this issue";
    print "  privately, you can also send an email to:";
    print "      BugId@skylined.nl";
    print;
    print "  In your report, please copy all the information about the error reported";
    print "  above, as well as the version information. This makes it easier to determine";
    print "  the cause of this issue. I will try to address the issues as soon as";
    print "  possible. Thank you in advance for helping to improve BugId!";
    uExitCode = 3;
  finally:
    os._exit(uExitCode);