import codecs, json, re, os, sys, threading, time, traceback;

"""
                          __                     _____________                  
            ,,,     _,siSS**SSis,_        ,-.   /             |                 
           :O()   ,SP*'`      `'*YS,     |   `-|  O    BugId  |                 
            ```  dS'  _    |    _ 'Sb   ,'      \_____________|                 
      ,,,       dP     \,-` `-<`    Yb _&/                                      
     :O()      ,S`  \,' \      \    `Sis|ssssssssssssssssss,        ,,,         
      ```      (S   (   | --====)    SSS|SSSSSSSSSSSSSSSSSSD        ()O:        
               'S,  /', /      /    ,S?*/******************'        ```         
                Yb    _/'-_ _-<._   dP `                                        
  _______________YS,       |      ,SP_________________________________________  
                  `Sbs,_      _,sdS`                                            
                    `'*YSSssSSY*'`                   https://bugid.skylined.nl  
                          ``                                                    
                                                                                
""";

# Augment the search path: look in main folder, parent folder or "modules" child folder, in that order.
sMainFolderPath = os.path.dirname(__file__);
asAbsoluteLoweredSysPaths = [os.path.abspath(sPath.lower()) for sPath in sys.path];
asAbsoluteSearchPaths = [os.path.abspath(os.path.join(sMainFolderPath, *asPath).lower()) for asPath in [[], [".."], ["modules"]]];
sys.path = [sPath for sPath in asAbsoluteSearchPaths if sPath.lower() not in asAbsoluteLoweredSysPaths] + sys.path;

from fPrintLogo import fPrintLogo;
from fPrintUsage import fPrintUsage;
from oConsole import oConsole;
from oVersionInformation import oVersionInformation;

# Colors used in output for various types of information:
NORMAL = -1;  # Console default color
INFO = 10;    # Light green
HILITE = 15;  # White
ERROR = 12;   # Light red

# Load external dependecies to make sure they are available and shown an error
# if any one fails to load. This error explains where the missing component
# can be downloaded to fix the error.
for (sModuleName, sDownloadURL) in [
  ("FileSystem", "https://github.com/SkyLined/FileSystem/"),
  ("Kill", "https://github.com/SkyLined/Kill/"),
  ("cBugId", "https://github.com/SkyLined/cBugId/"),
]:
  try:
    __import__(sModuleName, globals(), locals(), [], -1);
  except ImportError, oError:
    if oError.message == "No module named %s" % sModuleName:
      oConsole.fPrint(ERROR, "*" * 80);
      oConsole.fPrint(ERROR, "BugId depends on ", HILITE, sModuleName, ERROR, " which you can download at:");
      oConsole.fPrint(ERROR, "    ", sDownloadURL);
      oConsole.fPrint(ERROR, "After downloading, please save the code in the folder \"", sModuleName, "\",");
      oConsole.fPrint(ERROR, "\"modules\\", sModuleName, "\" or any other location where it can be imported.");
      oConsole.fPrint(ERROR, "Once you have completed these steps, please try again.");
      oConsole.fPrint(ERROR, "*" * 80);
    raise;

