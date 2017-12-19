import codecs, json, re, os, shutil, sys, threading, time, traceback;

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
# Running this script will return an exit code, which translates as such:
# 0 = executed successfully, no bugs found.
# 1 = executed successfully, bug detected.
# 2 = bad arguments
# 3 = internal error
# 4 = failed to start process or attach to process(es).

# Augment the search path: look in main folder, parent folder or "modules" child folder, in that order.
sMainFolderPath = os.path.abspath(os.path.dirname(__file__));
sParentFolderPath = os.path.normpath(os.path.join(sMainFolderPath, ".."));
sModuleFolderPath = os.path.join(sMainFolderPath, "modules");
asAbsoluteLoweredSysPaths = [os.path.abspath(sPath).lower() for sPath in sys.path];
sys.path += [sPath for sPath in [
  sMainFolderPath,
  sParentFolderPath,
  sModuleFolderPath,
] if sPath.lower() not in asAbsoluteLoweredSysPaths];

# Load external dependecies to make sure they are available and shown an error
# if any one fails to load. This error explains where the missing component
# can be downloaded to fix the error.
for (sModuleName, sDownloadURL) in [
  ("mFileSystem", "https://github.com/SkyLined/mFileSystem/"),
  ("mWindowsAPI", "https://github.com/SkyLined/mWindowsAPI/"),
  ("oConsole", "https://github.com/SkyLined/oConsole/"),
  ("cBugId", "https://github.com/SkyLined/cBugId/"),
]:
  try:
    __import__(sModuleName, globals(), locals(), [], -1);
  except ImportError as oError:
    if oError.message == "No module named %s" % sModuleName:
      print "*" * 80;
      print "%s depends on %s which you can download at:" % (os.path.basename(__file__), sModuleName);
      print "    %s" % sDownloadURL;
      print "After downloading, please save the code in this folder:";
      print "    %s" % os.path.join(sModuleFolderPath, sModuleName);
      print " - or -";
      print "    %s" % os.path.join(sParentFolderPath, sModuleName);
      print "Once you have completed these steps, please try again.";
      print "*" * 80;
    raise;

from cBugId import cBugId;
from dxConfig import dxConfig;
from fDumpExceptionAndExit import fDumpExceptionAndExit;
from fPrintLogo import fPrintLogo;
from fPrintUsage import fPrintUsage;
from fVersionCheck import fVersionCheck;
from mColors import *;
import mFileSystem;
import mWindowsAPI;
from oConsole import oConsole;

# Rather than a command line, a known application keyword can be provided. The default command line for such
# applications can be provided below and will be used if the keyword is provided as the command line by the user:
sProgramFilesPath = os.getenv("ProgramFiles");
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");
# All application specific settings and features are in the process of being moved
# to a sub-module. This should clean up the code quite a bit when finished.
from ddxApplicationSettings_by_sKeyword import ddxApplicationSettings_by_sKeyword;

gdfCleanup_by_sKeyword = {};
for (sKeyword, dxApplicationSettings) in ddxApplicationSettings_by_sKeyword.items():
  gdfCleanup_by_sKeyword[sKeyword] = dxApplicationSettings.get("fCleanup");

gdApplication_sBinaryPath_by_sKeyword = {
  "aoo-writer": r"%s\OpenOffice 4\program\swriter.exe" % sProgramFilesPath_x86,
  "acrobat": r"%s\Adobe\Reader 11.0\Reader\AcroRd32.exe" % sProgramFilesPath_x86,
  "acrobatdc": r"%s\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe" % sProgramFilesPath_x86,
  "foxit": r"%s\Foxit Software\Foxit Reader\FoxitReader.exe" % sProgramFilesPath_x86,
};
for (sKeyword, dxApplicationSettings) in ddxApplicationSettings_by_sKeyword.items():
  gdApplication_sBinaryPath_by_sKeyword[sKeyword] = dxApplicationSettings.get("sBinaryPath");

gsUWPApplicationPackageName_by_sKeyword = {};
gsUWPApplicationId_by_sKeyword = {};
for (sKeyword, dxApplicationSettings) in ddxApplicationSettings_by_sKeyword.items():
  dxUwpApplication = dxApplicationSettings.get("dxUWPApplication");
  if dxUwpApplication:
    gsUWPApplicationPackageName_by_sKeyword[sKeyword] = dxUwpApplication["sPackageName"];
    gsUWPApplicationId_by_sKeyword[sKeyword] = dxUwpApplication["sId"];

gasApplicationAttachToProcessesForExecutableNames_by_sKeyword = {};
for (sKeyword, dxApplicationSettings) in ddxApplicationSettings_by_sKeyword.items():
  gasApplicationAttachToProcessesForExecutableNames_by_sKeyword[sKeyword] = \
      dxApplicationSettings.get("asApplicationAttachToProcessesForExecutableNames");
# These arguments are always added
gdApplication_fasGetStaticArguments_by_sKeyword = {
  "aoo-writer": lambda bForHelp: ["-norestore", "-view", "-nologo", "-nolockcheck"],
};
for (sKeyword, dxApplicationSettings) in ddxApplicationSettings_by_sKeyword.items():
  gdApplication_fasGetStaticArguments_by_sKeyword[sKeyword] = dxApplicationSettings.get("fasGetStaticArguments");

# These arguments are added if the 
DEFAULT_BROWSER_TEST_URL = {}; # Placeholder for dxConfig["sDefaultBrowserTestURL"]
gdApplication_fasGetOptionalArguments_by_sKeyword = {
  "acrobat": lambda: ["repro.pdf"],
  "acrobatdc": lambda: ["repro.pdf"],
  "foxit": lambda: ["repro.pdf"],
};
for (sKeyword, dxApplicationSettings) in ddxApplicationSettings_by_sKeyword.items():
  gdApplication_fasGetOptionalArguments_by_sKeyword[sKeyword] = dxApplicationSettings["fasGetOptionalArguments"];

