import json, os, sys, time;

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
# 5 = license error

from fCheckDependencies import fCheckDependencies;
fCheckDependencies();

# Load the stuff from external modules that we need.
from cBugId import cBugId;
import mFileSystem2, mProductDetails, mWindowsAPI;
from oConsole import oConsole;
from ddxApplicationSettings_by_sKeyword import ddxApplicationSettings_by_sKeyword;
from dxConfig import dxConfig;
from fbApplyConfigSetting import fbApplyConfigSetting;
from fbInstallAsJITDebugger import fbInstallAsJITDebugger;
from fCheckPythonVersion import fCheckPythonVersion;
from fPrintApplicationKeyWordHelp import fPrintApplicationKeyWordHelp;
from fPrintExceptionInformation import fPrintExceptionInformation;
from fPrintLogo import fPrintLogo;
from fPrintUsageInformation import fPrintUsageInformation;
from fPrintVersionInformation import fPrintVersionInformation;
from mColors import *;

asTestedPythonVersions = ["2.7.14", "2.7.15", "2.7.16", "2.7.17"];

gasAttachForProcessExecutableNames = [];
gasLowercaseBinaryNamesThatAreAllowedToRunWithoutPageHeap = [
  "conhost.exe", # Used to create console windows, not part of the target application (unless the target is conhost)
];
gasReportedLowercaseBinaryNamesWithoutPageHeap = [];
gasBinaryNamesThatAreAllowedToRunWithNonIdealCdbISA = [
  # No application is known to require running processes with a non-ideal cdb ISA at this point.
];
gasReportedBinaryNameWithNonIdealCdbISA = [];
gbAnErrorOccured = False;
gbFailedToApplyMemoryLimitsErrorShown = False;
gbQuiet = False;
gbVerbose = False;
gbSaveDump = False;
gbSaveFullDump = False;
guDefaultCollateralMaximumNumberOfBugs = 5; # Just a hunch that that's a reasonable value.
guDetectedBugsCount = 0;
guMaximumNumberOfBugs = 1;
gduNumberOfRepros_by_sBugIdAndLocation = {};
gbSaveOutputWithReport = False;
gbPauseBeforeExit = False;
gbRunningAsJITDebugger = False;

def fTerminate(uExitCode):
  oConsole.fCleanup();
  if gbPauseBeforeExit:
    oConsole.fPrint("Press ENTER to quit...");
    raw_input();
  os._exit(uExitCode);

def fApplicationMaxRunTimeCallback(oBugId):
  oConsole.fPrint("+ T+%.1f The application has been running for %.1f seconds without crashing." % \
      (oBugId.fnApplicationRunTimeInSeconds(), dxConfig["nApplicationMaxRunTimeInSeconds"]));
  oConsole.fPrint();
  oConsole.fStatus(INFO, "* BugId is stopping...");
  oBugId.fStop();

def fApplicationResumedCallback(oBugId):
  oConsole.fStatus("* The application is running...");

def fApplicationRunningCallback(oBugId):
  oConsole.fStatus("* The application was started successfully and is running...");

def fApplicationSuspendedCallback(oBugId, sReason):
  oConsole.fStatus("* T+%.1f The application is suspended (%s)..." % (oBugId.fnApplicationRunTimeInSeconds(), sReason));

def fFailedToDebugApplicationCallback(oBugId, sErrorMessage):
  global gbAnErrorOccured;
  gbAnErrorOccured = True;
  oConsole.fLock();
  try:
    oConsole.fPrint(ERROR, u"\u250C\u2500", ERROR_INFO, " Failed to debug the application ", ERROR, sPadding = u"\u2500");
    for sLine in sErrorMessage.split("\n"):
      oConsole.fPrint(ERROR, u"\u2502 ", ERROR_INFO, sLine.rstrip("\r"));
    oConsole.fPrint(ERROR, u"\u2514", sPadding = u"\u2500");
    oConsole.fPrint();
  finally:
    oConsole.fUnlock();

def fInternalExceptionCallback(oBugId, oThread, oException, oTraceBack):
  global gbAnErrorOccured;
  gbAnErrorOccured = True;
  fSaveInternalExceptionReportAndExit(oException, oTraceBack);

def fSaveInternalExceptionReportAndExit(oException, oTraceBack):
  fPrintExceptionInformation(oException, oTraceBack);
  uIndex = 0;
  while True:
    uIndex += 1;
    sErrorReportFilePath = os.path.join(os.path.dirname(__file__), "BugId error report #%d.txt" % uIndex);
    if not os.path.isfile(sErrorReportFilePath):
      break;
  oConsole.fStatus("Creating a copy of the error report in %s..." % (sErrorReportFilePath,));
  oConsole.fbCopyOutputToFilePath(sErrorReportFilePath, bOverwrite = True);
  oConsole.fCleanup();
  oConsole.fPrint("A copy of the error report can be found in ", INFO, sErrorReportFilePath, NORMAL, "...");
  fTerminate(3);


def fLicenseErrorsCallback(oBugId, asErrors):
  # These should have been reported before cBugId was even instantiated, so this is kind of unexpected.
  # But rather than raise AssertionError("NOT REACHED"), we'll report the license error gracefully:
  global gbAnErrorOccured;
  gbAnErrorOccured = True;
  oConsole.fLock();
  try:
    oConsole.fPrint(ERROR, u"\u250C\u2500", ERROR_INFO, " Software license error ", ERROR, sPadding = u"\u2500");
    for sError in asErrors:
      oConsole.fPrint(ERROR, u"\u2502 ", ERROR_INFO, sError);
    oConsole.fPrint(ERROR, u"\u2514", sPadding = u"\u2500");
  finally:
    oConsole.fUnlock();
  fTerminate(5);

def fLicenseWarningsCallback(oBugId, asWarnings):
  # These were already reported when BugId started; ignore them.
  pass;
#  oConsole.fLock();
#  try:
#    oConsole.fPrint(WARNING, u"\u250C\u2500", WARNING_INFO, " Warning ", WARNING, sPadding = u"\u2500");
#    for sWarning in asWarnings:
#      oConsole.fPrint(WARNING, u"\u2502 ", WARNING_INFO, sWarning);
#    oConsole.fPrint(WARNING, u"\u2514", sPadding = u"\u2500");
#  finally:
#    oConsole.fUnlock();