from cBugId import cBugId;
import FileSystem, Kill;
from dxConfig import dxConfig;

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
asChromeDefaultArguments = [
  "--enable-experimental-accessibility-features",
  "--enable-experimental-canvas-features",
  "--enable-experimental-input-view-features",
  "--enable-experimental-web-platform-features",
  "--enable-usermedia-screen-capturing",
  "--enable-viewport",
  "--enable-webgl-draft-extensions",
  "--enable-webvr",
  "--expose-internals-for-testing",
  "--disable-popup-blocking",
  "--disable-prompt-on-repost",
  "--force-renderer-accessibility",
  "--javascript-harmony",
  "--no-sandbox",
];
asFirefoxDefaultArguments = [
  "--no-remote",
  "-profile", "%s\Firefox-profile" % os.getenv("TEMP"),
];
gdApplication_sBinaryPath_by_sKeyword = {
  "aoo-writer": r"%s\OpenOffice 4\program\swriter.exe" % sProgramFilesPath_x86,
  "acrobat": r"%s\Adobe\Reader 11.0\Reader\AcroRd32.exe" % sProgramFilesPath_x86,
  "acrobatdc": r"%s\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe" % sProgramFilesPath_x86,
  "chrome": sChromePath,
  "chrome_x86": sChromePath_x86,
  "chrome_x64": sChromePath_x64,
  "chrome-sxs": sChromeSxSPath,
  "chrome-sxs_x86": sChromeSxSPath_x86,
  "chrome-sxs_x64": sChromeSxSPath_x64,
  "firefox": sFirefoxPath,
  "firefox_x86": sFirefoxPath_x86,
  "firefox_x64": sFirefoxPath_x64,
  "firefox-dev": sFirefoxDevPath,
  "firefox-dev_x86": sFirefoxDevPath_x86,
  "firefox-dev_x64": sFirefoxDevPath_x64,
  "foxit": r"%s\Foxit Software\Foxit Reader\FoxitReader.exe" % sProgramFilesPath_x86,
  "msie": sMSIEPath,
  "msie_x86": sMSIEPath_x86,
  "msie_x64": sMSIEPath_x64,
};
gsApplicationPackageName_by_sKeyword = {
  "edge": "Microsoft.MicrosoftEdge",
};
gsApplicationId_by_sKeyword = {
  "edge": "MicrosoftEdge",
};
gasApplicationAttachToProcessesForBinaryNames_by_sKeyword = {
  "edge": ["browser_broker.exe", "RuntimeBroker.exe"],
};
# These arguments are always added
gdApplication_asStaticArguments_by_sKeyword = {
  "aoo-writer": ["-norestore", "-view", "-nologo", "-nolockcheck"],
  "chrome": asChromeDefaultArguments,
  "chrome_x86": asChromeDefaultArguments,
  "chrome_x64": asChromeDefaultArguments,
  "chrome-sxs": asChromeDefaultArguments,
  "chrome-sxs_x86": asChromeDefaultArguments,
  "chrome-sxs_x64": asChromeDefaultArguments,
  "firefox": asFirefoxDefaultArguments,
  "firefox_x86": asFirefoxDefaultArguments,
  "firefox_x64": asFirefoxDefaultArguments,
  "firefox-dev": asFirefoxDefaultArguments,
  "firefox-dev_x86": asFirefoxDefaultArguments,
  "firefox-dev_x64": asFirefoxDefaultArguments,
};
# These arguments are added if the 
DEFAULT_BROWSER_TEST_URL = {}; # Placeholder for dxConfig["sDefaultBrowserTestURL"]
gdApplication_asDefaultOptionalArguments_by_sKeyword = {
  "acrobat": ["repro.pdf"],
  "acrobatdc": ["repro.pdf"],
  "chrome": [DEFAULT_BROWSER_TEST_URL],
  "chrome_x86": [DEFAULT_BROWSER_TEST_URL],
  "chrome_x64": [DEFAULT_BROWSER_TEST_URL],
  "firefox": [DEFAULT_BROWSER_TEST_URL],
  "firefox_x86": [DEFAULT_BROWSER_TEST_URL],
  "firefox_x64": [DEFAULT_BROWSER_TEST_URL],
  "firefox-dev": [DEFAULT_BROWSER_TEST_URL],
  "firefox-dev_x86": [DEFAULT_BROWSER_TEST_URL],
  "firefox-dev_x64": [DEFAULT_BROWSER_TEST_URL],
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
    "bApplicationTerminatesWithMainProcess": True,
    "nApplicationMaxRunTime": 60.0, # Really slow.
    "nExcessiveCPUUsageCheckInitialTimeout": 30.0, # Give application some time to load repro
    "cBugId.nExcessiveCPUUsageCheckInterval": 5.0, # Application should not be busy for more than 5 seconds.
    "cBugId.nExcessiveCPUUsagePercent": 75,      # Application must be relatively busy.
    "cBugId.nExcessiveCPUUsageWormRunTime": 0.5, # Any well written function should return within half a second IMHO.
  },
  "acrobatdc": {
    "bApplicationTerminatesWithMainProcess": True,
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
  "edgedbg": dxBrowserSettings,
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
  "firefox": {srMozillaCentralSourceURLMappings: "https://dxr.mozilla.org/mozilla-central/source/%(path)s#%(lineno)s"},
  "firefox_x86": {srMozillaCentralSourceURLMappings: "https://dxr.mozilla.org/mozilla-central/source/%(path)s#%(lineno)s"},
  "firefox_x64": {srMozillaCentralSourceURLMappings: "https://dxr.mozilla.org/mozilla-central/source/%(path)s#%(lineno)s"},
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
gbAnErrorOccured = False;

gasBinariesThatAreAllowedToRunWithoutPageHeap = [
  # Chrome provides ASan builds, so page heap is redundant. You can and should still run it with page heap though.
  "chrome.exe",
  # Firefox uses jemalloc, so page heap is not very useful. You can and should still run it with page heap though.
  "firefox.exe",
  # Adobe Reader has a component that crashes immediately with a NULL pointer exception when you enable page heap.
  "RdrCEF.exe",
];
asApplicationKeywords = sorted(list(set(
  gdApplication_sBinaryPath_by_sKeyword.keys() +
  gsApplicationPackageName_by_sKeyword.keys() +
  gsApplicationId_by_sKeyword.keys() + # should be the same as above!
  gasApplicationAttachToProcessesForBinaryNames_by_sKeyword.keys() +
  gdApplication_asStaticArguments_by_sKeyword.keys() +
  gdApplication_asDefaultOptionalArguments_by_sKeyword.keys() +
  gdApplication_dxSettings_by_sKeyword.keys() +
  gdApplication_sURLTemplate_by_srSourceFilePath_by_sKeyword.keys() + 
  gdApplication_rImportantStdOutLines_by_sKeyword.keys() +
  gdApplication_rImportantStdErrLines_by_sKeyword.keys()
)));
gbQuiet = False;

def fuShowApplicationKeyWordHelp(sApplicationKeyword):
  if sApplicationKeyword not in asApplicationKeywords:
    oConsole.fPrint(ERROR,"- Unknown application keyword %s" % sApplicationKeyword);
    return 2;
  oConsole.fPrint("Known application settings for %s" % sApplicationKeyword);
  if sApplicationKeyword in gdApplication_sBinaryPath_by_sKeyword:
    if gdApplication_sBinaryPath_by_sKeyword[sApplicationKeyword] is None:
      oConsole.fPrint(ERROR,"  The application cannot be found on your system.");
    else:
      oConsole.fPrint("  Binary path: ", INFO, " ".join(gdApplication_sBinaryPath_by_sKeyword[sApplicationKeyword]));
  elif sApplicationKeyword in gsApplicationPackageName_by_sKeyword:
    oConsole.fPrint("  UWP Application information:");
    oConsole.fPrint("    Package name: ", INFO, gsApplicationPackageName_by_sKeyword[sApplicationKeyword]);
    oConsole.fPrint("    Id: ", INFO, gsApplicationId_by_sKeyword[sApplicationKeyword]);
    if sApplicationKeyword in gasApplicationAttachToProcessesForBinaryNames_by_sKeyword:
      oConsole.fPrint("    Attach to additional processes running any of the following binaries:");
      for sBinaryName in gasApplicationAttachToProcessesForBinaryNames_by_sKeyword[sApplicationKeyword]:
        oConsole.fPrint("      ", INFO, sBinaryName);
  if sApplicationKeyword in gdApplication_asStaticArguments_by_sKeyword:
    oConsole.fPrint("  Default static arguments: ", INFO, " ".join(
      gdApplication_asStaticArguments_by_sKeyword[sApplicationKeyword])
    );
  if sApplicationKeyword in gdApplication_asDefaultOptionalArguments_by_sKeyword:
    oConsole.fPrint("  Default optional arguments: ", INFO, " ".join([
      sArgument is DEFAULT_BROWSER_TEST_URL and dxConfig["sDefaultBrowserTestURL"] or sArgument
      for sArgument in gdApplication_asDefaultOptionalArguments_by_sKeyword[sApplicationKeyword]
    ]));
  if sApplicationKeyword in gdApplication_dxSettings_by_sKeyword:
    oConsole.fPrint("  Application specific settings:");
    for sSettingName, xValue in gdApplication_dxSettings_by_sKeyword[sApplicationKeyword].items():
      oConsole.fPrint("    ", HILITE, sSettingName, NORMAL, " = ", INFO, json.dumps(xValue));
  return 0;

def fApplyConfigSetting(sSettingName, xValue, sIndentation):
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
    if not gbQuiet:
      oConsole.fPrint(sIndentation, "* The default value for config setting ", HILITE, sFullName, NORMAL, \
          " is ", json.dumps(dxConfigGroup[sSettingName]), ".");
  else:
    if not gbQuiet:
      oConsole.fPrint(sIndentation, "+ Changed config setting ", HILITE, sFullName, NORMAL, \
          " from ", HILITE, repr(dxConfigGroup[sSettingName]), NORMAL, " to ", INFO, repr(xValue), NORMAL, ".");
    dxConfigGroup[sSettingName] = xValue;

def fApplicationRunningHandler(oBugId):
  oConsole.fStatus("* The application was started successfully and is running...");

def fApplicationSuspendedHandler(oBugId, sReason):
  oConsole.fStatus("* T+%.1f The application is suspended (%s)..." % (oBugId.fnApplicationRunTime(), sReason));

def fApplicationResumedHandler(oBugId):
  oConsole.fStatus("* The application is running...");

def fApplicationRunTimeoutHandler(oBugId):
  oConsole.fPrint("+ T+%.1f The application has been running for %.1f seconds without crashing." % \
      (oBugId.fnApplicationRunTime(), dxConfig["nApplicationMaxRunTime"]));
  oConsole.fPrint();
  oConsole.fStatus(INFO, "* BugId is stopping...");
  oBugId.fStop();

def fInternalExceptionHandler(oBugId, oException, oTraceBack):
  global gbAnErrorOccured;
  gbAnErrorOccured = True;
  fDumpException(oException, oTraceBack);

def fFailedToDebugApplicationHandler(oBugId, sErrorMessage):
  global gbAnErrorOccured;
  gbAnErrorOccured = True;
  oConsole.fPrint(ERROR, "-" * 80);
  oConsole.fPrint(ERROR, "- Failed to debug the application:");
  for sLine in sErrorMessage.split("\n"):
    oConsole.fPrint(ERROR, "  ", sLine.rstrip("\r"));
  oConsole.fPrint(ERROR, "-" * 80);
  oConsole.fPrint();

gasReportedBinaryNameWithoutPageHeap = [];
gasAttachToProcessesForBinaryNames = [];
def fPageHeapNotEnabledHandler(oBugId, uProcessId, sBinaryName, bPreventable):
  global gbAnErrorOccured, \
         gasBinariesThatAreAllowedToRunWithoutPageHeap, \
         gasReportedBinaryNameWithoutPageHeap, \
         gasAttachToProcessesForBinaryNames;
  if sBinaryName in gasBinariesThatAreAllowedToRunWithoutPageHeap:
    return;
  if not bPreventable:
    if not gbQuiet and sBinaryName not in gasReportedBinaryNameWithoutPageHeap:
      gasReportedBinaryNameWithoutPageHeap.append(sBinaryName);
      oConsole.fPrint(ERROR,"- Full page heap is not enabled for ",15,sBinaryName,13,".");
      oConsole.fPrint("  This appears to be due to a bug in page heap that prevents it from");
      oConsole.fPrint("  determining the binary name correctly. Unfortunately, there is no known fix");
      oConsole.fPrint("  or work-around for this. BugId will continue, but detection and analysis of");
      oConsole.fPrint("  any bugs in this process will be sub-optimal.");
      oConsole.fPrint();
  else:
    gbAnErrorOccured = True;
    oConsole.fPrint(ERROR, "- Full page heap is not enabled for all binaries used by the application.");
    oConsole.fPrint(ERROR, "  Specifically it is not enabled for ",15,sBinaryName,7,".");
    oConsole.fPrint("  You can enabled full page heap for %s by running:" % sBinaryName);
    oConsole.fPrint();
    oConsole.fPrint("      ",15,'PageHeap.cmd "',sBinaryName,'" ON');
    oConsole.fPrint();
    oConsole.fPrint("  Without page heap enabled, detection and anaylsis of any bugs will be sub-");
    oConsole.fPrint("  optimal. Please enable page heap and try again.");
    oConsole.fPrint();
    oConsole.fStatus(INFO, "* BugId is stopping...");
    # There is no reason to run without page heap, so terminated.
    oBugId.fStop();
    # If you really want to run without page heap, set `dxConfig["cBugId"]["bEnsurePageHeap"]` to `False` in `dxConfig.py`
    # or run with the command-line siwtch `--cBugId.bEnsurePageHeap=false`

def fMainProcessTerminatedHandler(oBugId, uProcessId, sBinaryName):
  if dxConfig["bApplicationTerminatesWithMainProcess"]:
    oConsole.fPrint("+ T+%.1f One of the main processes (id %d/0x%X, %s) has terminated." % \
        (oBugId.fnApplicationRunTime(), uProcessId, uProcessId, sBinaryName));
    oConsole.fPrint();
    oConsole.fStatus(INFO, "* BugId is stopping...");
    oBugId.fStop();
  elif not gbQuiet:
    oConsole.fPrint("+ T+%.1f One of the main processes (id %d/0x%X, %s) has terminated." % \
        (oBugId.fnApplicationRunTime(), uProcessId, uProcessId, sBinaryName));
    oConsole.fPrint();

def fStdErrOutputHandler(oBugId, sOutput):
  oConsole.fPrint(ERROR,"stderr>", NORMAL, sOutput);

def fNewProcessHandler(oBugId, oProcess):
  global gasAttachToProcessesForBinaryNames;
  if not gbQuiet:
    oConsole.fPrint("* New process ", INFO, "%d" % oProcess.uId, NORMAL, "/", INFO , "0x%X" % oProcess.uId, NORMAL, ": ", INFO, oProcess.sBinaryName);
  # Now is a good time to look for additional binaries that may need to be debugged as well.
  if gasAttachToProcessesForBinaryNames:
    oBugId.fAttachToProcessesForBinaryNames(gasAttachToProcessesForBinaryNames);

def fDumpException(oException, oTraceBack):
  oConsole.fPrint(ERROR, "-" * 80);
  oConsole.fPrint(ERROR, "- An internal exception has occured:");
  oConsole.fPrint(ERROR, "  %s" % repr(oException));
  oConsole.fPrint(ERROR,"  Stack:");
  txStack = traceback.extract_tb(oTraceBack);
  uFrameIndex = len(txStack) - 1;
  for (sFileName, uLineNumber, sFunctionName, sCode) in reversed(txStack):
    sSource = "%s/%d" % (sFileName, uLineNumber);
    if sFunctionName != "<module>":
      sSource = "%s (%s)" % (sFunctionName, sSource);
    oConsole.fPrint(ERROR,"  %3d %s" % (uFrameIndex, sSource));
    if sCode:
      oConsole.fPrint(ERROR,"      > %s" % sCode.strip());
    uFrameIndex -= 1;
  oConsole.fPrint(ERROR,"  BugId version %s" % oVersionInformation.sCurrentVersion);
  for (sModule, xModule) in [
    ("cBugId", cBugId),
    ("FileSystem", FileSystem),
    ("Kill", Kill),
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
  oConsole.fPrint("Thank you in advance for helping to improve BugId!");
  oConsole.fPrint();
  os._exit(0);

def fuVersionCheck():
  for (sModuleName, oModule, oModuleVersionInformation, fsVersionCheck) in [
    ("BugId",       sys.modules["__main__"],        oVersionInformation,                              None),
    ("cBugId",      sys.modules[cBugId.__module__], getattr(cBugId, "oVersionInformation", None),     getattr(cBugId, "fsVersionCheck", None)),
    ("FileSystem",  FileSystem,                     getattr(FileSystem, "oVersionInformation", None), getattr(FileSystem, "fsVersionCheck", None)),
    ("Kill",        Kill,                           getattr(Kill, "oVersionInformation", None),       getattr(Kill, "fsVersionCheck", None)),
  ]:    
    if oModuleVersionInformation:
      assert sModuleName == oModuleVersionInformation.sProjectName, \
          "Module %s reports that it is called %s" % (sModuleName, oModuleVersionInformation.sProjectName);
      oConsole.fPrint("+ ", oModuleVersionInformation.sProjectName, " version ", oModuleVersionInformation.sCurrentVersion, ".");
      oConsole.fStatus("* Checking ", INFO, oModuleVersionInformation.sProjectName, NORMAL, " for updates...");
      if oModuleVersionInformation.bPreRelease:
        oConsole.fPrint("  + You are running a ", HILITE, "pre-release", NORMAL, " version. ",
            "The latest release version is ", INFO, oModuleVersionInformation.sLatestVersion, NORMAL, ".");
      elif not oModuleVersionInformation.bUpToDate:
        oConsole.fPrint("  + Version ", INFO, oModuleVersionInformation.sLatestVersion, NORMAL,
            " is available at ", INFO, oModuleVersionInformation.sUpdateURL, NORMAL, ".");
    elif fsVersionCheck:
      oConsole.fPrint("* ", INFO, sModuleName, NORMAL, " version check reports: ", INFO, fsVersionCheck(), ".");
    else:
      oConsole.fPrint("- You are running an ", ERROR, "outdated", NORMAL, " version of ", INFO, sModuleName, NORMAL, ".");
    oConsole.fPrint("  + Installation path: %s" % os.path.dirname(oModule.__file__));
  oConsole.fPrint();
  return 0;

def fuMain(asArguments):
  global gbQuiet, \
         gasAttachToProcessesForBinaryNames;
  if len(asArguments) == 0:
    fPrintLogo();
    fPrintUsage(asApplicationKeywords);
    return 0;
  # returns an exit code, values are:
  # 0 = executed successfully, no bugs found.
  # 1 = executed successfully, bug detected.
  # 2 = bad arguments
  # 3 = internal error
  # 4 = failed to start process or attach to process(es).
  # Parse all "--" arguments until we encounter a non-"--" argument.
  sApplicationKeyword = None;
  sApplicationBinaryPath = None;
  auApplicationProcessIds = [];
  sApplicationPackageName = None;
  sApplicationId = None;
  asApplicationOptionalArguments = None;
  sApplicationISA = None;
  bRepeat = False;
  bCheckForUpdates = False;
  dxUserProvidedConfigSettings = {};
  bFast = False;
  while asArguments:
    sArgument = asArguments.pop(0);
    if sArgument == "--":
      if len(auApplicationProcessIds) > 0:
      # The rest of the arguments are to be passed to the application
        oConsole.fPrint(ERROR, "- You cannot supply process ids and application arguments.");
        return 2;
      asApplicationOptionalArguments = asArguments;
      break;
    elif sArgument in ["-q", "/q"]:
      gbQuiet = True;
    elif sArgument in ["-f", "/f"]:
      bFast = True;
    elif sArgument in ["-r", "/r"]:
      bRepeat = True;
    elif sArgument in ["-?", "/?", "-h", "/h"]:
      fPrintLogo();
      fPrintUsage(asApplicationKeywords);
      return 0;
    elif sArgument.startswith("--"):
      if "=" in sArgument:
        sSettingName, sValue = sArgument[2:].split("=", 1);
      else:
        # "--bFlag" is an alias for "--bFlag=true"
        sSettingName = sArgument[2:];
        sValue = "true";
      
      if sSettingName in ["pid", "pids"]:
        if sApplicationBinaryPath is not None:
          oConsole.fPrint(ERROR, "- You cannot supply an application binary and process ids.");
          return 2;
        if sApplicationPackageName is not None:
          oConsole.fPrint(ERROR, "- You cannot supply an application package name and process ids.");
          return 2;
        auApplicationProcessIds += [long(x) for x in sValue.split(",")];
      elif sSettingName in ["uwp", "uwp-app"]:
        if sApplicationPackageName is not None:
          oConsole.fPrint(ERROR, "- You cannot supply two or more application package names.");
          return 2;
        if sApplicationBinaryPath is not None:
          oConsole.fPrint(ERROR, "- You cannot supply an application binary and package name.");
          return 2;
        if len(auApplicationProcessIds) > 0:
          oConsole.fPrint(ERROR, "- You cannot supply process ids and an application package name.");
          return 2;
        if "!" not in sValue:
          oConsole.fPrint(ERROR, "- Please provide a string of the form %s=<package name>!<application id>.", sSettingName);
          return 2;
        sApplicationPackageName, sApplicationId = sValue.split("!", 1);
      elif sSettingName in ["version", "check-for-updates"]:
        return fuVersionCheck();
      elif sSettingName in ["isa", "cpu"]:
        if sValue not in ["x86", "x64"]:
          oConsole.fPrint(ERROR, "- Unknown ISA %s" % repr(sValue));
          return 2;
        sApplicationISA = sValue;
      elif sSettingName in ["quiet", "silent"]:
        gbQuiet = sValue.lower() == "true";
      elif sSettingName in ["fast", "quick"]:
        bFast = True;
      elif sSettingName in ["repeat", "forever"]:
        bRepeat = True;
      else:
        try:
          xValue = json.loads(sValue);
        except ValueError:
          oConsole.fPrint(ERROR, "- Cannot decode argument JSON value %s." % sValue);
          return 2;
        # User provided config settings must be applied after any keyword specific config settings:
        dxUserProvidedConfigSettings[sSettingName] = xValue;
    elif sArgument in asApplicationKeywords:
      if sApplicationKeyword is not None:
        oConsole.fPrint(ERROR, "- You cannot supply two or more application keywords.");
        return 2;
      sApplicationKeyword = sArgument;
    elif sArgument[-1] == "?" and sArgument[:-1] in asApplicationKeywords:
      return fuShowApplicationKeyWordHelp(sArgument[:-1]);
    else:
      if sApplicationBinaryPath is not None:
        oConsole.fPrint(ERROR, "- You cannot supply two or more application binaries.");
        return 2;
      if len(auApplicationProcessIds) > 0:
        oConsole.fPrint(ERROR, "- You cannot supply process ids and an application binary.");
        return 2;
      if sApplicationPackageName is not None:
        oConsole.fPrint(ERROR, "- You cannot supply an application package name and a binary.");
        return 2;
      sApplicationBinaryPath = sArgument;
  
  if bFast:
    gbQuiet = True;
    dxUserProvidedConfigSettings["bGenerateReportHTML"] = False;
    dxUserProvidedConfigSettings["asSymbolServerURLs"] = [];
    dxUserProvidedConfigSettings["cBugId.bUse_NT_SYMBOL_PATH"] = False;
  
  dsURLTemplate_by_srSourceFilePath = {};
  rImportantStdOutLines = None;
  rImportantStdErrLines = None;
  
  if sApplicationKeyword:
    # Get application binary/package name/process ids as needed:
    if sApplicationKeyword in gdApplication_sBinaryPath_by_sKeyword:
      # This application is started from the command-line.
      if auApplicationProcessIds:
        oConsole.fPrint(ERROR, "- You cannot specify process ids for application keyword ", INFO, sApplicationKeyword, NORMAL, ".");
        return 2;
      if sApplicationPackageName:
        oConsole.fPrint(ERROR, "- You cannot specify an application package name for application keyword ", INFO, sApplicationKeyword, NORMAL, ".");
        return 2;
      if sApplicationBinaryPath is None:
        sApplicationBinaryPath = gdApplication_sBinaryPath_by_sKeyword[sApplicationKeyword];
    elif sApplicationKeyword in gsApplicationPackageName_by_sKeyword:
      # This application is started as an application package.
      if sApplicationBinaryPath:
        oConsole.fPrint(ERROR, "- You cannot specify an application binary for application keyword ", INFO, sApplicationKeyword, NORMAL, ".");
        return 2;
      sApplicationPackageName = gsApplicationPackageName_by_sKeyword[sApplicationKeyword];
      sApplicationId = gsApplicationId_by_sKeyword[sApplicationKeyword];
    elif not auApplicationProcessIds:
      # This application is attached to.
      oConsole.fPrint(ERROR, "- You must specify process ids for application keyword ", INFO, sApplicationKeyword, NORMAL, ".");
      return 2;
    elif asApplicationOptionalArguments:
      # Cannot supply arguments if we're attaching to processes
      oConsole.fPrint(ERROR, "- You cannot specify arguments for application keyword ", INFO, sApplicationKeyword, NORMAL, ".");
      return 2;
    if sApplicationKeyword in gasApplicationAttachToProcessesForBinaryNames_by_sKeyword:
      gasAttachToProcessesForBinaryNames = gasApplicationAttachToProcessesForBinaryNames_by_sKeyword[sApplicationKeyword];
    # Get application arguments;
    asApplicationStaticArguments = gdApplication_asStaticArguments_by_sKeyword.get(sApplicationKeyword, []);
    if asApplicationOptionalArguments is None:
      asApplicationOptionalArguments = [
        sArgument is DEFAULT_BROWSER_TEST_URL and dxConfig["sDefaultBrowserTestURL"] or sArgument
        for sArgument in gdApplication_asDefaultOptionalArguments_by_sKeyword.get(sApplicationKeyword, [])
      ];
    asApplicationArguments = asApplicationStaticArguments + asApplicationOptionalArguments;
    # Apply application specific settings
    if sApplicationKeyword in gdApplication_dxSettings_by_sKeyword:
      if not gbQuiet:
        oConsole.fPrint("* Applying application specific configuration for %s:" % sApplicationKeyword);
      for (sSettingName, xValue) in gdApplication_dxSettings_by_sKeyword[sApplicationKeyword].items():
        if sSettingName not in dxUserProvidedConfigSettings:
          fApplyConfigSetting(sSettingName, xValue, "  "); # Apply and show result indented.
      if not gbQuiet:
        oConsole.fPrint();
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
  else:
    # There are no static arguments if there is no application keyword, only the user-supplied optional arguments
    # are used if they are supplied:
    asApplicationArguments = asApplicationOptionalArguments or [];
  
  # Apply user provided settings:
  for (sSettingName, xValue) in dxUserProvidedConfigSettings.items():
    fApplyConfigSetting(sSettingName, xValue, ""); # Apply and show result
  
  if bRepeat:
    duNumberOfRepros_by_sBugIdAndLocation = {};
    sValidStatisticsFileName = FileSystem.fsValidName("Reproduction statistics.txt");
  uRunCounter = 0;
  while 1: # Will only loop if bRepeat is True
    nStartTime = time.clock();
    uRunCounter += 1;
    if sApplicationBinaryPath:
      if not gbQuiet:
        asCommandLine = [sApplicationBinaryPath] + asApplicationArguments;
        oConsole.fPrint("* Command line: ", INFO, " ".join(asCommandLine));
        oConsole.fPrint();
      oConsole.fStatus("* The debugger is starting the application...");
    else:
      if auApplicationProcessIds:
        asProcessIdsOutput = [];
        for uApplicationProcessId in auApplicationProcessIds:
          if asProcessIdsOutput: asProcessIdsOutput.append(", ");
          asProcessIdsOutput.extend([INFO, str(uApplicationProcessId), NORMAL]);
        oConsole.fPrint("* Running process ids: ", INFO, *asProcessIdsOutput);
      if sApplicationPackageName:
        if not gbQuiet:
          if asApplicationArguments:
            oConsole.fPrint("* Package name: ", INFO, sApplicationPackageName, NORMAL, ", Arguments: ", INFO, " ".join(asApplicationArguments));
          else:
            oConsole.fPrint("* Package name: ", INFO, sApplicationPackageName);
          oConsole.fPrint();
      if not sApplicationPackageName:
        oConsole.fStatus("* The debugger is attaching to running processes of the application...");
      elif auApplicationProcessIds:
        oConsole.fStatus("* The debugger is attaching to running processes and starting the application...");
      else:
        oConsole.fStatus("* The debugger is starting the application...");
    oBugId = cBugId(
      sCdbISA = sApplicationISA or cBugId.sOSISA,
      sApplicationBinaryPath = sApplicationBinaryPath or None,
      auApplicationProcessIds = auApplicationProcessIds or None,
      sApplicationPackageName = sApplicationPackageName or None,
      sApplicationId = sApplicationId or None,
      asApplicationArguments = asApplicationArguments,
      asLocalSymbolPaths = dxConfig["asLocalSymbolPaths"],
      asSymbolCachePaths = dxConfig["asSymbolCachePaths"], 
      asSymbolServerURLs = dxConfig["asSymbolServerURLs"],
      dsURLTemplate_by_srSourceFilePath = dsURLTemplate_by_srSourceFilePath,
      rImportantStdOutLines = rImportantStdOutLines,
      rImportantStdErrLines = rImportantStdErrLines,
      bGenerateReportHTML = dxConfig["bGenerateReportHTML"],
      fFailedToDebugApplicationCallback = fFailedToDebugApplicationHandler,
      fApplicationRunningCallback = fApplicationRunningHandler,
      fApplicationSuspendedCallback = fApplicationSuspendedHandler,
      fApplicationResumedCallback = fApplicationResumedHandler,
      fMainProcessTerminatedCallback = fMainProcessTerminatedHandler,
      fInternalExceptionCallback = fInternalExceptionHandler,
      fFinishedCallback = None,
      fPageHeapNotEnabledCallback = fPageHeapNotEnabledHandler,
      fStdErrOutputCallback = fStdErrOutputHandler,
      fNewProcessCallback = fNewProcessHandler,
    );
    if dxConfig["nApplicationMaxRunTime"] is not None:
      oBugId.fxSetTimeout(dxConfig["nApplicationMaxRunTime"], fApplicationRunTimeoutHandler, oBugId);
    if dxConfig["bExcessiveCPUUsageCheckEnabled"] and dxConfig["nExcessiveCPUUsageCheckInitialTimeout"]:
      oBugId.fSetCheckForExcessiveCPUUsageTimeout(dxConfig["nExcessiveCPUUsageCheckInitialTimeout"]);
    oBugId.fStart();
    oBugId.fWait();
    if gbAnErrorOccured:
      return 3;
    if oBugId.oBugReport is not None:
      oConsole.fPrint(HILITE, "A bug was detect in the application:");
      oConsole.fPrint("  Id @ Location:    ", INFO, oBugId.oBugReport.sId, NORMAL, " @ ", INFO, oBugId.oBugReport.sBugLocation);
      if oBugId.oBugReport.sBugSourceLocation:
        oConsole.fPrint("  Source:           ", INFO, oBugId.oBugReport.sBugSourceLocation);
      oConsole.fPrint("  Description:      ", INFO, oBugId.oBugReport.sBugDescription);
      oConsole.fPrint("  Security impact:  ", INFO, oBugId.oBugReport.sSecurityImpact);
      oConsole.fPrint("  Version:          ", HILITE, oBugId.oBugReport.asVersionInformation[0]); # There is always the process' binary.
      for sVersionInformation in oBugId.oBugReport.asVersionInformation[1:]: # There may be two if the crash was in a
        oConsole.fPrint("                    ", sVersionInformation);                # different binary (e.g. a .dll)
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
          oConsole.fPrint("  Bug report:       ", ERROR, "Cannot be saved (%s)" % repr(eWriteDataToFileResult));
        else:
          oConsole.fPrint("  Bug report:       ", HILITE, sValidReportFileName, NORMAL, " (%d bytes)" % len(oBugId.oBugReport.sReportHTML));
    else:
      oConsole.fPrint(10, "The application terminated without a bug being detected.");
      sBugIdAndLocation = "No crash";
    oConsole.fPrint("  Application time: %s seconds" % (long(oBugId.fnApplicationRunTime() * 1000) / 1000.0));
    nOverheadTime = time.clock() - nStartTime - oBugId.fnApplicationRunTime();
    oConsole.fPrint("  BugId overhead:   %s seconds" % (long(nOverheadTime * 1000) / 1000.0));
    if not bRepeat: return oBugId.oBugReport is not None and 1 or 0;
    duNumberOfRepros_by_sBugIdAndLocation.setdefault(sBugIdAndLocation, 0)
    duNumberOfRepros_by_sBugIdAndLocation[sBugIdAndLocation] += 1;
    sStatistics = "";
    auOrderedNumberOfRepros = sorted(list(set(duNumberOfRepros_by_sBugIdAndLocation.values())));
    auOrderedNumberOfRepros.reverse();
    for uNumberOfRepros in auOrderedNumberOfRepros:
      for sBugIdAndLocation in duNumberOfRepros_by_sBugIdAndLocation.keys():
        if duNumberOfRepros_by_sBugIdAndLocation[sBugIdAndLocation] == uNumberOfRepros:
          sStatistics += "%d \xD7 %s (%d%%)\r\n" % (uNumberOfRepros, sBugIdAndLocation, round(100.0 * uNumberOfRepros / uRunCounter));
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
      oConsole.fPrint("  Statistics:       ", ERROR, "Cannot be saved (%s)" % repr(eWriteDataToFileResult));
    else:
      oConsole.fPrint("  Statistics:       ", INFO, sStatisticsFilePath, NORMAL, " (%d bytes)" % len(sStatistics));
    oConsole.fPrint(); # and loop

if __name__ == "__main__":
  try:
    uExitCode = fuMain(sys.argv[1:]);
    
    if not gbQuiet and dxConfig["bShowLicenseAndDonationInfo"]:
      oConsole.fPrint();
      oConsole.fPrint("This version of BugId is provided free of charge for non-commercial use only.");
      oConsole.fPrint("If you find it useful and would like to make a donation, you can send bitcoin");
      oConsole.fPrint("to ",INFO,"183yyxa9s1s1f7JBpPHPmzQ346y91Rx5DX",NORMAL,".");
      oConsole.fPrint("If you wish to use BugId commercially, please contact the author to request a");
      oConsole.fPrint("quote. Contact and licensing information can be found at:");
      oConsole.fPrint("    ",INFO,"https://github.com/SkyLined/BugId#license",NORMAL,".");
    
    os._exit(uExitCode);
  except Exception as oException:
    cException, oException, oTraceBack = sys.exc_info();
    fDumpException(oException, oTraceBack);
    os._exit(3);