gdApplication_sISA_by_sKeyword = {
  # Applications will default to cBugId.sOSISA. Applications need only be added here if they can differ from that.
  "aoo-writer": "x86",
  "acrobat": "x86",
  "acrobatdc": "x86",
  "foxit": "x86",
};
for (sKeyword, dxApplicationSettings) in ddxApplicationSettings_by_sKeyword.items():
  gdApplication_sISA_by_sKeyword[sKeyword] = dxApplicationSettings.get("sISA");

dxBrowserSettings = {
  # Settings used by all browsers (these should eventually be fine-tuned for each browser)
  "bApplicationTerminatesWithMainProcess": True,
  "nExcessiveCPUUsageCheckInitialTimeout": 30.0, # Give browser some time to load repro
  "cBugId.nExcessiveCPUUsageCheckInterval": 30.0, # Browser may be busy for a bit, but no longer than 30 seconds.
  "cBugId.nExcessiveCPUUsagePercent": 95,      # Browser msust be very, very busy.
  "cBugId.nExcessiveCPUUsageWormRunTime": 0.5, # Any well written function should return within half a second IMHO.
};

gdApplication_dxConfigSettings_by_sKeyword = {
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
  "foxit": {
    "bApplicationTerminatesWithMainProcess": True,
    "nApplicationMaxRunTime": 10.0, # Normally loads within 2 seconds, but give it some more to be sure.
    "nExcessiveCPUUsageCheckInitialTimeout": 10.0, # Give application some time to load repro
    "cBugId.nExcessiveCPUUsageCheckInterval": 5.0, # Application should not be busy for more than 5 seconds.
    "cBugId.nExcessiveCPUUsagePercent": 75,      # Application must be relatively busy.
    "cBugId.nExcessiveCPUUsageWormRunTime": 0.5, # Any well written function should return within half a second IMHO.
  },
};
for (sKeyword, dxApplicationSettings) in ddxApplicationSettings_by_sKeyword.items():
  gdApplication_dxConfigSettings_by_sKeyword[sKeyword] = dxApplicationSettings.get("dxConfigSettings");

# Known applications can have regular expressions that map source file paths in its output to URLs, so the details HTML
# for any detected bug can have clickable links to an online source repository:
srMozillaCentralSourceURLMappings = "".join([
  r"c:[\\/]builds[\\/]moz2_slave[\\/][^\\/]+[\\/]build[\\/](?:src[\\/])?", # absolute file path
  r"(?P<path>[^:]+\.\w+)", # relative file path
  r"(:| @ |, line )", # separator
  r"(?P<lineno>\d+)",  # line number
]);
gdApplication_sURLTemplate_by_srSourceFilePath_by_sKeyword = {
};
for (sKeyword, dxApplicationSettings) in ddxApplicationSettings_by_sKeyword.items():
  gdApplication_sURLTemplate_by_srSourceFilePath_by_sKeyword[sKeyword] = \
      dxApplicationSettings.get("dsURLTemplate_by_srSourceFilePath");

# Known applications can also have regular expressions that detect important lines in its stdout/stderr output. These
# will be shown prominently in the details HTML for any detected bug.
gdApplication_rImportantStdOutLines_by_sKeyword = {};
gdApplication_rImportantStdErrLines_by_sKeyword = {};
gbAnErrorOccured = False;

gasBinariesThatAreAllowedToRunWithoutPageHeap = [s.lower() for s in [
  # Chrome provides ASan builds, so page heap is redundant. You can and should still run it with page heap though.
  "chrome.exe",
  # Firefox uses jemalloc, so page heap is not very useful. You can and should still run it with page heap though.
  "firefox.exe",
  # Adobe Reader has a component that crashes immediately with a NULL pointer exception when you enable page heap.
  "rdrcef.exe",
  # Applications may spawn additional console applications, which require conhost.exe. This executable is part of the
  # windows OS and not part of the application, so you may want to keep page heap disabled for it.
  "conhost.exe",
]];
asApplicationKeywords = sorted(list(set(
  gdApplication_sBinaryPath_by_sKeyword.keys() +
  gsUWPApplicationPackageName_by_sKeyword.keys() +
  gsUWPApplicationId_by_sKeyword.keys() + # should be the same as above!
  gasApplicationAttachToProcessesForExecutableNames_by_sKeyword.keys() +
  gdApplication_fasGetStaticArguments_by_sKeyword.keys() +
  gdApplication_fasGetOptionalArguments_by_sKeyword.keys() +
  gdApplication_dxConfigSettings_by_sKeyword.keys() +
  gdApplication_sURLTemplate_by_srSourceFilePath_by_sKeyword.keys() + 
  gdApplication_rImportantStdOutLines_by_sKeyword.keys() +
  gdApplication_rImportantStdErrLines_by_sKeyword.keys()
)));
gbQuiet = False;
gbVerbose = False;
guDefaultCollateralMaximumNumberOfBugs = 5; # Just a hunch that that's a reasonable value.