def fCdbISANotIdealCallback(oBugId, oProcess, bIsMainProcess, sCdbISA, bPreventable):
  global \
      gasBinaryNamesThatAreAllowedToRunWithNonIdealCdbISA, \
      gasReportedBinaryNameWithNonIdealCdbISA, \
      gbAnErrorOccured;
  sBinaryName = oProcess.sBinaryName;
  if sBinaryName.lower() in gasBinaryNamesThatAreAllowedToRunWithNonIdealCdbISA:
    return;
  if not bPreventable:
    if not gbQuiet and sBinaryName not in gasReportedBinaryNameWithNonIdealCdbISA:
      gasReportedBinaryNameWithNonIdealCdbISA.append(sBinaryName);
      oConsole.fLock();
      try:
        oConsole.fPrint(
          WARNING, "- You are debugging an ",
          WARNING_INFO, oProcess.sISA, WARNING, " process running ",
          WARNING_INFO, sBinaryName, WARNING, " with a ",
          WARNING_INFO, sCdbISA, WARNING, " cdb.exe."
        );
        oConsole.fPrint("  This appears to be due to the application running both x86 and x64 processes.");
        oConsole.fPrint("  Unfortunately, this means use-after-free bugs in this process may be reported");
        oConsole.fPrint("  as attempts to access reserved memory regions, which is tecnically true but");
        oConsole.fPrint("  not as accurate as you might expect.");
        oConsole.fPrint();
      finally:
        oConsole.fUnlock();
  else:
    gbAnErrorOccured = True;
    oConsole.fLock();
    try:
      oConsole.fPrint(
        ERROR, "- You are debugging an ",
        ERROR_INFO, oProcess.sISA, WARNING, " process running ",
        ERROR_INFO, sBinaryName, WARNING, " with a ",
        ERROR_INFO, sCdbISA, WARNING, " cdb.exe."
      );
      oConsole.fPrint(
        "  You should use the ", INFO, "--isa=", oProcess.sISA, NORMAL, " command line argument to let BugId know",
        "it should be using a ", oProcess.sISA, " cdb.exe.");
      oConsole.fPrint("  Please restart BugId with the aboce command line argument to try again.");
      oConsole.fPrint();
      oConsole.fStatus(INFO, "* BugId is stopping...");
    finally:
      oConsole.fUnlock();
    # There is no reason to run without page heap, so terminated.
    oBugId.fStop();
    # If you really want to run without page heap, set `dxConfig["cBugId"]["bEnsurePageHeap"]` to `False` in
    # `dxConfig.py`or run with the command-line siwtch `--cBugId.bEnsurePageHeap=false`
  
def fPageHeapNotEnabledCallback(oBugId, oProcess, bIsMainProcess, bPreventable):
  global \
      gasLowercaseBinaryNamesThatAreAllowedToRunWithoutPageHeap, \
      gasReportedLowercaseBinaryNamesWithoutPageHeap, \
      gbAnErrorOccured;
  sLowerBinaryName = oProcess.sBinaryName.lower();
  if (
    gbQuiet
    or sLowerBinaryName in gasLowercaseBinaryNamesThatAreAllowedToRunWithoutPageHeap
    or sLowerBinaryName in gasReportedLowercaseBinaryNamesWithoutPageHeap 
  ):
    return;
  gasReportedLowercaseBinaryNamesWithoutPageHeap.append(sLowerBinaryName);
  oConsole.fLock();
  try:
    oConsole.fPrint(WARNING, "- Full page heap is not enabled for ", WARNING_INFO, oProcess.sBinaryName,
                    WARNING, " in process ", WARNING_INFO, "0x%X" % oProcess.uId, WARNING, ".");
    if bPreventable:
      oConsole.fPrint("  Without page heap enabled, detection and anaylsis of any bugs will be sub-");
      oConsole.fPrint("  optimal. Please enable page heap to improve detection and analysis.");
      oConsole.fPrint();
      oConsole.fPrint("  You can enabled full page heap for ", sLowerBinaryName, " by running:");
      oConsole.fPrint();
      oConsole.fPrint("      ", INFO, 'PageHeap.cmd "', oProcess.sBinaryName, '" ON');
    else:
      oConsole.fPrint("  This appears to be due to a bug in page heap that prevents it from");
      oConsole.fPrint("  determining the binary name correctly. Unfortunately, there is no known fix");
      oConsole.fPrint("  or work-around for this. BugId will continue, but detection and analysis of");
      oConsole.fPrint("  any bugs in this process will be sub-optimal.");
    oConsole.fPrint();
  finally:
    oConsole.fUnlock();

def fCdbStdInInputCallback(oBugId, sInput):
  oConsole.fPrint(HILITE, "<stdin<", NORMAL, sInput, uConvertTabsToSpaces = 8);
def fCdbStdOutOutputCallback(oBugId, sOutput):
  oConsole.fPrint(HILITE, "stdout>", NORMAL, sOutput, uConvertTabsToSpaces = 8);
def fCdbStdErrOutputCallback(oBugId, sOutput):
  oConsole.fPrint(ERROR_INFO, "stderr>", ERROR, sOutput, uConvertTabsToSpaces = 8);
def fLogMessageCallback(oBugId, sMessage, dsData = None):
  sData = dsData and ", ".join(["%s: %s" % (sName, sValue) for (sName, sValue) in dsData.items()]);
  oConsole.fPrint(DIM, "log>%s%s" % (sMessage, sData and " (%s)" % sData or ""));

# Helper function to format messages that are specific to a process.
def fPrintMessageForProcess(sHeaderChar, oProcess, bIsMainProcess, *asMessage):
  # oProcess is a mWindowsAPI.cProcess or derivative.
  if sHeaderChar is None:
    # Just blanks for the header (used for multi-line output to reduce redundant output).
    oConsole.fPrint(
      " ", " ", bIsMainProcess and "    " or "   ", "         ",
      " " * len("%d" % oProcess.uId), " ", " " * len("0x%X" % oProcess.uId),
      "  ", " " * len(oProcess.sBinaryName), "   ",
      *asMessage,
      uConvertTabsToSpaces = 8
    );
  else:
    oConsole.fPrint(
      sHeaderChar, " ", bIsMainProcess and "Main" or "Sub", " process ",
      INFO, "%d" % oProcess.uId, NORMAL, "/", INFO , "0x%X" % oProcess.uId, NORMAL,
      " (", INFO, oProcess.sBinaryName, NORMAL, "): ",
      *asMessage,
      uConvertTabsToSpaces = 8
    );

def fFailedToApplyApplicationMemoryLimitsCallback(oBugId, oProcess, bIsMainProcess):
  global gbFailedToApplyMemoryLimitsErrorShown, gbQuiet, gbVerbose;
  if not gbQuiet:
    fPrintMessageForProcess("-", oProcess, bIsMainProcess,
        ERROR_INFO, "Cannot apply application memory limits");
    gbFailedToApplyMemoryLimitsErrorShown = True;
    if not gbVerbose:
      oConsole.fPrint("  Any additional failures to apply memory limits to processess will not be shown.");