def fuShowApplicationKeyWordHelp(sApplicationKeyword):
  if sApplicationKeyword not in asApplicationKeywords:
    oConsole.fPrint(ERROR, "- Unknown application keyword ", ERROR_INFO, sApplicationKeyword, ERROR, ".");
    return 2;
  oConsole.fPrint("Known application settings for ", sApplicationKeyword);
  if sApplicationKeyword in gdApplication_sBinaryPath_by_sKeyword:
    if gdApplication_sBinaryPath_by_sKeyword[sApplicationKeyword] is None:
      oConsole.fPrint(ERROR, "  The application cannot be found on your system.");
    else:
      oConsole.fPrint("  Binary path: ", INFO, gdApplication_sBinaryPath_by_sKeyword[sApplicationKeyword]);
  elif sApplicationKeyword in gsUWPApplicationPackageName_by_sKeyword:
    oConsole.fLock();
    try:
      oConsole.fPrint("  UWP Application information:");
      oConsole.fPrint("    Package name: ", INFO, gsUWPApplicationPackageName_by_sKeyword[sApplicationKeyword]);
      oConsole.fPrint("    Id: ", INFO, gsUWPApplicationId_by_sKeyword[sApplicationKeyword]);
      if sApplicationKeyword in gasApplicationAttachToProcessesForExecutableNames_by_sKeyword:
        oConsole.fPrint("    Attach to additional processes running any of the following binaries:");
        for sBinaryName in gasApplicationAttachToProcessesForExecutableNames_by_sKeyword[sApplicationKeyword]:
          oConsole.fPrint("      ", INFO, sBinaryName);
    finally:
      oConsole.fUnlock();
  if gdApplication_fasGetStaticArguments_by_sKeyword.get(sApplicationKeyword):
    fasGetStaticArguments = gdApplication_fasGetStaticArguments_by_sKeyword[sApplicationKeyword];
    oConsole.fPrint("  Default static arguments: ", INFO, " ".join(
      fasGetStaticArguments(bForHelp = True))
    );
  if sApplicationKeyword in gdApplication_fasGetOptionalArguments_by_sKeyword:
    asOptionalArguments = gdApplication_fasGetOptionalArguments_by_sKeyword[sApplicationKeyword](bForHelp = True)
    oConsole.fPrint("  Default optional arguments: ", INFO, " ".join(asOptionalArguments));
  if gdApplication_dxConfigSettings_by_sKeyword.get(sApplicationKeyword):
    oConsole.fLock();
    try:
      oConsole.fPrint("  Application specific settings:");
      for sSettingName, xValue in gdApplication_dxConfigSettings_by_sKeyword[sApplicationKeyword].items():
        oConsole.fPrint("    ", HILITE, sSettingName, NORMAL, " = ", INFO, json.dumps(xValue));
    finally:
      oConsole.fUnlock();
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
    if gbVerbose:
      oConsole.fPrint(sIndentation, "* The default value for config setting ", HILITE, sFullName, NORMAL, \
          " is ", json.dumps(dxConfigGroup[sSettingName]), ".");
  else:
    if gbVerbose:
      oConsole.fPrint(sIndentation, "+ Changed config setting ", HILITE, sFullName, NORMAL, \
          " from ", HILITE, repr(dxConfigGroup[sSettingName]), NORMAL, " to ", INFO, repr(xValue), NORMAL, ".");
    dxConfigGroup[sSettingName] = xValue;

def fApplicationRunningHandler(oBugId):
  oConsole.fStatus("* The application was started successfully and is running...");

def fApplicationSuspendedHandler(oBugId, sReason):
  oConsole.fStatus("* T+%.1f The application is suspended (%s)..." % (oBugId.fnApplicationRunTime(), sReason));

def fApplicationResumedHandler(oBugId):
  oConsole.fStatus("* The application is running...");

def fApplicationRunTimeHandler(oBugId):
  oConsole.fPrint("+ T+%.1f The application has been running for %.1f seconds without crashing." % \
      (oBugId.fnApplicationRunTime(), dxConfig["nApplicationMaxRunTime"]));
  oConsole.fPrint();
  oConsole.fStatus(INFO, "* BugId is stopping...");
  oBugId.fStop();

def fInternalExceptionHandler(oBugId, oException, oTraceBack):
  global gbAnErrorOccured;
  gbAnErrorOccured = True;
  fDumpExceptionAndExit(oException, oTraceBack);

def fFailedToDebugApplicationHandler(oBugId, sErrorMessage):
  global gbAnErrorOccured;
  gbAnErrorOccured = True;
  oConsole.fLock();
  try:
    oConsole.fPrint(ERROR, "-" * 80);
    oConsole.fPrint(ERROR, "- Failed to debug the application:");
    for sLine in sErrorMessage.split("\n"):
      oConsole.fPrint(ERROR, "  ", sLine.rstrip("\r"));
    oConsole.fPrint(ERROR, "-" * 80);
    oConsole.fPrint();
  finally:
    oConsole.fUnlock();

gasReportedBinaryNameWithoutPageHeap = [];
gasAttachToProcessesForExecutableNames = [];
def fPageHeapNotEnabledHandler(oBugId, uProcessId, sBinaryName, sCommandLine, bIsMainProcess, bPreventable):
  global gbAnErrorOccured, \
         gasBinariesThatAreAllowedToRunWithoutPageHeap, \
         gasReportedBinaryNameWithoutPageHeap, \
         gasAttachToProcessesForExecutableNames;
  if sBinaryName.lower() in gasBinariesThatAreAllowedToRunWithoutPageHeap:
    return;
  if not bPreventable:
    if not gbQuiet and sBinaryName not in gasReportedBinaryNameWithoutPageHeap:
      gasReportedBinaryNameWithoutPageHeap.append(sBinaryName);
      oConsole.fLock();
      try:
        oConsole.fPrint(ERROR,"- Full page heap is not enabled for ", ERROR_INFO, sBinaryName, ERROR,".");
        oConsole.fPrint("  This appears to be due to a bug in page heap that prevents it from");
        oConsole.fPrint("  determining the binary name correctly. Unfortunately, there is no known fix");
        oConsole.fPrint("  or work-around for this. BugId will continue, but detection and analysis of");
        oConsole.fPrint("  any bugs in this process will be sub-optimal.");
        oConsole.fPrint();
      finally:
        oConsole.fUnlock();
  else:
    gbAnErrorOccured = True;
    oConsole.fLock();
    try:
      oConsole.fPrint(ERROR, "- Full page heap is not enabled for all binaries used by the application.");
      oConsole.fPrint(ERROR, "  Specifically it is not enabled for ", ERROR_INFO, sBinaryName, ERROR,".");
      oConsole.fPrint("  You can enabled full page heap for ", sBinaryName, " by running:");
      oConsole.fPrint();
      oConsole.fPrint("      ", INFO, 'PageHeap.cmd "', sBinaryName, '" ON');
      oConsole.fPrint();
      oConsole.fPrint("  Without page heap enabled, detection and anaylsis of any bugs will be sub-");
      oConsole.fPrint("  optimal. Please enable page heap and try again.");
      oConsole.fPrint();
      oConsole.fStatus(INFO, "* BugId is stopping...");
    finally:
      oConsole.fUnlock();
    # There is no reason to run without page heap, so terminated.
    oBugId.fStop();
    # If you really want to run without page heap, set `dxConfig["cBugId"]["bEnsurePageHeap"]` to `False` in
    # `dxConfig.py`or run with the command-line siwtch `--cBugId.bEnsurePageHeap=false`

def fCdbStdInInputHandler(oBugId, sInput):
  oConsole.fPrint(HILITE, "<stdin<", NORMAL, sInput, uConvertTabsToSpaces = 8);
def fCdbStdOutOutputHandler(oBugId, sOutput):
  oConsole.fPrint(INFO, "stdout>", NORMAL, sOutput, uConvertTabsToSpaces = 8);
def fCdbStdErrOutputHandler(oBugId, sOutput):
  oConsole.fPrint(ERROR_INFO, "stderr>", ERROR, sOutput, uConvertTabsToSpaces = 8);

# Helper function to format messages that are specific to a process.
def fShowMessageForProcess(sHeaderChar, uProcessId, sBinaryName, bIsMainProcess, *asMessage):
  oConsole.fPrint(
    sHeaderChar, " ", bIsMainProcess and "Main" or "Sub", " process ",
    INFO, "%d" % uProcessId, NORMAL, "/", INFO , "0x%X" % uProcessId, NORMAL,
    " (", INFO, sBinaryName, NORMAL, "): ",
    *asMessage,
    uConvertTabsToSpaces = 8
  );

gbFailedToApplyMemoryLimitsErrorShown = False;
def fFailedToApplyApplicationMemoryLimitsHandler(oBugId, uProcessId, sBinaryName, sCommandLine, bIsMainProcess):
  global gbFailedToApplyMemoryLimitsErrorShown, gbQuiet, gbVerbose;
  if not gbQuiet:
    fShowMessageForProcess("-", uProcessId, sBinaryName, bIsMainProcess,
        ERROR_INFO, "Cannot apply application memory limits");
    gbFailedToApplyMemoryLimitsErrorShown = True;
    if not gbVerbose:
      oConsole.fPrint("  Any additional failures to apply memory limits to processess will not be shown.");
def fFailedToApplyProcessMemoryLimitsHandler(oBugId, uProcessId, sBinaryName, sCommandLine, bIsMainProcess):
  global gbFailedToApplyMemoryLimitsErrorShown, gbVerbose;
  if gbVerbose or not gbFailedToApplyMemoryLimitsErrorShown:
    fShowMessageForProcess("-", uProcessId, sBinaryName, bIsMainProcess,
        ERROR_INFO, "Cannot apply process memory limits");
    gbFailedToApplyMemoryLimitsErrorShown = True;
    if not gbVerbose:
      oConsole.fPrint("  Any additional failures to apply memory limits to processess will not be shown.");


def fStartedProcessHandler(oBugId, uProcessId, sBinaryName, sCommandLine, bIsMainProcess):
  fNewProcessHandler(oBugId, uProcessId, sBinaryName, sCommandLine, bIsMainProcess, bAttached = False);
def fAttachedToProcessHandler(oBugId, uProcessId, sBinaryName, sCommandLine, bIsMainProcess):
  fNewProcessHandler(oBugId, uProcessId, sBinaryName, sCommandLine, bIsMainProcess, bAttached = True);
def fNewProcessHandler(oBugId, uProcessId, sBinaryName, sCommandLine, bIsMainProcess, bAttached):
  global gasAttachToProcessesForExecutableNames;
  if not gbQuiet:
    fShowMessageForProcess("+", uProcessId, sBinaryName, bIsMainProcess,
      bAttached and "Attached" or "Started", "; command line = ", INFO, sCommandLine or "<unknown>", NORMAL, "."
    );
  # Now is a good time to look for additional binaries that may need to be debugged as well.
  if gasAttachToProcessesForExecutableNames:
    oBugId.fAttachToProcessesForExecutableNames(*gasAttachToProcessesForExecutableNames);

def fApplicationStdOutOutputHandler(oBugId, uProcessId, sBinaryName, sCommandLine, sMessage):
  fShowMessageForProcess("*", uProcessId, sBinaryName, True, # Always a main process
    INFO, "stdout", NORMAL, ">", HILITE, sMessage,
  );
def fApplicationStdErrOutputHandler(oBugId, uProcessId, sBinaryName, sCommandLine, sMessage):
  fShowMessageForProcess("*", uProcessId, sBinaryName, True, # Always a main process
    ERROR, "stderr", NORMAL, ">", ERROR_INFO, sMessage,
  );

def fProcessTerminatedHandler(oBugId, uProcessId, sBinaryName, sCommandLine, bIsMainProcess):
  bStopBugId = bIsMainProcess and dxConfig["bApplicationTerminatesWithMainProcess"];
  if not gbQuiet:
    fShowMessageForProcess("-", uProcessId, sBinaryName, bIsMainProcess,
      "Terminated", bStopBugId and "; the application is considered to have terminated with it." or ".",
    );
  if bStopBugId:
    oConsole.fStatus(INFO, "* BugId is stopping because a main process terminated...");
    oBugId.fStop();