def fFailedToApplyProcessMemoryLimitsCallback(oBugId, oProcess, bIsMainProcess):
  global gbFailedToApplyMemoryLimitsErrorShown, gbVerbose;
  if gbVerbose or not gbFailedToApplyMemoryLimitsErrorShown:
    fPrintMessageForProcess("-", oProcess, bIsMainProcess,
        ERROR_INFO, "Cannot apply process memory limits");
    gbFailedToApplyMemoryLimitsErrorShown = True;
    if not gbVerbose:
      oConsole.fPrint("  Any additional failures to apply memory limits to processess will not be shown.");

def fProcessStartedCallback(oBugId, oConsoleProcess, bIsMainProcess):
  if gbVerbose:
    fPrintMessageForProcess("+", oConsoleProcess, bIsMainProcess,
      "Started", "; command line = ", INFO, oConsoleProcess.sCommandLine, NORMAL, "."
    );
def fProcessAttachedCallback(oBugId, oProcess, bIsMainProcess):
  global gasAttachForProcessExecutableNames;
  if not gbQuiet: # Main processes
    fPrintMessageForProcess("+", oProcess, bIsMainProcess,
      "Attached", "; command line = ", INFO, oProcess.sCommandLine or "<unknown>", NORMAL, "."
    );
  # Now is a good time to look for additional binaries that may need to be debugged as well.
  if gasAttachForProcessExecutableNames:
    oBugId.fAttachForProcessExecutableNames(*gasAttachForProcessExecutableNames);

def fApplicationDebugOutputCallback(oBugId, oProcess, bIsMainProcess, asMessages):
  uCount = 0;
  sDebug = "debug";
  oConsole.fLock();
  for sMessage in asMessages:
    uCount += 1;
    if uCount == 1:
      sHeader = "*";
      # we will create a box shape to show which messages belong together.
      # On the first line we will branch down and right if the message is multi-line.
      sPrefix = " " if len(asMessages) == 1 else u"\u252c";
    else:
      sHeader = None;
      # if more lines folow, show a vertical stripe, otherwise bend right on the last line
      sPrefix = u"\u2514" if uCount == len(asMessages) else u"\u2502";
    fPrintMessageForProcess(sHeader, oProcess, bIsMainProcess,
      INFO, sDebug, NORMAL, sPrefix, HILITE, sMessage,
    );
    sDebug = "     ";
  oConsole.fUnlock();

def fApplicationStdOutOutputCallback(oBugId, oConsoleProcess, bIsMainProcess, sMessage):
  fPrintMessageForProcess("*", oConsoleProcess, bIsMainProcess,
    INFO, "stdout", NORMAL, ">", HILITE, sMessage,
  );
def fApplicationStdErrOutputCallback(oBugId, oConsoleProcess, bIsMainProcess, sMessage):
  fPrintMessageForProcess("*", oConsoleProcess, bIsMainProcess,
    ERROR, "stderr", NORMAL, ">", ERROR_INFO, sMessage,
  );

def fProcessTerminatedCallback(oBugId, oProcess, bIsMainProcess):
  bStopBugId = bIsMainProcess and dxConfig["bApplicationTerminatesWithMainProcess"];
  if not gbQuiet:
    fPrintMessageForProcess("-", oProcess, bIsMainProcess,
      "Terminated", bStopBugId and "; the application is considered to have terminated with it." or ".",
    );
  if bStopBugId:
    oConsole.fStatus(INFO, "* BugId is stopping because a main process terminated...");
    oBugId.fStop();

def fBugReportCallback(oBugId, oBugReport):
  global guDetectedBugsCount, \
         guMaximumNumberOfBugs, \
         gduNumberOfRepros_by_sBugIdAndLocation;
  guDetectedBugsCount += 1;
  oConsole.fLock();
  try:
    oConsole.fPrint(u"\u250C\u2500 ", HILITE, "A bug was detected ", NORMAL, sPadding = u"\u2500");
    if oBugReport.sBugLocation:
      oConsole.fPrint(u"\u2502 Id @ Location:    ", INFO, oBugReport.sId, NORMAL, " @ ", INFO, oBugReport.sBugLocation);
      sBugIdAndLocation = "%s @ %s" % (oBugReport.sId, oBugReport.sBugLocation);
    else:
      oConsole.fPrint(u"\u2502 Id:               ", INFO, oBugReport.sId);
      sBugIdAndLocation = oBugReport.sId;
    gduNumberOfRepros_by_sBugIdAndLocation.setdefault(sBugIdAndLocation, 0);
    gduNumberOfRepros_by_sBugIdAndLocation[sBugIdAndLocation] += 1;
    if oBugReport.sBugSourceLocation:
      oConsole.fPrint(u"\u2502 Source:           ", INFO, oBugReport.sBugSourceLocation);
    oConsole.fPrint(u"\u2502 Description:      ", INFO, oBugReport.sBugDescription);
    oConsole.fPrint(u"\u2502 Security impact:  ", INFO, (oBugReport.sSecurityImpact or "None"));
    oConsole.fPrint(u"\u2502 Version:          ", NORMAL, oBugReport.asVersionInformation[0]); # The process' binary.
    for sVersionInformation in oBugReport.asVersionInformation[1:]: # There may be two if the crash was in a
      oConsole.fPrint(u"\u2502                   ", NORMAL, sVersionInformation); # different binary (e.g. a .dll)
    if dxConfig["bGenerateReportHTML"]:
      # Use a report file name base on the BugId.
      sDesiredReportFileName = "%s" % sBugIdAndLocation;
      # In collateral mode, we will number the reports so you know in which order bugs were reported.
      if guMaximumNumberOfBugs > 1:
        sDesiredReportFileName = "#%d %s" % (guDetectedBugsCount, sDesiredReportFileName);
      # Translate characters that are not valid in file names.
      suValidReportFileName = mFileSystem2.fsGetValidName(sDesiredReportFileName, bUnicode = \
          dxConfig["bUseUnicodeReportFileNames"]);
      if dxConfig["sReportFolderPath"] is not None:
        suReportFilePath = os.path.join(dxConfig["sReportFolderPath"], suValidReportFileName + ".html");
      else:
        suReportFilePath = suValidReportFileName + ".html";
      oReportFile = None;
      oConsole.fStatus(u"\u2502 Bug report:       ", INFO, suValidReportFileName, ".html", NORMAL, "...");
      try:
        oReportFile = mFileSystem2.foGetOrCreateFile(suReportFilePath);
        oReportFile.fWrite(oBugReport.sReportHTML);
      except Exception as oException:
        oConsole.fPrint(u"\u2502 ", ERROR, "Bug report:       ", ERROR_INFO, suValidReportFileName, ".html", ERROR, " not saved!");
        oConsole.fPrint(u"\u2502   Error:          ", ERROR_INFO, str(oException));
      else:
        oConsole.fPrint(u"\u2502 Bug report:       ", INFO, suValidReportFileName, ".html", NORMAL, ".");
      if oReportFile:
        oReportFile.fClose();
      if gbSaveOutputWithReport:
        if dxConfig["sReportFolderPath"] is not None:
          suLogOutputFilePath = os.path.join(dxConfig["sReportFolderPath"], suValidReportFileName + " BugId output.txt");
        else:
          suLogOutputFilePath = suValidReportFileName + " BugId output.txt";
        oConsole.fStatus(u"\u2502 BugId output log: ", INFO, suValidReportFileName, ".txt", NORMAL, "...");
        try:
          oConsole.fbCopyOutputToFilePath(suLogOutputFilePath);
        except Exception as oException:
          oConsole.fCleanup();
          oConsole.fPrint(u"\u2502 BugId output log: ", ERROR_INFO, suValidReportFileName, ".txt", ERROR, " not saved!");
          oConsole.fPrint(u"\u2502   Error:          ", ERROR_INFO, str(oException));
        else:
          oConsole.fPrint(u"\u2502 BugId output log: ", INFO, suValidReportFileName, ".txt", NORMAL, ".");
      if gbSaveDump:
        if dxConfig["sReportFolderPath"] is not None:
          suDumpFilePath = os.path.join(dxConfig["sReportFolderPath"], suValidReportFileName + ".dmp");
        else:
          suDumpFilePath = suValidReportFileName + ".dmp";
        sDumpFilePath = unicode(suDumpFilePath).encode("ascii", 'replace').replace("?", ".");
        oConsole.fStatus(u"\u2502 Dump file:        ", INFO, suValidReportFileName, ".dmp", NORMAL, "...");
        oBugId.fSaveDumpToFile(sDumpFilePath, True, gbSaveFullDump);
        oConsole.fPrint(u"\u2502 Dump file:        ", INFO, suValidReportFileName, ".dmp", NORMAL, ".");
    oConsole.fPrint(u"\u2514", sPadding = u"\u2500");
  finally:
    oConsole.fUnlock();

def fMain(asArguments):
  global \
      gasAttachForProcessExecutableNames, \
      gasLowercaseBinaryNamesThatAreAllowedToRunWithoutPageHeap, \
      gbQuiet, \
      gbVerbose, \
      gbSaveDump, \
      gbSaveFullDump, \
      guDetectedBugsCount, \
      guMaximumNumberOfBugs, \
      gbSaveOutputWithReport, \
      gbPauseBeforeExit;
  
  # Make sure Windows and the Python binary are up to date; we don't want our users to unknowingly run outdated
  # software as this is likely to cause unexpected issues.
  fCheckPythonVersion("BugId", asTestedPythonVersions, "https://github.com/SkyLined/BugId/issues/new")
  if mWindowsAPI.oSystemInfo.sOSVersion != "10.0":
    oConsole.fPrint(ERROR, "Error: unfortunately BugId only runs on Windows 10 at this time.");
    fTerminate(3);
  if mWindowsAPI.oSystemInfo.sOSISA == "x64" and mWindowsAPI.fsGetPythonISA() == "x86":
    oConsole.fLock();
    try:
      oConsole.fPrint(WARNING, u"\u250C\u2500", WARNING_INFO, " Warning ", WARNING, sPadding = u"\u2500");
      oConsole.fPrint(WARNING, u"\u2502 You are running a ", WARNING_INFO, "32-bit", WARNING, " version of Python on a ",
          WARNING_INFO, "64-bit", WARNING, " version of Windows.");
      oConsole.fPrint(WARNING, u"\u2502 BugId will not be able to debug 64-bit applications unless you run it in a 64-bit " +
          "version of Python.");
      oConsole.fPrint(WARNING, u"\u2502 If you experience any issues, use a 64-bit version of Python and try again.");
      oConsole.fPrint(WARNING, u"\u2514", sPadding = u"\u2500");
    finally:
      oConsole.fUnlock();
  
  # Show usage information if no arguments are provided:
  if len(asArguments) == 0:
    fPrintLogo();
    fPrintUsageInformation(ddxApplicationSettings_by_sKeyword.keys());
    fTerminate(0);
  
  # Parse all arguments until we encounter "--".
  sApplicationKeyword = None;
  sApplicationBinaryPath = None;
  auApplicationProcessIds = [];
  u0JITDebuggerEventId = None;
  oUWPApplication = None;
  asApplicationOptionalArguments = None;
  sApplicationISA = None;
  bRepeat = False;
  uNumberOfRepeats = None;
  bCheckForUpdates = False;
  dxUserProvidedConfigSettings = {};
  asAdditionalLocalSymbolPaths = [];
  bFast = False;
  bInstallAsJITDebugger = True;
  while asArguments:
    sArgument = asArguments.pop(0);
    if sArgument == "--":
      if len(auApplicationProcessIds) > 0:
      # The rest of the arguments are to be passed to the application
        oConsole.fPrint(ERROR, "- You cannot provide process ids and application arguments.");
        fTerminate(2);
      asApplicationOptionalArguments = asArguments;
      break;
    elif sArgument in ["-q", "/q", "-Q", "/Q"]:
      gbQuiet = True;
    elif sArgument in ["-v", "/v", "-V", "/V"]:
      gbVerbose = True;
    elif sArgument in ["-f", "/f", "-F", "/F"]:
      bFast = True;
    elif sArgument in ["-r", "/r", "-R", "/R"]:
      bRepeat = True;
    elif sArgument in ["-d", "/d", "-D", "/D"]:
      gbSaveDump = True;
    elif sArgument in ["-p", "/p", "-P", "/P"]:
      gbPauseBeforeExit = True;
    elif sArgument in ["-i", "/i", "-I", "/I"]:
      # Install as JIT Debugger. Remaining arguments are passed on the command line to the JIT debugger.
      if fbInstallAsJITDebugger(asArguments):
        fTerminate(0);
      fTerminate(3);
    elif sArgument in ["-c", "/c", "-C", "/C"]:
      guMaximumNumberOfBugs = guDefaultCollateralMaximumNumberOfBugs;
    elif sArgument in ["-h", "/h", "-H", "/H", "-?", "/?"]:
      fPrintLogo();
      fPrintUsageInformation(ddxApplicationSettings_by_sKeyword.keys());
      fTerminate(0);
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
          fTerminate(2);
        if sApplicationBinaryPath is not None:
          oConsole.fPrint(ERROR, "- You cannot provide an application binary and process ids.");
          fTerminate(2);
        if oUWPApplication is not None:
          oConsole.fPrint(ERROR, "- You cannot provide UWP application details and process ids.");
          fTerminate(2);
        auApplicationProcessIds += [long(x) for x in sValue.split(",")];
      elif sSettingName == "handle-jit-event":
        if not sValue:
          oConsole.fPrint(ERROR, "- No event handle provided!");
          fTerminate(2);
        u0JITDebuggerEventId = long(sValue);
      elif sSettingName in ["uwp", "uwp-app"]:
        if not sValue:
          oConsole.fPrint(ERROR, "- You must provide UWP application details.");
          fTerminate(2);
        if oUWPApplication is not None:
          oConsole.fPrint(ERROR, "- You cannot provide UWP application details more than once.");
          fTerminate(2);
        if sApplicationBinaryPath is not None:
          oConsole.fPrint(ERROR, "- You cannot provide an application binary and UWP application details.");
          fTerminate(2);
        if len(auApplicationProcessIds) > 0:
          oConsole.fPrint(ERROR, "- You cannot provide process ids and UWP application details.");
          fTerminate(2);
        tsUWPApplicationPackageNameAndId = sValue.split("!", 1);
        sUWPApplicationPackageName = tsUWPApplicationPackageNameAndId[0];
        sUWPApplicationId = tsUWPApplicationPackageNameAndId[1] if len(tsUWPApplicationPackageNameAndId) == 2 else None;
        oUWPApplication = mWindowsAPI.cUWPApplication(sUWPApplicationPackageName, sUWPApplicationId);
      elif sSettingName in ["help"]:
        fPrintLogo();
        fPrintUsageInformation(ddxApplicationSettings_by_sKeyword.keys());
        fTerminate(0);
      elif sSettingName in ["version", "check-for-updates"]:
        fPrintVersionInformation(
          bCheckForUpdates = True,
          bCheckAndShowLicenses = True,
          bShowInstallationFolders = True,
        );
        fTerminate(0);
      elif sSettingName in ["log-output"]:
        gbSaveOutputWithReport = True;
      elif sSettingName in ["isa", "cpu"]:
        if not sValue:
          oConsole.fPrint(ERROR, "- You must provide an Instruction Set Architecture.");
          fTerminate(2);
        if sValue not in ["x86", "x64"]:
          oConsole.fPrint(ERROR, "- Unknown Instruction Set Architecture ", repr(sValue));
          fTerminate(2);
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
      elif sSettingName in ["dump"]:
        if sValue is None or sValue.lower() == "true":
          gbSaveDump = True;
        elif sValue.lower() == "false":
          gbSaveDump = False;
        else:
          oConsole.fPrint(ERROR, "- The value for ", ERROR_INFO, "--", sSettingName, ERROR, \
              " must be \"true\" or \"false\".");
      elif sSettingName in ["full-dump"]:
        if sValue is None or sValue.lower() == "true":
          gbSaveDump = True; # Saving a full dumps means saving a dump.
          gbSaveFullDump = True;
        elif sValue.lower() == "false":
          gbSaveFullDump = False;
        else:
          oConsole.fPrint(ERROR, "- The value for ", ERROR_INFO, "--", sSettingName, ERROR, \
              " must be \"true\" or \"false\".");
      elif sSettingName in ["forever"]:
        if sValue is None or sValue.lower() == "true":
          bRepeat = True;
        elif sValue.lower() == "false":
          bRepeat = False;
        else:
          oConsole.fPrint(ERROR, "- The value for ", ERROR_INFO, "--", sSettingName, ERROR, \
              " must be \"true\" or \"false\".");
      elif sSettingName in ["repeat"]:
        bRepeat = sValue is None or sValue.lower() != "false";
        if bRepeat and sValue is not None:
          try:
            uNumberOfRepeats = long(sValue);
            if uNumberOfRepeats < 2:
              uNumberOfRepeats = None;
            elif str(uNumberOfRepeats) != sValue:
              uNumberOfRepeats = None;
          except:
            pass;
          if uNumberOfRepeats is None:
            oConsole.fPrint(ERROR, "- The value for ", ERROR_INFO, "--", sSettingName, ERROR, \
                " must be an integer larger than 1 or \"false\".");
      elif sSettingName == "pause":
        gbPauseBeforeExit = True;
      elif sSettingName in ["collateral"]:
        if sValue is None:
          guMaximumNumberOfBugs = guDefaultCollateralMaximumNumberOfBugs;
        else:
          # -- collateral=1 means one collateral bug in addition to the first bug.
          guMaximumNumberOfBugs = long(sValue) + 1;
      elif sSettingName in ["symbols"]:
        if sValue is None or not mFileSystem2.foGetFolder(sValue):
          oConsole.fPrint(ERROR, "- The value for ", ERROR_INFO, "--", sSettingName, ERROR, \
              " must be a valid folder path.");
        asAdditionalLocalSymbolPaths.append(sValue);
      elif sSettingName in ["report", "reports", "report-folder", "reports-folder", "report-folder-path", "reports-folder-path"]:
        if sValue is None or not mFileSystem2.foGetFolder(sValue):
          oConsole.fPrint(ERROR, "- The value for ", ERROR_INFO, "--", sSettingName, ERROR, \
              " must be a valid folder path.");
        dxConfig["sReportFolderPath"] = sValue;
      elif sSettingName in ["test-internal-error", "internal-error-test"]:
        raise Exception("Testing internal error");
      else:
        if not sValue:
          oConsole.fPrint(ERROR, "- You cannot provide an argument (", ERROR_INFO, "--", sSettingName, ERROR, \
              ") without a value.");
          fTerminate(2);
        try:
          xValue = json.loads(sValue);
        except ValueError as oError:
          oConsole.fPrint(ERROR, "- Cannot decode argument JSON value --", ERROR_INFO, sSettingName, ERROR, "=", \
              ERROR_INFO, sValue, ERROR, ": ", ERROR_INFO, " ".join(oError.args), ERROR, ".");
          fTerminate(2);
        # User provided config settings must be applied after any keyword specific config settings:
        dxUserProvidedConfigSettings[sSettingName] = xValue;
    elif sArgument in ddxApplicationSettings_by_sKeyword:
      if sApplicationKeyword is not None:
        oConsole.fPrint(ERROR, "- You cannot provide multiple application keywords.");
        fTerminate(2);
      sApplicationKeyword = sArgument;
    elif len(sArgument) > 0 and sArgument[-1] == "?":
      sApplicationKeyword = sArgument[:-1];
      dxApplicationSettings = ddxApplicationSettings_by_sKeyword.get(sApplicationKeyword);
      if not dxApplicationSettings:
        oConsole.fPrint(ERROR, "- Unknown application keyword ", ERROR_INFO, sApplicationKeyword, ERROR, ".");
        fTerminate(2);
      fPrintApplicationKeyWordHelp(sApplicationKeyword, dxApplicationSettings);
      fTerminate(0);
    else:
      if sApplicationBinaryPath is not None:
        oConsole.fLock();
        try:
          oConsole.fPrint(ERROR, "- You cannot provide multiple application binaries.");
          oConsole.fPrint(ERROR, "  (Did you perhaps forget to put ", ERROR_INFO, "--", ERROR, \
              " before the start of the application arguments?)");
        finally:
          oConsole.fUnlock();
        fTerminate(2);
      if len(auApplicationProcessIds) > 0:
        oConsole.fPrint(ERROR, "- You cannot provide process ids and an application binary.");
        fTerminate(2);
      if oUWPApplication is not None:
        oConsole.fPrint(ERROR, "- You cannot provide an application UWP package name and a binary.");
        fTerminate(2);
      if len(sArgument) == 0:
        oConsole.fPrint(ERROR, "- You cannot provide an empty string as the application binary path.");
        fTerminate(2);
      sApplicationBinaryPath = sArgument;
  
  if bFast:
    gbQuiet = True;
    dxUserProvidedConfigSettings["bGenerateReportHTML"] = False;
    dxUserProvidedConfigSettings["asSymbolServerURLs"] = [];
    dxUserProvidedConfigSettings["cBugId.bUse_NT_SYMBOL_PATH"] = False;
  
  dsApplicationURLTemplate_by_srSourceFilePath = {};
  
  if gbSaveOutputWithReport:
    oConsole.fEnableLog();
  
  fSetup = None; # Function specific to a keyword application, used to setup stuff before running.
  fCleanup = None; # Function specific to a keyword application, used to cleanup stuff before & after running.
  if sApplicationKeyword:
    dxApplicationSettings = ddxApplicationSettings_by_sKeyword.get(sApplicationKeyword);
    if not dxApplicationSettings:
      oConsole.fPrint(ERROR, "- Unknown application keyword ", ERROR_INFO, sApplicationKeyword, ERROR, ".");
      fTerminate(2);
    fSetup = dxApplicationSettings.get("fSetup");
    fCleanup = dxConfig["bCleanup"] and dxApplicationSettings.get("fCleanup");
    # Get application binary/UWP package name/process ids as needed:
    if "sBinaryPath" in dxApplicationSettings:
      # This application is started from the command-line.
      if auApplicationProcessIds:
        oConsole.fPrint(ERROR, "- You cannot provide process ids for application keyword ", ERROR_INFO, \
            sApplicationKeyword, ERROR, ".");
        fTerminate(2);
      if oUWPApplication:
        oConsole.fPrint(ERROR, "- You cannot provide an application UWP package name for application keyword ", \
            ERROR_INFO, sApplicationKeyword, ERROR, ".");
        fTerminate(2);
      if sApplicationBinaryPath is None:
        sApplicationBinaryPath = dxApplicationSettings["sBinaryPath"];
        if sApplicationBinaryPath is None:
          oConsole.fPrint(ERROR, "- The main application binary for ", ERROR_INFO, sApplicationKeyword, \
              ERROR, " could not be detected on your system.");
          oConsole.fPrint(ERROR, "  Please provide the path to this binary in the arguments.");
          fTerminate(4);
    elif "dxUWPApplication" in dxApplicationSettings:
      dxUWPApplication = dxApplicationSettings["dxUWPApplication"];
      # This application is started as a Universal Windows Platform application.
      if sApplicationBinaryPath:
        oConsole.fPrint(ERROR, "- You cannot provide an application binary for application keyword ", \
            ERROR_INFO, sApplicationKeyword, ERROR, ".");
        fTerminate(2);
      if auApplicationProcessIds:
        oConsole.fPrint(ERROR, "- You cannot provide process ids for application keyword ", ERROR_INFO, \
            sApplicationKeyword, ERROR, ".");
        fTerminate(2);
      sUWPApplicationPackageName = dxUWPApplication["sPackageName"];
      sUWPApplicationId = dxUWPApplication["sId"];
      oUWPApplication = mWindowsAPI.cUWPApplication(sUWPApplicationPackageName, sUWPApplicationId);
    elif not auApplicationProcessIds:
      # This application is attached to.
      oConsole.fPrint(ERROR, "- You must provide process ids for application keyword ", \
          ERROR_INFO, sApplicationKeyword, ERROR, ".");
      fTerminate(2);
    elif asApplicationOptionalArguments:
      # Cannot provide arguments if we're attaching to processes
      oConsole.fPrint(ERROR, "- You cannot provide arguments for application keyword ", \
          ERROR_INFO, sApplicationKeyword, ERROR, ".");
      fTerminate(2);
    if "asApplicationAttachForProcessExecutableNames" in dxApplicationSettings:
      gasAttachForProcessExecutableNames = dxApplicationSettings["asApplicationAttachForProcessExecutableNames"];
    # Get application arguments;
    if "fasGetStaticArguments" in dxApplicationSettings:
      fasGetApplicationStaticArguments = dxApplicationSettings["fasGetStaticArguments"];
      asApplicationStaticArguments = fasGetApplicationStaticArguments(bForHelp = False);
    else:
      asApplicationStaticArguments = [];
    if asApplicationOptionalArguments is None and "fasGetOptionalArguments" in dxApplicationSettings:
      fasGetApplicationOptionalArguments = dxApplicationSettings["fasGetOptionalArguments"];
      asApplicationOptionalArguments = fasGetApplicationOptionalArguments(bForHelp = False);
    asApplicationArguments = asApplicationStaticArguments + asApplicationOptionalArguments;
    # Apply application specific settings
    if dxApplicationSettings.get("dxConfigSettings"):
      dxApplicationConfigSettings = dxApplicationSettings["dxConfigSettings"];
      if gbVerbose:
        oConsole.fPrint("* Applying application specific configuration for %s:" % sApplicationKeyword);
      for (sSettingName, xValue) in dxApplicationConfigSettings.items():
        if sSettingName not in dxUserProvidedConfigSettings:
          # Apply and show result indented or errors.
          if not fbApplyConfigSetting(sSettingName, xValue, [None, "  "][gbVerbose]):
            fTerminate(2);
      if gbVerbose:
        oConsole.fPrint();
    # Apply application specific source settings
    if "dsURLTemplate_by_srSourceFilePath" in dxApplicationSettings:
      dsApplicationURLTemplate_by_srSourceFilePath = dxApplicationSettings["dsURLTemplate_by_srSourceFilePath"];
    # If not ISA is specified, apply the application specific ISA (if any).
    if not sApplicationISA and "sISA" in dxApplicationSettings:
      sApplicationISA = dxApplicationSettings["sISA"];
    if "asBinaryNamesThatAreAllowedToRunWithoutPageHeap" in dxApplicationSettings:
      gasLowercaseBinaryNamesThatAreAllowedToRunWithoutPageHeap += [
        sBinaryName.lower() for sBinaryName in dxApplicationSettings["asBinaryNamesThatAreAllowedToRunWithoutPageHeap"]
      ];
  elif (auApplicationProcessIds or oUWPApplication or sApplicationBinaryPath):
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
    fTerminate(2);
  
  # Check that the UWP application exists if needed.
  if oUWPApplication:
    if not oUWPApplication.bPackageExists:
      oConsole.fPrint(ERROR, "- UWP application package ", ERROR_INFO, oUWPApplication.sPackageName,
          ERROR, " does not exist.");
      fTerminate(2);
    elif not oUWPApplication.bIdExists:
      oConsole.fPrint(ERROR, "- UWP application package ", ERROR_INFO, oUWPApplication.sPackageName,
          ERROR, " does not contain an application with id ", ERROR_INFO, oUWPApplication.sApplicationId,
          ERROR, ".");
      fTerminate(2);
  # Apply user provided settings:
  for (sSettingName, xValue) in dxUserProvidedConfigSettings.items():
    # Apply and show result or errors:
    if not fbApplyConfigSetting(sSettingName, xValue, [None, ""][gbVerbose]):
      fTerminate(2);
  
  # Check if cdb.exe is found:
  sCdbISA = sApplicationISA or cBugId.sOSISA;
  if not cBugId.fbCdbFound(sCdbISA):
    oConsole.fLock();
    try:
      oConsole.fPrint(ERROR, "- BugId depends on ", ERROR_INFO, "Debugging Tools for Windows", ERROR, " which was not found.");
      oConsole.fPrint();
      oConsole.fPrint("To install, download the Windows 10 SDK installer at:");
      oConsole.fPrint();
      oConsole.fPrint("  ", INFO, "https://developer.microsoft.com/en-US/windows/downloads/windows-10-sdk");
      oConsole.fPrint();
      oConsole.fPrint("After downloading, run the installer. You can deselect all other features");
      oConsole.fPrint("of the SDK before installation; only ", INFO, "Debugging Tools for Windows", NORMAL, " is required.");
      oConsole.fPrint();
      oConsole.fPrint("Once you have completed these steps, please try again.");
    finally:
      oConsole.fUnlock();
    fTerminate(2);
  
  # Check license
  (asLicenseErrors, asLicenseWarnings) = mProductDetails.ftasGetLicenseErrorsAndWarnings();
  if asLicenseErrors:
    oConsole.fLock();
    try:
      oConsole.fPrint(ERROR, u"\u250C\u2500", ERROR_INFO, " Software license error ", ERROR, sPadding = u"\u2500");
      for sLicenseError in asLicenseErrors:
        oConsole.fPrint(ERROR, u"\u2502 ", ERROR_INFO, sLicenseError);
      oConsole.fPrint(ERROR, u"\u2514", sPadding = u"\u2500");
    finally:
      oConsole.fUnlock();
    fTerminate(5);
  if asLicenseWarnings:
    oConsole.fLock();
    try:
      oConsole.fPrint(WARNING, u"\u250C\u2500", WARNING_INFO, " Software license warning ", WARNING, sPadding = u"\u2500");
      for sLicenseWarning in asLicenseWarnings:
        oConsole.fPrint(WARNING, u"\u2502 ", WARNING_INFO, sLicenseWarning);
      oConsole.fPrint(WARNING, u"\u2514", sPadding = u"\u2500");
    finally:
      oConsole.fUnlock();
  
  if bRepeat:
    sValidStatisticsFileName = mFileSystem2.fsGetValidName("Reproduction statistics.txt");
  asLocalSymbolPaths = dxConfig["asLocalSymbolPaths"] or [];
  if asAdditionalLocalSymbolPaths:
    asLocalSymbolPaths += asAdditionalLocalSymbolPaths;
  uRunCounter = 0;
  while 1: # Will only loop if bRepeat is True
    nStartTimeInSeconds = time.clock();
    if fSetup:
      # Call setup before the application is started. Argument is boolean value indicating if this is the first time
      # the function is being called.
      oConsole.fStatus("* Applying special application configuration settings...");
      fSetup(bFirstRun = uRunCounter == 0);
    uRunCounter += 1;
    oBugId = cBugId(
      sCdbISA = sCdbISA,
      sApplicationBinaryPath = sApplicationBinaryPath or None,
      auApplicationProcessIds = auApplicationProcessIds or None,
      u0JITDebuggerEventId = u0JITDebuggerEventId,
      oUWPApplication = oUWPApplication,
      asApplicationArguments = asApplicationArguments,
      asLocalSymbolPaths = asLocalSymbolPaths or None,
      asSymbolCachePaths = dxConfig["asSymbolCachePaths"], 
      asSymbolServerURLs = dxConfig["asSymbolServerURLs"],
      dsURLTemplate_by_srSourceFilePath = dsApplicationURLTemplate_by_srSourceFilePath,
      bGenerateReportHTML = dxConfig["bGenerateReportHTML"],
      uProcessMaxMemoryUse = dxConfig["uProcessMaxMemoryUse"],
      uTotalMaxMemoryUse = dxConfig["uTotalMaxMemoryUse"],
      uMaximumNumberOfBugs = guMaximumNumberOfBugs,
    );
    oConsole.fLock();
    try:
      if sApplicationBinaryPath:
        # make the binary path absolute because relative paths don't work.
        sApplicationBinaryPath = os.path.abspath(sApplicationBinaryPath);
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
        if oUWPApplication and not gbQuiet:
          oConsole.fPrint(*(
            ["* UWP application id: ", INFO, oBugId.oUWPApplication.sApplicationId, NORMAL] +
            [", package name: ", INFO, oBugId.oUWPApplication.sPackageName, NORMAL] +
            ([", Arguments: ", INFO, " ".join(asApplicationArguments), NORMAL] if asApplicationArguments else []) +
            ["."]
          ));
        if not oUWPApplication:
          oConsole.fStatus("* The debugger is attaching to running processes of the application...");
        elif auApplicationProcessIds:
          oConsole.fStatus("* The debugger is attaching to running processes and starting the application...");
        else:
          oConsole.fStatus("* The debugger is starting the application...");
    finally:
      oConsole.fUnlock();
    oBugId.fAddCallback("Application resumed", fApplicationResumedCallback);
    oBugId.fAddCallback("Application running", fApplicationRunningCallback);
    oBugId.fAddCallback("Application suspended", fApplicationSuspendedCallback);
    oBugId.fAddCallback("Application debug output", fApplicationDebugOutputCallback);
    oBugId.fAddCallback("Application stderr output", fApplicationStdErrOutputCallback);
    oBugId.fAddCallback("Application stdout output", fApplicationStdOutOutputCallback);
    oBugId.fAddCallback("Bug report", fBugReportCallback);
    oBugId.fAddCallback("Cdb stderr output", fCdbStdErrOutputCallback);
    if gbVerbose:
      oBugId.fAddCallback("Cdb stdin input", fCdbStdInInputCallback);
      oBugId.fAddCallback("Cdb stdout output", fCdbStdOutOutputCallback);
      oBugId.fAddCallback("Log message", fLogMessageCallback);
    oBugId.fAddCallback("Failed to apply application memory limits", fFailedToApplyApplicationMemoryLimitsCallback);
    oBugId.fAddCallback("Failed to apply process memory limits", fFailedToApplyProcessMemoryLimitsCallback);
    oBugId.fAddCallback("Failed to debug application", fFailedToDebugApplicationCallback);
    oBugId.fAddCallback("Internal exception", fInternalExceptionCallback);
    oBugId.fAddCallback("License warnings", fLicenseWarningsCallback);
    oBugId.fAddCallback("License errors", fLicenseErrorsCallback);
    oBugId.fAddCallback("Page heap not enabled", fPageHeapNotEnabledCallback);
    oBugId.fAddCallback("Cdb ISA not ideal", fCdbISANotIdealCallback);
    oBugId.fAddCallback("Process attached", fProcessAttachedCallback);
    oBugId.fAddCallback("Process started", fProcessStartedCallback);
    oBugId.fAddCallback("Process terminated", fProcessTerminatedCallback);

    if dxConfig["nApplicationMaxRunTimeInSeconds"] is not None:
      oBugId.foSetTimeout(
        sDescription = "Maximum application runtime",
        nTimeoutInSeconds = dxConfig["nApplicationMaxRunTimeInSeconds"],
        f0Callback = fApplicationMaxRunTimeCallback,
     );
    if dxConfig["bExcessiveCPUUsageCheckEnabled"] and dxConfig["nExcessiveCPUUsageCheckInitialTimeoutInSeconds"]:
      oBugId.fSetCheckForExcessiveCPUUsageTimeout(dxConfig["nExcessiveCPUUsageCheckInitialTimeoutInSeconds"]);
    guDetectedBugsCount = 0;
    oBugId.fStart();
    oBugId.fWait();
    if gbAnErrorOccured:
      if fCleanup:
        # Call cleanup after runnning the application, before exiting BugId
        oConsole.fStatus("* Cleaning up application state...");
        fCleanup();
      fTerminate(3);
    if guDetectedBugsCount == 0:
      oConsole.fPrint(u"\u2500\u2500 The application terminated without a bug being detected ", sPadding = u"\u2500");
      gduNumberOfRepros_by_sBugIdAndLocation.setdefault("No crash", 0);
      gduNumberOfRepros_by_sBugIdAndLocation["No crash"] += 1;
    if gbVerbose:
      oConsole.fPrint("  Application time: %s seconds" % (long(oBugId.fnApplicationRunTimeInSeconds() * 1000) / 1000.0));
      nOverheadTimeInSeconds = time.clock() - nStartTimeInSeconds - oBugId.fnApplicationRunTimeInSeconds();
      oConsole.fPrint("  BugId overhead:   %s seconds" % (long(nOverheadTimeInSeconds * 1000) / 1000.0));
    if uNumberOfRepeats is not None:
      uNumberOfRepeats -= 1;
      if uNumberOfRepeats == 0:
        bRepeat = False;
    if not bRepeat:
      if fCleanup:
        # Call cleanup after runnning the application, before exiting BugId
        oConsole.fStatus("* Cleaning up application state...");
        fCleanup();
      fTerminate(guDetectedBugsCount > 0 and 1 or 0);
    sStatistics = "";
    auOrderedNumberOfRepros = sorted(list(set(gduNumberOfRepros_by_sBugIdAndLocation.values())));
    auOrderedNumberOfRepros.reverse();
    for uNumberOfRepros in auOrderedNumberOfRepros:
      for sBugIdAndLocation in gduNumberOfRepros_by_sBugIdAndLocation.keys():
        if gduNumberOfRepros_by_sBugIdAndLocation[sBugIdAndLocation] == uNumberOfRepros:
          sStatistics += "%d \xD7 %s (%d%%)\r\n" % (uNumberOfRepros, str(sBugIdAndLocation), \
              round(100.0 * uNumberOfRepros / uRunCounter));
    if dxConfig["sReportFolderPath"] is not None:
      sStatisticsFilePath = os.path.join(dxConfig["sReportFolderPath"], sValidStatisticsFileName);
    else:
      sStatisticsFilePath = sValidStatisticsFileName;
    oStatisticsFile = None;
    try:
      oStatisticsFile = mFileSystem2.foGetOrCreateFile(sStatisticsFilePath);
      oStatisticsFile.fWrite(sStatistics);
    except Exception as oException:
      oConsole.fPrint("  Statistics:       ", ERROR, "Cannot be saved (", ERROR_INFO, str(oException), ERROR, ")");
    else:
      oConsole.fPrint("  Statistics:       ", INFO, sStatisticsFilePath, NORMAL, " (%d bytes)" % len(sStatistics));
    if oStatisticsFile:
      oStatisticsFile.fClose();
    oConsole.fPrint(); # and loop
  raise AssertionError("Not reached!"); #  lgtm [py/unreachable-statement]
  
if __name__ == "__main__":
  # Apply settings in dxConfig["cBugId"] to cBugId.dxConfig, then replace dxConfig["cBugId"] with cBugId.dxConfig.
  for (sName, xValue) in dxConfig["cBugId"].items():
    # Note that this does not allow modifying individual properties of dictionaries in dxConfig for cBugId.
    # But at this time, there are no dictionaries in dxConfig, so this is not required.
    cBugId.dxConfig[sName] = xValue;
  dxConfig["cBugId"] = cBugId.dxConfig;
  oConsole.fEnableLog();
  try:
    fMain(sys.argv[1:]);
  except KeyboardInterrupt:
    oConsole.fPrint("+ Interrupted.");
  except Exception as oException:
    gbAnErrorOccured = True;
    cException, oException, oTraceBack = sys.exc_info();
    fSaveInternalExceptionReportAndExit(oException, oTraceBack);