guDetectedBugsCount = 0;
guMaximumNumberOfBugs = 1;
def fBugReportHandler(oBugId, oBugReport):
  global guDetectedBugsCount, guMaximumNumberOfBugs;
  guDetectedBugsCount += 1;
  oConsole.fLock();
  try:
    oConsole.fPrint(u"\u250C\u2500 ", HILITE, "A bug was detect in the application ", NORMAL, sPadding = u"\u2500");
    if oBugReport.sBugLocation:
      oConsole.fPrint(u"\u2502 Id @ Location:    ", INFO, oBugReport.sId, NORMAL, " @ ", INFO, oBugReport.sBugLocation);
      sBugIdAndLocation = "%s @ %s" % (oBugReport.sId, oBugReport.sBugLocation);
    else:
      oConsole.fPrint(u"\u2502 Id:               ", INFO, oBugReport.sId);
      sBugIdAndLocation = oBugReport.sId;
    if oBugReport.sBugSourceLocation:
      oConsole.fPrint(u"\u2502 Source:           ", INFO, oBugReport.sBugSourceLocation);
    oConsole.fPrint(u"\u2502 Description:      ", INFO, oBugReport.sBugDescription);
    oConsole.fPrint(u"\u2502 Security impact:  ", INFO, oBugReport.sSecurityImpact);
    oConsole.fPrint(u"\u2502 Version:          ", NORMAL, oBugReport.asVersionInformation[0]); # The process' binary.
    for sVersionInformation in oBugReport.asVersionInformation[1:]: # There may be two if the crash was in a
      oConsole.fPrint(u"\u2502                   ", NORMAL, sVersionInformation); # different binary (e.g. a .dll)
    if dxConfig["bGenerateReportHTML"]:
      # Use a report file name base on the BugId.
      sDesiredReportFileName = "%s.html" % sBugIdAndLocation;
      # In collateral mode, we will number the reports so you know in which order bugs were reported.
      if guMaximumNumberOfBugs > 1:
        sDesiredReportFileName = "#%d %s" % (guDetectedBugsCount, sDesiredReportFileName);
      # Translate characters that are not valid in file names.
      sValidReportFileName = mFileSystem.fsValidName(sDesiredReportFileName, bUnicode = \
          dxConfig["bUseUnicodeReportFileNames"]);
      if dxConfig["sReportFolderPath"] is not None:
        sReportFilePath = mFileSystem.fsPath(dxConfig["sReportFolderPath"], sValidReportFileName);
      else:
        sReportFilePath = mFileSystem.fsPath(sValidReportFileName);
      eWriteDataToFileResult = mFileSystem.feWriteDataToFile(
        oBugReport.sReportHTML,
        sReportFilePath,
        fbRetryOnFailure = lambda: False,
      );
      if eWriteDataToFileResult:
        oConsole.fPrint(u"\u2502 Bug report:       ", ERROR, "Cannot be saved (", \
            ERROR_INFO, repr(eWriteDataToFileResult), ERROR, ")");
      else:
        oConsole.fPrint(u"\u2502 Bug report:       ", NORMAL, sValidReportFileName,  \
            " (%d bytes)" % len(oBugReport.sReportHTML));
    oConsole.fPrint(u"\u2516", sPadding = u"\u2500");
  finally:
    oConsole.fUnlock();

def fuMain(asArguments):
  global gbVerbose, gbQuiet, gasAttachToProcessesForExecutableNames, guMaximumNumberOfBugs, guDetectedBugsCount;
  if len(asArguments) == 0:
    fPrintLogo();
    fPrintUsage(asApplicationKeywords);
    return 0;
  # Parse all arguments until we encounter "--".
  sApplicationKeyword = None;
  sApplicationBinaryPath = None;
  auApplicationProcessIds = [];
  sUWPApplicationPackageName = None;
  sUWPApplicationId = None;
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
        oConsole.fPrint(ERROR, "- You cannot provide process ids and application arguments.");
        return 2;
      asApplicationOptionalArguments = asArguments;
      break;
    elif sArgument in ["-q", "/q"]:
      gbQuiet = True;
    elif sArgument in ["-v", "/v"]:
      gbVerbose = True;
    elif sArgument in ["-f", "/f"]:
      bFast = True;
    elif sArgument in ["-r", "/r"]:
      bRepeat = True;
    elif sArgument in ["-c", "/c"]:
      guMaximumNumberOfBugs = guDefaultCollateralMaximumNumberOfBugs;
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
        sValue = None;
      
      if sSettingName in ["pid", "pids"]:
        if not sValue:
          oConsole.fPrint(ERROR, "- You must provide at least one process id.");
          return 2;
        if sApplicationBinaryPath is not None:
          oConsole.fPrint(ERROR, "- You cannot provide an application binary and process ids.");
          return 2;
        if sUWPApplicationPackageName is not None:
          oConsole.fPrint(ERROR, "- You cannot provide an UWP application package name and process ids.");
          return 2;
        auApplicationProcessIds += [long(x) for x in sValue.split(",")];
      elif sSettingName in ["uwp", "uwp-app"]:
        if not sValue:
          oConsole.fPrint(ERROR, "- You must provide an UWP application package name.");
          return 2;
        if sUWPApplicationPackageName is not None:
          oConsole.fPrint(ERROR, "- You cannot provide multiple UWP application package names.");
          return 2;
        if sApplicationBinaryPath is not None:
          oConsole.fPrint(ERROR, "- You cannot provide an application binary and UWP package name.");
          return 2;
        if len(auApplicationProcessIds) > 0:
          oConsole.fPrint(ERROR, "- You cannot provide process ids and an UWP application package name.");
          return 2;
        if "!" not in sValue:
          oConsole.fPrint(ERROR, "- Please provide a string of the form ", ERROR_INFO, sSettingName, \
              "=<package name>!<application id>.");
          return 2;
        sUWPApplicationPackageName, sUWPApplicationId = sValue.split("!", 1);
      elif sSettingName in ["help"]:
        fPrintLogo();
        fPrintUsage(asApplicationKeywords);
        return 0;
      elif sSettingName in ["version", "check-for-updates"]:
        fVersionCheck();
        return 0;
      elif sSettingName in ["isa", "cpu"]:
        if not sValue:
          oConsole.fPrint(ERROR, "- You must provide an Instruction Set Architecture.");
          return 2;
        if sValue not in ["x86", "x64"]:
          oConsole.fPrint(ERROR, "- Unknown Instruction Set Architecture ", repr(sValue));
          return 2;
        sApplicationISA = sValue;
      elif sSettingName in ["quiet", "silent"]:
        if sValue is None or sValue.lower() == "true":
          gbQuiet = True;
        elif sValue.lower() == "false":
          gbQuiet = False;
        else:
          oConsole.fPrint(ERROR, "- The value for ", ERROR_INFO, "--", sSettingName, ERROR, \
              " must be \"true\" or \"false\".");
      elif sSettingName in ["verbose", "debug"]:
        if sValue is None or sValue.lower() == "true":
          gbVerbose = True;
        elif sValue.lower() == "false":
          gbVerbose = False;
        else:
          oConsole.fPrint(ERROR, "- The value for ", ERROR_INFO, "--", sSettingName, ERROR, \
              " must be \"true\" or \"false\".");
      elif sSettingName in ["fast", "quick"]:
        if sValue is None or sValue.lower() == "true":
          bFast = True;
        elif sValue.lower() == "false":
          bFast = False;
        else:
          oConsole.fPrint(ERROR, "- The value for ", ERROR_INFO, "--", sSettingName, ERROR, \
              " must be \"true\" or \"false\".");
      elif sSettingName in ["repeat", "forever"]:
        if sValue is None or sValue.lower() == "true":
          bRepeat = True;
        elif sValue.lower() == "false":
          bRepeat = False;
        else:
          oConsole.fPrint(ERROR, "- The value for ", ERROR_INFO, "--", sSettingName, ERROR, \
              " must be \"true\" or \"false\".");
      elif sSettingName in ["collateral"]:
        if sValue is None:
          guMaximumNumberOfBugs = guDefaultCollateralMaximumNumberOfBugs;
        else:
          guMaximumNumberOfBugs = long(sValue);
      elif sSettingName in ["test-internal-error", "internal-error-test"]:
        raise Exception("Testing internal error");
      else:
        if not sValue:
          oConsole.fPrint(ERROR, "- You cannot provide an argument (", ERROR_INFO, "--", sSettingName, ERROR, \
              ") without a value.");
          return 2;
        try:
          xValue = json.loads(sValue);
        except ValueError as oError:
          oConsole.fPrint(ERROR, "- Cannot decode argument JSON value ", ERROR_INFO, "--", sSettingName, "=", sValue, \
              ERROR, ": ", ERROR_INFO, " ".join(oError.args), ERROR, ".");
          return 2;
        # User provided config settings must be applied after any keyword specific config settings:
        dxUserProvidedConfigSettings[sSettingName] = xValue;
    elif sArgument in asApplicationKeywords:
      if sApplicationKeyword is not None:
        oConsole.fPrint(ERROR, "- You cannot provide multiple application keywords.");
        return 2;
      sApplicationKeyword = sArgument;
    elif sArgument[-1] == "?" and sArgument[:-1] in asApplicationKeywords:
      return fuShowApplicationKeyWordHelp(sArgument[:-1]);
    else:
      if sApplicationBinaryPath is not None:
        oConsole.fLock();
        try:
          oConsole.fPrint(ERROR, "- You cannot provide multiple application binaries.");
          oConsole.fPrint(ERROR, "  (Did you perhaps forget to put ", ERROR_INFO, "--", ERROR, \
              " before the start of the application arguments?)");
        finally:
          oConsole.fUnlock();
        return 2;
      if len(auApplicationProcessIds) > 0:
        oConsole.fPrint(ERROR, "- You cannot provide process ids and an application binary.");
        return 2;
      if sUWPApplicationPackageName is not None:
        oConsole.fPrint(ERROR, "- You cannot provide an application UWP package name and a binary.");
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
  
  fCleanup = None;
  if sApplicationKeyword:
    fCleanup = gdfCleanup_by_sKeyword.get(sApplicationKeyword) or None;
    # Get application binary/UWP package name/process ids as needed:
    if sApplicationKeyword in gsUWPApplicationPackageName_by_sKeyword:
      # This application is started as an application package.
      if sApplicationBinaryPath:
        oConsole.fPrint(ERROR, "- You cannot provide an application binary for application keyword ", \
            ERROR_INFO, sApplicationKeyword, ERROR, ".");
        return 2;
      sUWPApplicationPackageName = gsUWPApplicationPackageName_by_sKeyword[sApplicationKeyword];
      sUWPApplicationId = gsUWPApplicationId_by_sKeyword[sApplicationKeyword];
    elif sApplicationKeyword in gdApplication_sBinaryPath_by_sKeyword:
      # This application is started from the command-line.
      if auApplicationProcessIds:
        oConsole.fPrint(ERROR, "- You cannot provide process ids for application keyword ", ERROR_INFO, \
            sApplicationKeyword, ERROR, ".");
        return 2;
      if sUWPApplicationPackageName:
        oConsole.fPrint(ERROR, "- You cannot provide an application UWP package name for application keyword ", \
            ERROR_INFO, sApplicationKeyword, ERROR, ".");
        return 2;
      if sApplicationBinaryPath is None:
        sApplicationBinaryPath = gdApplication_sBinaryPath_by_sKeyword[sApplicationKeyword];
        if sApplicationBinaryPath is None:
          oConsole.fPrint(ERROR, "- The main application binary for ", ERROR_INFO, sApplicationKeyword, \
              ERROR, " could not be detected on your system.");
          oConsole.fPrint(ERROR, "  Please provide the path to this binary in the arguments.");
          return 4;
    elif not auApplicationProcessIds:
      # This application is attached to.
      oConsole.fPrint(ERROR, "- You must provide process ids for application keyword ", \
          ERROR_INFO, sApplicationKeyword, ERROR, ".");
      return 2;
    elif asApplicationOptionalArguments:
      # Cannot provide arguments if we're attaching to processes
      oConsole.fPrint(ERROR, "- You cannot provide arguments for application keyword ", \
          ERROR_INFO, sApplicationKeyword, ERROR, ".");
      return 2;
    if sApplicationKeyword in gasApplicationAttachToProcessesForExecutableNames_by_sKeyword:
      gasAttachToProcessesForExecutableNames = \
          gasApplicationAttachToProcessesForExecutableNames_by_sKeyword[sApplicationKeyword];
    # Get application arguments;
    fasGetApplicationStaticArguments = gdApplication_fasGetStaticArguments_by_sKeyword.get(sApplicationKeyword, None);
    asApplicationStaticArguments = fasGetApplicationStaticArguments and \
        fasGetApplicationStaticArguments(bForHelp = False) or [];
    if asApplicationOptionalArguments is None:
      asApplicationOptionalArguments = gdApplication_fasGetOptionalArguments_by_sKeyword[sApplicationKeyword]();
    asApplicationArguments = asApplicationStaticArguments + asApplicationOptionalArguments;
    # Apply application specific settings
    if sApplicationKeyword in gdApplication_dxConfigSettings_by_sKeyword:
      if gbVerbose:
        oConsole.fPrint("* Applying application specific configuration for %s:" % sApplicationKeyword);
      for (sSettingName, xValue) in gdApplication_dxConfigSettings_by_sKeyword[sApplicationKeyword].items():
        if sSettingName not in dxUserProvidedConfigSettings:
          fApplyConfigSetting(sSettingName, xValue, "  "); # Apply and show result indented.
      if gbVerbose:
        oConsole.fPrint();
    # Apply application specific source settings
    if gdApplication_sURLTemplate_by_srSourceFilePath_by_sKeyword.get(sApplicationKeyword):
      dsURLTemplate_by_srSourceFilePath = \
          gdApplication_sURLTemplate_by_srSourceFilePath_by_sKeyword[sApplicationKeyword];
    # Apply application specific stdio settings:
    if sApplicationKeyword in gdApplication_rImportantStdOutLines_by_sKeyword:
      rImportantStdOutLines = gdApplication_rImportantStdOutLines_by_sKeyword[sApplicationKeyword];
    if sApplicationKeyword in gdApplication_rImportantStdErrLines_by_sKeyword:
      rImportantStdErrLines = gdApplication_rImportantStdErrLines_by_sKeyword[sApplicationKeyword];
    # If not ISA is specified, apply the application specific ISA (if any).
    sApplicationISA = sApplicationISA or gdApplication_sISA_by_sKeyword.get(sApplicationKeyword);
  elif (auApplicationProcessIds or sUWPApplicationPackageName or sApplicationBinaryPath):
    # There are no static arguments if there is no application keyword, only the user-supplied optional arguments
    # are used if they are supplied:
    asApplicationArguments = asApplicationOptionalArguments or [];
  else:
    oConsole.fLock();
    try:
      oConsole.fPrint(ERROR, "- You must provide something to debug. This can be either one or more process");
      oConsole.fPrint(ERROR, "  ids, an application command-line or an UWP application package name.");
      oConsole.fPrint("Run \"", INFO, "BugId -h", NORMAL, "\" for help on command-line arguments.");
    finally:
      oConsole.fUnlock();
    return 2;
  
  # Apply user provided settings:
  for (sSettingName, xValue) in dxUserProvidedConfigSettings.items():
    fApplyConfigSetting(sSettingName, xValue, ""); # Apply and show result
  
  if bRepeat:
    duNumberOfRepros_by_sBugIdAndLocation = {};
    sValidStatisticsFileName = mFileSystem.fsValidName("Reproduction statistics.txt");
  uRunCounter = 0;
  while 1: # Will only loop if bRepeat is True
    nStartTime = time.clock();
    if fCleanup and dxConfig["bCleanup"]:
      oConsole.fStatus("* Cleaning up application state...");
      fCleanup();
    uRunCounter += 1;
    oConsole.fLock();
    try:
      if sApplicationBinaryPath:
        if not gbQuiet:
          asCommandLine = [sApplicationBinaryPath] + asApplicationArguments;
          oConsole.fPrint("* Command line: ", INFO, " ".join(asCommandLine));
        oConsole.fStatus("* The debugger is starting the application...");
      else:
        if auApplicationProcessIds:
          asProcessIdsOutput = [];
          for uApplicationProcessId in auApplicationProcessIds:
            if asProcessIdsOutput: asProcessIdsOutput.append(", ");
            asProcessIdsOutput.extend([INFO, str(uApplicationProcessId), NORMAL]);
          oConsole.fPrint("* Running process ids: ", INFO, *asProcessIdsOutput);
        if sUWPApplicationPackageName:
          if not gbQuiet:
            if asApplicationArguments:
              oConsole.fPrint("* UWP application id: ", INFO, sUWPApplicationId, NORMAL, ", package name: ", INFO, \
                  sUWPApplicationPackageName, NORMAL, ", Arguments: ", INFO, " ".join(asApplicationArguments));
            else:
              oConsole.fPrint("* UWP application id: ", INFO, sUWPApplicationId, NORMAL, ", package name: ", INFO, \
                  sUWPApplicationPackageName);
        if not sUWPApplicationPackageName:
          oConsole.fStatus("* The debugger is attaching to running processes of the application...");
        elif auApplicationProcessIds:
          oConsole.fStatus("* The debugger is attaching to running processes and starting the application...");
        else:
          oConsole.fStatus("* The debugger is starting the application...");
    finally:
      oConsole.fUnlock();
    oBugId = cBugId(
      sCdbISA = sApplicationISA or cBugId.sOSISA,
      sApplicationBinaryPath = sApplicationBinaryPath or None,
      auApplicationProcessIds = auApplicationProcessIds or None,
      sUWPApplicationPackageName = sUWPApplicationPackageName or None,
      sUWPApplicationId = sUWPApplicationId or None,
      asApplicationArguments = asApplicationArguments,
      asLocalSymbolPaths = dxConfig["asLocalSymbolPaths"],
      asSymbolCachePaths = dxConfig["asSymbolCachePaths"], 
      asSymbolServerURLs = dxConfig["asSymbolServerURLs"],
      dsURLTemplate_by_srSourceFilePath = dsURLTemplate_by_srSourceFilePath,
      rImportantStdOutLines = rImportantStdOutLines,
      rImportantStdErrLines = rImportantStdErrLines,
      bGenerateReportHTML = dxConfig["bGenerateReportHTML"],
      uProcessMaxMemoryUse = dxConfig["uProcessMaxMemoryUse"],
      uTotalMaxMemoryUse = dxConfig["uTotalMaxMemoryUse"],
      uMaximumNumberOfBugs = guMaximumNumberOfBugs,
    );
    oBugId.fAddEventCallback("Failed to debug application", fFailedToDebugApplicationHandler);
    oBugId.fAddEventCallback("Failed to apply application memory limits", fFailedToApplyApplicationMemoryLimitsHandler);
    oBugId.fAddEventCallback("Failed to apply process memory limits", fFailedToApplyProcessMemoryLimitsHandler);
    oBugId.fAddEventCallback("Application running", fApplicationRunningHandler);
    oBugId.fAddEventCallback("Application suspended", fApplicationSuspendedHandler);
    oBugId.fAddEventCallback("Application resumed", fApplicationResumedHandler);
    oBugId.fAddEventCallback("Process terminated", fProcessTerminatedHandler);
    oBugId.fAddEventCallback("Internal exception", fInternalExceptionHandler);
    oBugId.fAddEventCallback("Page heap not enabled", fPageHeapNotEnabledHandler);
    if gbVerbose:
      oBugId.fAddEventCallback("Cdb stdin input", fCdbStdInInputHandler);
      oBugId.fAddEventCallback("Cdb stdout output", fCdbStdOutOutputHandler);
    oBugId.fAddEventCallback("Cdb stderr output", fCdbStdErrOutputHandler);
    oBugId.fAddEventCallback("Started process", fStartedProcessHandler);
    oBugId.fAddEventCallback("Attached to process", fAttachedToProcessHandler);
    oBugId.fAddEventCallback("Application stdout output", fApplicationStdOutOutputHandler);
    oBugId.fAddEventCallback("Application stderr output", fApplicationStdOutOutputHandler);
    oBugId.fAddEventCallback("Bug report", fBugReportHandler);

    if dxConfig["nApplicationMaxRunTime"] is not None:
      oBugId.foSetTimeout("Maximum application runtime", dxConfig["nApplicationMaxRunTime"], \
          fApplicationRunTimeHandler);
    if dxConfig["bExcessiveCPUUsageCheckEnabled"] and dxConfig["nExcessiveCPUUsageCheckInitialTimeout"]:
      oBugId.fSetCheckForExcessiveCPUUsageTimeout(dxConfig["nExcessiveCPUUsageCheckInitialTimeout"]);
    guDetectedBugsCount = 0;
    oBugId.fStart();
    oBugId.fWait();
    if gbAnErrorOccured:
      return 3;
    if guDetectedBugsCount == 0:
      oConsole.fPrint(u"\u2500\u2500 The application terminated without a bug being detected ", sPadding = u"\u2500");
      sBugIdAndLocation = "No crash";
    if gbVerbose:
      oConsole.fPrint("  Application time: %s seconds" % (long(oBugId.fnApplicationRunTime() * 1000) / 1000.0));
      nOverheadTime = time.clock() - nStartTime - oBugId.fnApplicationRunTime();
      oConsole.fPrint("  BugId overhead:   %s seconds" % (long(nOverheadTime * 1000) / 1000.0));
    if not bRepeat:
      return guDetectedBugsCount > 0 and 1 or 0;
    duNumberOfRepros_by_sBugIdAndLocation.setdefault(sBugIdAndLocation, 0)
    duNumberOfRepros_by_sBugIdAndLocation[sBugIdAndLocation] += 1;
    sStatistics = "";
    auOrderedNumberOfRepros = sorted(list(set(duNumberOfRepros_by_sBugIdAndLocation.values())));
    auOrderedNumberOfRepros.reverse();
    for uNumberOfRepros in auOrderedNumberOfRepros:
      for sBugIdAndLocation in duNumberOfRepros_by_sBugIdAndLocation.keys():
        if duNumberOfRepros_by_sBugIdAndLocation[sBugIdAndLocation] == uNumberOfRepros:
          sStatistics += "%d \xD7 %s (%d%%)\r\n" % (uNumberOfRepros, str(sBugIdAndLocation), \
              round(100.0 * uNumberOfRepros / uRunCounter));
    if dxConfig["sReportFolderPath"] is not None:
      sStatisticsFilePath = mFileSystem.fsPath(dxConfig["sReportFolderPath"], sValidStatisticsFileName);
    else:
      sStatisticsFilePath = mFileSystem.fsPath(sValidStatisticsFileName);
    eWriteDataToFileResult = mFileSystem.feWriteDataToFile(
      sStatistics,
      sStatisticsFilePath,
      fbRetryOnFailure = lambda: False,
    );
    if eWriteDataToFileResult:
      oConsole.fPrint("  Statistics:       ", ERROR, "Cannot be saved (", ERROR_INFO, repr(eWriteDataToFileResult), \
          ERROR, ")");
    else:
      oConsole.fPrint("  Statistics:       ", INFO, sStatisticsFilePath, NORMAL, " (%d bytes)" % len(sStatistics));
    oConsole.fPrint(); # and loop

if __name__ == "__main__":
  try:
    uExitCode = fuMain(sys.argv[1:]);
    
    if not gbQuiet and dxConfig["bShowLicenseAndDonationInfo"]:
      oConsole.fLock();
      try:
        oConsole.fPrint();
        oConsole.fPrint("This version of BugId is provided free of charge for non-commercial use only.");
        oConsole.fPrint("If you find it useful and would like to make a donation, you can send bitcoin");
        oConsole.fPrint("to ",INFO,"183yyxa9s1s1f7JBpPHPmzQ346y91Rx5DX",NORMAL,".");
        oConsole.fPrint("If you wish to use BugId commercially, please contact the author to request a");
        oConsole.fPrint("quote. Contact and licensing information can be found at:");
        oConsole.fPrint("    ",INFO,"https://github.com/SkyLined/BugId#license",NORMAL,".");
      finally:
        oConsole.fUnlock();
    os._exit(uExitCode);
  except Exception as oException:
    cException, oException, oTraceBack = sys.exc_info();
    fDumpExceptionAndExit(oException, oTraceBack);
