"""                                                                             
  ____________________________________________________________________________  
                              __                                                
   ││▌║█▐▐║▌▌█│║║│      _,siSP**YSis,_       ╒╦╦══╦╗             ╒╦╦╕    ╔╦╕    
   ││▌║█▐▐║▌▌█│║║│    ,SP*'`    . `'*YS,      ║╠══╬╣ ╔╗ ╔╗ ╔╦═╦╗  ║║  ╔╦═╬╣     
   ╵2808197631337╵   dS'  _    |    _ 'Sb    ╘╩╩══╩╝ ╚╩═╩╝ ╚╩═╬╣ ╘╩╩╛ ╚╩═╩╝     
                    dP     \,-` `-<` `  Y;                 ╚╩═╩╝    ╮╷╭         
      ╮╷╭          ,S`  \+' \      \    `Sissssssssssssssssssss,   :O()    ╲ö╱  
     :O()          (S   (   | --====)   :SSSSSSSSSSSSSSSSSSSSSSD    ╯╵╰    ─O─  
      ╯╵╰  ╮╷╭     'S,  /+, /      /    ,S?********************'           ╱O╲  
           ()O:     Yb    _/'-_ _-<._.  dP                                      
           ╯╵╰       YS,       |      ,SP         https://bugid.skylined.nl     
  ____________________`Sbs,_    ' _,sdS`______________________________________  
                        `'*YSissiSY*'`                                          
                              ``                                                
                                                                            """;

import json, os, re, sys, time;

sModulePath = os.path.dirname(__file__);
sys.path = [sModulePath] + [sPath for sPath in sys.path if sPath.lower() != sModulePath.lower()];
from fInitializeProduct import fInitializeProduct;
fInitializeProduct();

try: # mDebugOutput use is Optional
  import mDebugOutput as m0DebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  m0DebugOutput = None;

guExitCodeInternalError = 1; # Just in case mExitCodes is not loaded, as we need this later.
try:
  # Load the stuff from external modules that we need.
  from mBugId import cBugId;
  from mConsole import oConsole;
  from mDateTime import cDateTime, cDateTimeDuration;
  from mFileSystemItem import cFileSystemItem;
  from mNotProvided import *;
  import mProductDetails, mWindowsAPI;
  
  from ddxApplicationSettings_by_sKeyword import ddxApplicationSettings_by_sKeyword;
  from dxConfig import dxConfig;
  from fApplicationDebugOutputCallbackHandler import fApplicationDebugOutputCallbackHandler;
  from fApplicationMaxRunTimeCallbackHandler import fApplicationMaxRunTimeCallbackHandler;
  from fApplicationResumedCallbackHandler import fApplicationResumedCallbackHandler;
  from fApplicationRunningCallbackHandler import fApplicationRunningCallbackHandler;
  from fApplicationStdErrOutputCallbackHandler import fApplicationStdErrOutputCallbackHandler;
  from fApplicationStdOutOutputCallbackHandler import fApplicationStdOutOutputCallbackHandler;
  from fApplicationSuspendedCallbackHandler import fApplicationSuspendedCallbackHandler;
  from fASanDetectedCallbackHandler import fASanDetectedCallbackHandler;
  from fatsArgumentLowerNameAndValue import fatsArgumentLowerNameAndValue;
  from fbApplyConfigSetting import fbApplyConfigSetting;
  from fbInstallAsJITDebugger import fbInstallAsJITDebugger;
  from fCdbCommandStartedExecutingCallbackHandler import fCdbCommandStartedExecutingCallbackHandler;
  from fCdbCommandFinishedExecutingCallbackHandler import fCdbCommandFinishedExecutingCallbackHandler;
  from fCdbStdErrOutputCallbackHandler import fCdbStdErrOutputCallbackHandler;
  from fCdbStdInInputCallbackHandler import fCdbStdInInputCallbackHandler;
  from fCdbStdOutOutputCallbackHandler import fCdbStdOutOutputCallbackHandler;
  from fCheckPythonVersion import fCheckPythonVersion;
  from fCollateralCannotIgnoreBugCallbackHandler import fCollateralCannotIgnoreBugCallbackHandler;
  from fCollateralBugIgnoredCallbackHandler import fCollateralBugIgnoredCallbackHandler;
  from fdsGetAdditionalVersionByName import fdsGetAdditionalVersionByName;
  from fiCollateralInteractiveAskForValue import fiCollateralInteractiveAskForValue;
  from fLogMessageCallbackHandler import fLogMessageCallbackHandler;
  from fOutputApplicationKeyWordHelp import fOutputApplicationKeyWordHelp;
  from fOutputCurrentJITDebuggerSettings import fOutputCurrentJITDebuggerSettings;
  from fOutputExceptionInformation import fOutputExceptionInformation;
  from fOutputMessageForProcess import fOutputMessageForProcess;
  from fProcessStartedCallbackHandler import fProcessStartedCallbackHandler;
  from fProcessTerminatedCallbackHandler import fProcessTerminatedCallbackHandler;
  from mColorsAndChars import *;
  from mExitCodes import *;
  
  def fxProcessBooleanArgument(sArgumentName, s0Value, u0CanAlsoBeAnIntegerLargerThan = None):
    if s0Value is None or s0Value.lower() == "true":
      return True;
    if s0Value.lower() == "false":
      return False;
    if u0CanAlsoBeAnIntegerLargerThan is not None:
      try:
        uValue = int(s0Value);
      except:
        pass;
      else:
        if uValue > u0CanAlsoBeAnIntegerLargerThan:
          return uValue;
    oConsole.fOutput(
      COLOR_ERROR, CHAR_ERROR,
      COLOR_NORMAL, " The value for ",
      COLOR_INFO, sArgument,
      COLOR_NORMAL, " must be \"",
      COLOR_INFO, "true",
      COLOR_NORMAL, "\" (default) or \"",
      COLOR_INFO, "false",
      COLOR_NORMAL, "\"",
      [
        " or an integer larger than ", COLOR_INFO, str(u0CanAlsoBeAnIntegerLargerThan), COLOR_NORMAL,
      ] if u0CanAlsoBeAnIntegerLargerThan is not None else [],
      ".",
    );
    fTerminate(guExitCodeBadArgument);
  def fTerminateIfNoArgumentValueProvided(sArgumentName, s0Value, sExpectedValueType):
    if not s0Value:
      oConsole.fOutput(
        COLOR_ERROR, CHAR_ERROR,
        COLOR_NORMAL, " The value for ",
        COLOR_INFO, sArgumentName,
        COLOR_NORMAL, " must contain ", sExpectedValueType, ".",
      );
      fTerminate(guExitCodeBadArgument);
  
  if __name__ == "__main__":
    asTestedPythonVersions = ["3.8.5", "3.9.1", "3.9.7", "3.10.0"];
    
    gasAttachForProcessExecutableNames = [];
    gasLowercaseBinaryNamesThatAreAllowedToRunWithoutPageHeap = [
      "conhost.exe", # Used to create console windows, not part of the target application (unless the target is conhost)
    ];
    gasReportedLowercaseBinaryNamesWithoutPageHeap = [];
    gasBinaryNamesThatAreAllowedToRunWithNonIdealCdbISA = [
      # No application is known to require running processes with a non-ideal cdb ISA at this point.
    ];
    gasReportedBinaryNameWithNonIdealCdbISA = [];
    gbAnInternalErrorOccured = False;
    gbFailedToApplyMemoryLimitsErrorShown = False;
    gbSaveDump = False;
    gbSaveFullDump = False;
    guDetectedBugsCount = 0;
    guNumberOfTimesToRunTheApplication = 1;
    gu0MaximumNumberOfBugsEachRun = 1;
    gduNumberOfRepros_by_sBugIdAndLocation = {};
    gbSaveOutputWithReport = False;
    gbPauseBeforeExit = False;
    gbRunningAsJITDebugger = False;
    # o0Parent can be used without checking for None because every file has a parent:
    goInternalErrorReportsFolder = cFileSystemItem(__file__).o0Parent.foGetChild("Internal error reports");
    goBugIdStartDateTime = cDateTime.foNow();
    def fsGetFileName(sFileNamesBase, bPrefixWithBugIdStartDateTime):
      # Translate characters that are not valid in file names.
      # Optionally add the BugId start date as a prefix.
      return cFileSystemItem.fsGetValidName(
        "%s%s" % (
          (goBugIdStartDateTime.fsToString() + " ") if bPrefixWithBugIdStartDateTime else "",
          sFileNamesBase,
        ),
        bUseUnicodeHomographs = dxConfig["bUseUnicodeReportFileNames"],
      );
    
    def fTerminate(uExitCode):
      oConsole.fCleanup();
      if gbPauseBeforeExit:
        oConsole.fOutput("Press ENTER to quit...");
        input();
      os._exit(uExitCode);
    
    def fFailedToDebugApplicationCallback(oBugId, sErrorMessage):
      global gbAnInternalErrorOccured;
      gbAnInternalErrorOccured = True;
      oConsole.fLock();
      try:
        oConsole.fOutput("┌───[", COLOR_ERROR, " Failed to debug the application ", COLOR_NORMAL, "]", sPadding = "─");
        for sLine in sErrorMessage.split("\n"):
          oConsole.fOutput("│ ", COLOR_INFO, sLine.rstrip("\r"));
        oConsole.fOutput("└", sPadding = "─");
        oConsole.fOutput();
      finally:
        oConsole.fUnlock();
    
    def fFailedToApplyApplicationMemoryLimitsCallback(oBugId, oProcess, bIsMainProcess):
      global gbFailedToApplyMemoryLimitsErrorShown;
      if not dxConfig["bQuiet"]:
        fOutputMessageForProcess(
          COLOR_ERROR, CHAR_ERROR,
          oProcess, bIsMainProcess,
          "Cannot apply application memory limits",
        );
        gbFailedToApplyMemoryLimitsErrorShown = True;
        if not dxConfig["bVerbose"]:
          oConsole.fOutput("  Any additional failures to apply memory limits to processess will not be shown.");
    
    def fFailedToApplyProcessMemoryLimitsCallback(oBugId, oProcess, bIsMainProcess):
      global gbFailedToApplyMemoryLimitsErrorShown;
      if dxConfig["bVerbose"] or not gbFailedToApplyMemoryLimitsErrorShown:
        fOutputMessageForProcess(
          COLOR_ERROR, CHAR_ERROR,
          oProcess, bIsMainProcess,
          "Cannot apply process memory limits",
        );
        gbFailedToApplyMemoryLimitsErrorShown = True;
        if not dxConfig["bVerbose"]:
          oConsole.fOutput("  Any additional failures to apply memory limits to processess will not be shown.");
    
    def fInternalExceptionCallback(oBugId, oThread, oException, oTraceBack):
      global gbAnInternalErrorOccured;
      gbAnInternalErrorOccured = True;
      fSaveInternalExceptionReportAndExit(oException, oTraceBack);
    
    def fSaveInternalExceptionReportAndExit(oException, oTraceBack):
      fOutputExceptionInformation(oException, oTraceBack);
      rErrorReportFileName = re.compile(
        r"\A"
        r"\d{4}.\d\d.\d\d " r"\d\d.\d\d.\d\d(?:.\d+)? " # Date Time
        r"BugId error report #(\d+)\.txt"              # Name #<number>
        r"\Z"
      );
      uIndex = 1;
      if not goInternalErrorReportsFolder.fbIsFolder:
        if not goInternalErrorReportsFolder.fbCreateAsFolder(bCreateParents = True):
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " The internal error report folder ",
            COLOR_INFO, goInternalErrorReportsFolder.sPath,
            COLOR_NORMAL, " cannot be created.",
          );
      else:
        # Scan for previous error reports, so we can number them:
        a0oPotentialOlderErrorReports = goInternalErrorReportsFolder.fa0oGetChildren(bThrowErrors = False);
        if a0oPotentialOlderErrorReports is None:
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " The internal error report folder ",
            COLOR_INFO, goInternalErrorReportsFolder.sPath,
            COLOR_NORMAL, " cannot be read.",
          );
        else:
          for oPotentialOlderErrorReport in a0oPotentialOlderErrorReports:
            oErrorReportFileNameMatch = rErrorReportFileName.match(oPotentialOlderErrorReport.sName);
            if oErrorReportFileNameMatch:
              uExistingIndex = int(oErrorReportFileNameMatch.group(1));
              if uExistingIndex >= uIndex:
                uIndex = uExistingIndex + 1;
      sExceptionReportFileName = fsGetFileName(
        "BugId error report #%d.txt" % uIndex,
        bPrefixWithBugIdStartDateTime = True
      );
      oExceptionReportFile = goInternalErrorReportsFolder.foGetChild(sExceptionReportFileName);
      oConsole.fStatus(
        COLOR_BUSY, CHAR_BUSY,
        COLOR_NORMAL, " Creating a copy of the error report in ",
        COLOR_INFO, oExceptionReportFile.sPath,
        COLOR_NORMAL, "...",
      );
      assert oConsole.fbCopyOutputToFilePath(oExceptionReportFile.sPath, bOverwrite = True, bThrowErrors = True), \
          "UNREACHABLE CODE (bThrowErrors = True)";
      oConsole.fOutput(
        COLOR_OK, CHAR_OK,
        COLOR_NORMAL, " A copy of the error report can be found in ",
        COLOR_INFO, oExceptionReportFile.sPath,
        COLOR_NORMAL, ".",
      );
      fTerminate(guExitCodeInternalError);
    
    def fLicenseErrorsCallback(oBugId, asErrors):
      # These should have been reported before cBugId was even instantiated, so this is kind of unexpected.
      # But rather than raise AssertionError("NOT REACHED"), we'll report the license error gracefully:
      global gbAnInternalErrorOccured;
      gbAnInternalErrorOccured = True;
      oConsole.fLock();
      try:
        oConsole.fOutput("┌───[", COLOR_INFO, " Software license error ", COLOR_NORMAL, "]", sPadding = "─");
        for sError in asErrors:
          oConsole.fOutput("│ ", COLOR_INFO, sError);
        oConsole.fOutput("└", sPadding = "─");
      finally:
        oConsole.fUnlock();
      fTerminate(guExitCodeLicenseError);
    
    def fLicenseWarningsCallback(oBugId, asWarnings):
      # These were already reported when BugId started; ignore them.
      pass;
    
    def fCdbISANotIdealCallback(oBugId, oProcess, bIsMainProcess, sCdbISA, bPreventable):
      global \
          gasBinaryNamesThatAreAllowedToRunWithNonIdealCdbISA, \
          gasReportedBinaryNameWithNonIdealCdbISA, \
          gbAnInternalErrorOccured;
      sBinaryName = oProcess.sBinaryName;
      if sBinaryName.lower() in gasBinaryNamesThatAreAllowedToRunWithNonIdealCdbISA:
        return;
      if not bPreventable:
        if not dxConfig["bQuiet"] and sBinaryName not in gasReportedBinaryNameWithNonIdealCdbISA:
          gasReportedBinaryNameWithNonIdealCdbISA.append(sBinaryName);
          oConsole.fLock();
          try:
            oConsole.fOutput(
              COLOR_WARNING, CHAR_WARNING,
              COLOR_NORMAL, " You are debugging an ",
              COLOR_INFO, oProcess.sISA,
              COLOR_NORMAL, " process running ",
              COLOR_INFO, sBinaryName,
              COLOR_NORMAL, " with a ",
              COLOR_INFO, sCdbISA,
              COLOR_NORMAL, " cdb.exe.",
            );
            oConsole.fOutput("  This appears to be due to the application running both x86 and x64 processes.");
            oConsole.fOutput("  Unfortunately, this means use-after-free bugs in this process may be reported");
            oConsole.fOutput("  as attempts to access reserved memory regions, which is tecnically true but");
            oConsole.fOutput("  not as accurate as you might expect.");
            oConsole.fOutput();
          finally:
            oConsole.fUnlock();
      else:
        gbAnInternalErrorOccured = True;
        oConsole.fLock();
        try:
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " You are debugging an ",
            COLOR_INFO, oProcess.sISA,
            COLOR_NORMAL, " process running ",
            COLOR_INFO, sBinaryName,
            COLOR_NORMAL, " with a ",
            COLOR_INFO, sCdbISA,
            COLOR_NORMAL, " version of cdb.exe.",
          );
          oConsole.fOutput(
            "  You should use the ",
            COLOR_INFO, "--isa=", oProcess.sISA, COLOR_NORMAL,
            " command line argument to let BugId know it should be using a ",
            COLOR_INFO, oProcess.sISA,
            COLOR_NORMAL, " version of cdb.exe.");
          oConsole.fOutput("  Please restart BugId with the aboce command line argument to try again.");
          oConsole.fOutput();
          oConsole.fStatus(COLOR_BUSY, CHAR_BUSY, COLOR_NORMAL, " BugId is stopping...");
        finally:
          oConsole.fUnlock();
        # There is no reason to run without page heap, so terminated.
        oBugId.fStop();
        # If you really want to run without page heap, set `dxConfig["cBugId"]["bEnsurePageHeap"]` to `False` in
        # `dxConfig.py`or run with the command-line siwtch `--cBugId.bEnsurePageHeap=false`
    
    def fPageHeapNotEnabledCallback(oBugId, oProcess, bIsMainProcess, bPreventable):
      global \
          gasLowercaseBinaryNamesThatAreAllowedToRunWithoutPageHeap, \
          gasReportedLowercaseBinaryNamesWithoutPageHeap;
      sLowerBinaryName = oProcess.sBinaryName.lower();
      if (
        dxConfig["bQuiet"]
        or sLowerBinaryName in gasLowercaseBinaryNamesThatAreAllowedToRunWithoutPageHeap
        or sLowerBinaryName in gasReportedLowercaseBinaryNamesWithoutPageHeap 
      ):
        return;
      gasReportedLowercaseBinaryNamesWithoutPageHeap.append(sLowerBinaryName);
      oConsole.fLock();
      try:
        oConsole.fOutput(
          COLOR_WARNING, CHAR_WARNING,
          COLOR_NORMAL, " Full page heap is not enabled for ",
          COLOR_INFO, oProcess.sBinaryName,
          COLOR_NORMAL, " in process ",
          COLOR_INFO, "%s" % oProcess.uId,
          COLOR_NORMAL, "/",
          COLOR_INFO, "0x%X" % oProcess.uId,
          COLOR_NORMAL, ".",
        );
        if bPreventable:
          oConsole.fOutput("  Without page heap enabled, detection and anaylsis of any bugs will be sub-");
          oConsole.fOutput("  optimal. Please enable page heap to improve detection and analysis.");
          oConsole.fOutput();
          oConsole.fOutput("  You can enabled full page heap for ", sLowerBinaryName, " by running:");
          oConsole.fOutput();
          oConsole.fOutput("      ", COLOR_INFO, 'PageHeap.cmd "', oProcess.sBinaryName, '" ON');
        else:
          oConsole.fOutput("  This appears to be due to a bug in page heap that prevents it from");
          oConsole.fOutput("  determining the binary name correctly. Unfortunately, there is no known fix");
          oConsole.fOutput("  or work-around for this. BugId will continue, but detection and analysis of");
          oConsole.fOutput("  any bugs in this process will be sub-optimal.");
        oConsole.fOutput();
      finally:
        oConsole.fUnlock();
    
    def fProcessAttachedCallback(oBugId, oProcess, bIsMainProcess):
      global gasAttachForProcessExecutableNames;
      if not dxConfig["bQuiet"]: # Main processes
        fOutputMessageForProcess(
          COLOR_ADD, CHAR_ADD,
          oProcess, bIsMainProcess,
          "Attached (",
          COLOR_INFO, oProcess.sCommandLine or "command line unknown",
          COLOR_NORMAL, ").",
        );
      # Now is a good time to look for additional binaries that may need to be debugged as well.
      if gasAttachForProcessExecutableNames:
        oBugId.fAttachForProcessExecutableNames(*gasAttachForProcessExecutableNames);
    
    def fBugReportCallback(oBugId, oBugReport):
      global guDetectedBugsCount, \
             gu0MaximumNumberOfBugsEachRun, \
             gduNumberOfRepros_by_sBugIdAndLocation, \
             gbAnInternalErrorOccured;
      guDetectedBugsCount += 1;
      oConsole.fLock();
      try:
        oConsole.fOutput("┌───[", COLOR_HILITE, " A bug was detected ", COLOR_NORMAL, "]", sPadding = "─");
        if oBugReport.s0BugLocation:
          oConsole.fOutput("│ Id @ Location:    ", COLOR_INFO, oBugReport.sId, COLOR_NORMAL, " @ ", COLOR_INFO, oBugReport.s0BugLocation);
          sBugIdAndLocation = "%s @ %s" % (oBugReport.sId, oBugReport.s0BugLocation);
        else:
          oConsole.fOutput("│ Id:               ", COLOR_INFO, oBugReport.sId);
          sBugIdAndLocation = oBugReport.sId;
        gduNumberOfRepros_by_sBugIdAndLocation.setdefault(sBugIdAndLocation, 0);
        gduNumberOfRepros_by_sBugIdAndLocation[sBugIdAndLocation] += 1;
        if oBugReport.sBugSourceLocation:
          oConsole.fOutput("│ Source:           ", COLOR_INFO, oBugReport.sBugSourceLocation);
        oConsole.fOutput("│ Description:      ", COLOR_INFO, oBugReport.s0BugDescription or "None provided");
        oConsole.fOutput("│ Security impact:  ", COLOR_INFO, (oBugReport.s0SecurityImpact or "None"));
        if oBugReport.asVersionInformation:
          oConsole.fOutput("│ Version:          ", COLOR_NORMAL, oBugReport.asVersionInformation[0]); # The process' binary.
          for sVersionInformation in oBugReport.asVersionInformation[1:]: # There may be two if the crash was in a
            oConsole.fOutput("│                   ", COLOR_NORMAL, sVersionInformation); # different binary (e.g. a .dll)
        if dxConfig["bGenerateReportHTML"]:
          # Use a report file name base on the BugId.
          # In collateral mode, we will number the reports, so they can more easily be ordered chronologically.
          bCountBugs = (
            gu0MaximumNumberOfBugsEachRun is None
            or gu0MaximumNumberOfBugsEachRun > 1
            or guNumberOfTimesToRunTheApplication > 1
          );
          sOutputFileNamesHeader = "".join([
            # guDetectedBugsCount has already been increased from zero, so the first file will be "#1"
            ("#%d " % guDetectedBugsCount) if bCountBugs else "",
            sBugIdAndLocation,
          ]);
          sReportFileName = fsGetFileName(
            sOutputFileNamesHeader + ".html",
            # In JIT mode and when counting bugs we prefix the report with the date and time.
            bPrefixWithBugIdStartDateTime = gbRunningAsJITDebugger or bCountBugs,
          );
          if dxConfig["sReportFolderPath"] is not None:
            oReportFile = cFileSystemItem(dxConfig["sReportFolderPath"]).foGetChild(sReportFileName);
          else:
            oReportFile = cFileSystemItem(sReportFileName);
          oConsole.fStatus(
            COLOR_BUSY, CHAR_BUSY,
            COLOR_NORMAL, " Saving bug report ",
            COLOR_INFO, oReportFile.sPath,
            COLOR_NORMAL, "...",
          );
          try:
            sbReportHTML = bytes(oBugReport.sReportHTML, "utf-8", "strict");
            if oReportFile.fbIsFile():
              oReportFile.fWrite(sbReportHTML);
            else:
              oReportFile.fCreateAsFile(sbReportHTML, bCreateParents = True);
          except Exception as oException:
            oConsole.fOutput(
              COLOR_NORMAL, "│ ",
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " Bug report:     ",
              COLOR_INFO, oReportFile.sPath,
              COLOR_NORMAL, "could not be saved!",
            );
            oConsole.fOutput(
              COLOR_NORMAL, "│                   => ",
              COLOR_INFO, str(oException),
            );
            gbAnInternalErrorOccured = True;
          else:
            oConsole.fOutput(
              COLOR_NORMAL, "│ Bug report:       ",
              COLOR_INFO, oReportFile.sName,
              COLOR_NORMAL, ".",
            );
          if gbSaveOutputWithReport:
            # We want the BugId ouput file to be stored in the same folder as the bug report,
            # with a similar file name, so where to store it is determined in a very similar way:
            sBugIdOutputFileName = fsGetFileName(
              sOutputFileNamesHeader + " BugId output.txt",
              bPrefixWithBugIdStartDateTime = gbRunningAsJITDebugger or bCountBug,
            );
            if dxConfig["sReportFolderPath"] is not None:
              oBugIdOutputFile = cFileSystemItem(dxConfig["sReportFolderPath"]).foGetChild(sBugIdOutputFileName);
            else:
              oBugIdOutputFile = cFileSystemItem(sBugIdOutputFileName);
            oConsole.fStatus(
              COLOR_BUSY, CHAR_BUSY,
              COLOR_NORMAL, " Saving BugId output log ",
              COLOR_INFO, oBugIdOutputFile.sPath,
              COLOR_NORMAL, "...",
            );
            try:
              oConsole.fbCopyOutputToFilePath(oBugIdOutputFile.sWindowsPath);
            except Exception as oException:
              oConsole.fCleanup();
              oConsole.fOutput("│ ", COLOR_ERROR, CHAR_ERROR, COLOR_NORMAL, " BugId output:   ", oBugIdOutputFile.sPath, COLOR_ERROR, "could not be saved!");
              oConsole.fOutput("│                   => ", COLOR_INFO, str(oException));
              gbAnInternalErrorOccured = True;
            else:
              oConsole.fOutput("│ BugId output log: ", COLOR_INFO, oBugIdOutputFile.sPath, COLOR_NORMAL, ".");
          if gbSaveDump:
            # We want the debugger dump file to be stored in the same folder as the bug report,
            # with a similar file name, so where to store it is determined in a very similar way:
            sDebuggerDumpFileName = fsGetFileName(
              sOutputFileNamesHeader + ".dmp",
              bPrefixWithBugIdStartDateTime = gbRunningAsJITDebugger or bCountBugs,
            );
            # Because of limitations in cdb.exe, we can only use ASCII chars in the file name
            # all non-ASCII chars will be replaced with ".":
            sDebuggerDumpASCIIFileName = "".join([
              sChar if 0x20 <= ord(sChar) < 0x7F else "."
              for sChar in sDebuggerDumpFileName
            ]);
            if dxConfig["sReportFolderPath"] is not None:
              oDebuggerDumpFile = cFileSystemItem(dxConfig["sReportFolderPath"]).foGetChild(sDebuggerDumpASCIIFileName);
            else:
              oDebuggerDumpFile = cFileSystemItem(sDebuggerDumpASCIIFileName);
            oConsole.fStatus(
              COLOR_BUSY, CHAR_BUSY,
              COLOR_NORMAL, " Saving dump file ",
              COLOR_INFO, oDebuggerDumpFile.sPath,
              COLOR_NORMAL, "...",
            );
            oBugId.fSaveDumpToFile(oDebuggerDumpFile.sPath, True, gbSaveFullDump);
            oConsole.fOutput("│ Dump file:        ", COLOR_INFO, oDebuggerDumpFile.sPath, COLOR_NORMAL, ".");
        oConsole.fOutput("└", sPadding = "─");
      finally:
        oConsole.fUnlock();
    
    def fMain():
      global \
          gasAttachForProcessExecutableNames, \
          gasLowercaseBinaryNamesThatAreAllowedToRunWithoutPageHeap, \
          gbSaveDump, \
          gbSaveFullDump, \
          guDetectedBugsCount, \
          guNumberOfTimesToRunTheApplication, \
          gu0MaximumNumberOfBugsEachRun, \
          gbSaveOutputWithReport, \
          gbPauseBeforeExit;
      
      # Make sure Windows and the Python binary are up to date; we don't want our users to unknowingly run outdated
      # software as this is likely to cause unexpected issues.
      fCheckPythonVersion("BugId", asTestedPythonVersions, "https://github.com/SkyLined/BugId/issues/new")
      if mWindowsAPI.oSystemInfo.sOSVersion != "10.0":
        oConsole.fOutput(
          COLOR_ERROR, CHAR_ERROR, 
          COLOR_NORMAL, " BugId only runs on Windows 10.",
        );
        fTerminate(guExitCodeBadDependencyError);
      if mWindowsAPI.oSystemInfo.sOSISA == "x64" and mWindowsAPI.fsGetPythonISA() == "x86":
        oConsole.fLock();
        try:
          oConsole.fOutput("┌───[", COLOR_WARNING, " Warning ", COLOR_NORMAL, "]", sPadding = "─");
          oConsole.fOutput(
            "│ You are running a ",
            COLOR_INFO, "32-bit",
            COLOR_NORMAL, " version of Python on a ",
            COLOR_INFO, "64-bit",
            COLOR_NORMAL, " version of Windows.",
          );
          oConsole.fOutput(
            "│ BugId will not be able to debug 64-bit applications unless you run it in a 64-bit version of Python.",
          );
          oConsole.fOutput(
            "│ If you experience any issues, use a 64-bit version of Python and try again.",
          );
          oConsole.fOutput("└", sPadding = "─");
        finally:
          oConsole.fUnlock();
      
      # Parse all arguments until we encounter "--".
      s0ApplicationKeyword = None;
      s0ApplicationBinaryPath = None;
      auApplicationProcessIds = [];
      u0JITDebuggerEventId = None;
      o0UWPApplication = None;
      asApplicationOptionalArguments = [];
      sApplicationISA = None;
      bRepeatForever = False;
      uNumberOfTimesTheApplicationHasBeenRun = 0;
      bCheckForUpdates = False;
      dxUserProvidedConfigSettings = {};
      asAdditionalLocalSymbolPaths = [];
      bFast = False;
      a0sJITDebuggerArguments = None;
      for (sArgument, s0LowerName, s0Value) in fatsArgumentLowerNameAndValue(fdsGetAdditionalVersionByName):
        if a0sJITDebuggerArguments is not None:
          # Stop processing arguments after "-I"
          a0sJITDebuggerArguments.append(sArgument);
          continue;
        if s0LowerName in ["q", "quiet"]:
          dxConfig["bQuiet"] = fxProcessBooleanArgument(s0LowerName, s0Value);
        elif s0LowerName in ["v", "verbose"]:
          dxConfig["bVerbose"] = fxProcessBooleanArgument(s0LowerName, s0Value);
        elif s0LowerName in ["p", "pause"]:
          gbPauseBeforeExit = fxProcessBooleanArgument(s0LowerName, s0Value);
        elif s0LowerName in ["f", "fast", "quick"]:
          bFast = fxProcessBooleanArgument(s0LowerName, s0Value);
        elif s0LowerName in ["r", "repeat", "forever"]:
          xValue = fxProcessBooleanArgument(s0LowerName, s0Value, u0CanAlsoBeAnIntegerLargerThan = 1 if s0LowerName != "forever" else None);
          if isinstance(xValue, bool):
            bRepeatForever = xValue;
          else:
            bRepeatForever = False;
            guNumberOfTimesToRunTheApplication = xValue;
        elif s0LowerName in ["d", "dump", "full-dump"]:
          if fxProcessBooleanArgument(s0LowerName, s0Value):
            gbSaveDump = True;
            if s0LowerName in ["full-dump"]:
              gbSaveFullDump = True; # --full-dump[=true] enables dump & full dump
          elif s0LowerName in ["full-dump"]:
            gbSaveFullDump = False; # --full-dump=false disables full dump only (not dump)
          else:
            gbSaveDump = False;
        elif s0LowerName in ["i"]:
          if s0Value is not None:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " The option ",
              COLOR_INFO, sArgument,
              COLOR_NORMAL, " does not accept a value.",
            )
            fTerminate(guExitCodeBadArgument);
          # Install as JIT Debugger. Remaining arguments are passed on the command line to the JIT debugger.
          a0sJITDebuggerArguments = []; # Remaining arguments will be added to this list.
        elif s0LowerName in ["c", "collateral"]:
          if s0Value is None:
            gu0MaximumNumberOfBugsEachRun = None;
          elif s0Value == "?":
            gu0MaximumNumberOfBugsEachRun = None;
            dxConfig["bInteractive"] = True;
          else:
            # `--collateral=2` means one collateral bug in addition to the first bug.
            try:
              gu0MaximumNumberOfBugsEachRun = int(s0Value);
              assert gu0MaximumNumberOfBugsEachRun > 0;
            except:
              oConsole.fOutput(
                COLOR_ERROR, CHAR_ERROR,
                COLOR_NORMAL, " The value for ",
                COLOR_INFO, sArgument,
                COLOR_NORMAL, " must be empty or an integer larger than ",
                COLOR_INFO, "0",
                COLOR_NORMAL, ".",
              );
              fTerminate(guExitCodeBadArgument);
        elif s0LowerName in ["pid", "pids"]:
          if not s0Value:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " The value for ",
              COLOR_INFO, sArgument,
              COLOR_NORMAL, " must contain at least one process id.",
            );
            fTerminate(guExitCodeBadArgument);
          if s0ApplicationBinaryPath is not None:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " You cannot provide both an application binary and process ids.",
            );
            fTerminate(guExitCodeBadArgument);
          if o0UWPApplication is not None:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " You cannot provide both UWP application details and process ids.",
            );
            fTerminate(guExitCodeBadArgument);
          for sPid in s0Value.split(","):
            try:
              uProcessId = int(sPid);
              if uProcessId <= 0 or uProcessId % 4 != 0:
                raise ValueError();
              auApplicationProcessIds.append(uProcessId);
            except ValueError:
              oConsole.fOutput(
                COLOR_ERROR, CHAR_ERROR,
                COLOR_NORMAL, " The value for ",
                COLOR_INFO, sArgument,
                COLOR_NORMAL, " must contain a list of comma separated process ids and ",
                COLOR_INFO, repr(sPid),
                COLOR_NORMAL, " is not a valid process id.",
              );
              fTerminate(guExitCodeBadArgument);
        elif s0LowerName in ["handle-jit-event"]:
          fTerminateIfNoArgumentValueProvided(s0LowerName, s0Value, "a JIT debugger event id");
          try:
            u0JITDebuggerEventId = int(s0Value);
          except ValueError:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " The value for ",
              COLOR_INFO, sArgument,
              COLOR_NORMAL, " must contain a JIT debugger event id and ",
              COLOR_INFO, repr(s0Value),
              COLOR_NORMAL, " is not a valid event id.",
            );
            fTerminate(guExitCodeBadArgument);
        elif s0LowerName in ["uwp", "uwp-app"]:
          if not s0Value:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " You must provide UWP application details.",
            );
            fTerminate(guExitCodeBadArgument);
          if o0UWPApplication is not None:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " You cannot provide UWP application details more than once.",
            );
            fTerminate(guExitCodeBadArgument);
          if s0ApplicationBinaryPath is not None:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " You cannot provide an application binary and UWP application details.",
            );
            fTerminate(guExitCodeBadArgument);
          if len(auApplicationProcessIds) > 0:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " You cannot provide process ids and UWP application details.",
            );
            fTerminate(guExitCodeBadArgument);
          tsUWPApplicationPackageNameAndId = s0Value.split("!", 1);
          sUWPApplicationPackageName = tsUWPApplicationPackageNameAndId[0];
          sUWPApplicationId = tsUWPApplicationPackageNameAndId[1] if len(tsUWPApplicationPackageNameAndId) == 2 else None;
          o0UWPApplication = mWindowsAPI.cUWPApplication(sUWPApplicationPackageName, sUWPApplicationId);
        elif s0LowerName in ["jit"]:
          fOutputCurrentJITDebuggerSettings();
          fTerminate(guExitCodeSuccess);
        elif s0LowerName in ["log-output"]:
          gbSaveOutputWithReport = fxProcessBooleanArgument(s0LowerName, s0Value);
        elif s0LowerName in ["isa", "cpu"]:
          if not s0Value:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " You must provide an Instruction Set Architecture.",
            );
            fTerminate(guExitCodeBadArgument);
          if s0Value not in ["x86", "x64"]:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " Unknown Instruction Set Architecture ", repr(s0Value),
            );
            fTerminate(guExitCodeBadArgument);
          sApplicationISA = s0Value;
        elif s0LowerName in ["symbols"]:
          if s0Value is None or not cFileSystemItem(s0Value).fbIsFolder():
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " The value for ",
              COLOR_INFO, sArgument,
              COLOR_NORMAL, " must be a valid folder path.",
            );
            fTerminate(guExitCodeBadArgument);
          asAdditionalLocalSymbolPaths.append(s0Value);
        elif s0LowerName in ["report", "reports", "report-folder", "reports-folder", "report-folder-path", "reports-folder-path"]:
          if s0Value is None:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " The value for ",
              COLOR_INFO, sArgument,
              COLOR_NORMAL, " must be a valid folder path.",
            );
            fTerminate(guExitCodeBadArgument);
          oReportFolder = cFileSystemItem(s0Value);
          if (
            not oReportFolder.fbIsFolder()
            and not oReportFolder.fbCreateAsFolder(bCreateParents = True)
          ):
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " The folder ",
              COLOR_INFO, s0Value,
              COLOR_NORMAL, " does not exist and cannot be created.",
            );
            fTerminate(guExitCodeBadArgument);
          dxConfig["sReportFolderPath"] = s0Value;
        elif s0LowerName in ["test-internal-error", "internal-error-test"]:
          raise Exception("This exception was raised to test internal error handling.");
        elif s0LowerName:
          if not s0Value:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " You cannot provide a setting name (",
              COLOR_INFO, sArgument,
              COLOR_NORMAL, ") without a value.",
            );
            fTerminate(guExitCodeBadArgument);
          try:
            xValue = json.loads(s0Value);
          except ValueError as oError:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " Cannot decode argument JSON value ",
              COLOR_INFO, sArgument,
              COLOR_NORMAL, "=",
              COLOR_INFO, s0Value,
              COLOR_NORMAL, ": ",
              COLOR_INFO, " ".join(oError.args),
              COLOR_NORMAL, ".",
            );
            fTerminate(guExitCodeBadArgument);
          # User provided config settings must be applied after any keyword specific config settings, so we
          # save them and apply them later. We also need to get the non-lowercase name.
          sName = sArgument.split("=", 1)[0].lstrip("--"); # Good enough.
          dxUserProvidedConfigSettings[sName] = xValue;
        elif s0Value: # Before "--": 
          if s0ApplicationKeyword is None and s0ApplicationBinaryPath is None:
            if sArgument in ddxApplicationSettings_by_sKeyword:
              s0ApplicationKeyword = sArgument;
            elif sArgument[-1] == "?":
              sApplicationKeyword = sArgument[:-1];
              dxApplicationSettings = ddxApplicationSettings_by_sKeyword.get(sApplicationKeyword);
              if not dxApplicationSettings:
                oConsole.fOutput(
                  COLOR_ERROR, CHAR_ERROR,
                  COLOR_NORMAL, " Unknown application keyword ",
                  COLOR_INFO, sApplicationKeyword,
                  COLOR_NORMAL, ".",
                );
                fTerminate(guExitCodeBadArgument);
              fOutputApplicationKeyWordHelp(sApplicationKeyword, dxApplicationSettings);
              fTerminate(guExitCodeSuccess);
            else:
              if len(auApplicationProcessIds) > 0:
                oConsole.fOutput(
                  COLOR_ERROR, CHAR_ERROR,
                  COLOR_NORMAL, " You cannot provide process ids and an application binary.",
                );
                fTerminate(guExitCodeBadArgument);
              if o0UWPApplication is not None:
                oConsole.fOutput(
                  COLOR_ERROR, CHAR_ERROR,
                  COLOR_NORMAL, " You cannot provide an application UWP package name and a binary.",
                );
                fTerminate(guExitCodeBadArgument);
              s0ApplicationBinaryPath = sArgument;
          else:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " Unknown argument: ",
              COLOR_INFO, sArgument,
              COLOR_NORMAL, ".",
            );
        else: # After "--":
          if len(auApplicationProcessIds) > 0:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " You cannot provide process ids and application arguments.",
            );
            fTerminate(guExitCodeBadArgument);
          asApplicationOptionalArguments.append(sArgument);
      
      if a0sJITDebuggerArguments is not None:
        if fbInstallAsJITDebugger(a0sJITDebuggerArguments):
          fTerminate(guExitCodeSuccess);
        fTerminate(guExitCodeInternalError);
      if bFast:
        dxConfig["bQuiet"] = True;
        dxUserProvidedConfigSettings["bGenerateReportHTML"] = False;
        dxUserProvidedConfigSettings["azsSymbolServerURLs"] = [];
        dxUserProvidedConfigSettings["cBugId.bUse_NT_SYMBOL_PATH"] = False;
      
      if u0JITDebuggerEventId is not None and dxConfig["sReportFolderPath"] is None:
        oConsole.fOutput(
          COLOR_ERROR, CHAR_ERROR,
          COLOR_NORMAL, " JIT debugging is not possible without providing a value for ",
          COLOR_INFO, "sReportFolderPath",
          COLOR_NORMAL, ".",
        );
        fTerminate(guExitCodeBadArgument);
      
      dsApplicationURLTemplate_by_srSourceFilePath = {};
      
      if gbSaveOutputWithReport:
        oConsole.fEnableLog();
      
      fSetup = None; # Function specific to a keyword application, used to setup stuff before running.
      fCleanup = None; # Function specific to a keyword application, used to cleanup stuff before & after running.
      if s0ApplicationKeyword:
        dxApplicationSettings = ddxApplicationSettings_by_sKeyword.get(s0ApplicationKeyword);
        if not dxApplicationSettings:
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " Unknown application keyword ",
            COLOR_INFO, s0ApplicationKeyword,
            COLOR_NORMAL, ".",
          );
          fTerminate(guExitCodeBadArgument);
        fSetup = dxApplicationSettings.get("fSetup");
        fCleanup = dxConfig["bCleanup"] and dxApplicationSettings.get("fCleanup");
        # Get application binary/UWP package name/process ids as needed:
        if "sBinaryPath" in dxApplicationSettings:
          # This application is started from the command-line.
          if auApplicationProcessIds:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " You cannot provide process ids for application keyword ",
              COLOR_INFO, s0ApplicationKeyword,
              COLOR_NORMAL, ".",
            );
            fTerminate(guExitCodeBadArgument);
          if o0UWPApplication:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " You cannot provide an application UWP package name for application keyword ",
              COLOR_INFO, s0ApplicationKeyword,
              COLOR_NORMAL, ".",
            );
            fTerminate(guExitCodeBadArgument);
          if s0ApplicationBinaryPath is None:
            s0ApplicationBinaryPath = dxApplicationSettings["sBinaryPath"];
            if s0ApplicationBinaryPath is None:
              oConsole.fOutput(
                COLOR_ERROR, CHAR_ERROR,
                COLOR_NORMAL, " The main application binary for ",
                COLOR_INFO, s0ApplicationKeyword,
                COLOR_NORMAL, " could not be detected on your system.",
              );
              oConsole.fOutput(
                COLOR_NORMAL, "  Please provide the path to this binary in the arguments.",
              );
              fTerminate(guExitCodeApplicationBinaryNotFound);
        elif "dxUWPApplication" in dxApplicationSettings:
          dxUWPApplication = dxApplicationSettings["dxUWPApplication"];
          # This application is started as a Universal Windows Platform application.
          if s0ApplicationBinaryPath:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " You cannot provide an application binary for application keyword ",
              COLOR_INFO, s0ApplicationKeyword,
              COLOR_NORMAL, ".",
            );
            fTerminate(guExitCodeBadArgument);
          if auApplicationProcessIds:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL, " You cannot provide process ids for application keyword ",
              COLOR_INFO, s0ApplicationKeyword,
              COLOR_NORMAL, ".",
            );
            fTerminate(guExitCodeBadArgument);
          sUWPApplicationPackageName = dxUWPApplication["sPackageName"];
          sUWPApplicationId = dxUWPApplication["sId"];
          o0UWPApplication = mWindowsAPI.cUWPApplication(sUWPApplicationPackageName, sUWPApplicationId);
        elif not auApplicationProcessIds:
          # This application is attached to.
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " You must provide process ids for application keyword ",
            COLOR_INFO, s0ApplicationKeyword,
            COLOR_NORMAL, ".",
          );
          fTerminate(guExitCodeBadArgument);
        elif asApplicationOptionalArguments:
          # Cannot provide arguments if we're attaching to processes
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " You cannot provide arguments for application keyword ",
            COLOR_INFO, s0ApplicationKeyword,
            COLOR_NORMAL, ".",
          );
          fTerminate(guExitCodeBadArgument);
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
          asApplicationOptionalArguments = fasGetApplicationOptionalArguments(dxConfig, bForHelp = False);
        asApplicationArguments = asApplicationStaticArguments + asApplicationOptionalArguments;
        # Apply application specific settings
        if dxApplicationSettings.get("dxConfigSettings"):
          dxApplicationConfigSettings = dxApplicationSettings["dxConfigSettings"];
          if dxConfig["bVerbose"]:
            oConsole.fOutput(
              COLOR_INFO, CHAR_INFO,
              COLOR_NORMAL, " Applying application specific configuration for ",
              COLOR_INFO, s0ApplicationKeyword,
              COLOR_NORMAL, ":",
            );
          for (sSettingName, xValue) in dxApplicationConfigSettings.items():
            if sSettingName not in dxUserProvidedConfigSettings:
              # Apply and show result indented or errors.
              if not fbApplyConfigSetting(sSettingName, xValue, [None, "  "][dxConfig["bVerbose"]]):
                fTerminate(guExitCodeBadArgument);
          if dxConfig["bVerbose"]:
            oConsole.fOutput();
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
      elif (auApplicationProcessIds or o0UWPApplication or s0ApplicationBinaryPath):
        # There are no static arguments if there is no application keyword, only the user-supplied optional arguments
        # are used if they are supplied:
        asApplicationArguments = asApplicationOptionalArguments or [];
      else:
        oConsole.fLock();
        try:
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " You must provide something to debug. This can be either one or more process",
          );
          oConsole.fOutput("  ids, an application command-line or an UWP application package name.");
          oConsole.fOutput();
          oConsole.fOutput("  Run \"", COLOR_INFO, "BugId -h", COLOR_NORMAL, "\" for help on command-line arguments.");
        finally:
          oConsole.fUnlock();
        fTerminate(guExitCodeBadArgument);
      
      # Check that the UWP application exists if needed.
      if o0UWPApplication:
        if not o0UWPApplication.bPackageExists:
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " UWP application package ",
            COLOR_INFO, o0UWPApplication.sPackageName,
            COLOR_NORMAL, " does not exist.",
          );
          fTerminate(guExitCodeBadArgument);
        elif not o0UWPApplication.bIdExists:
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " UWP application package ",
            COLOR_INFO, o0UWPApplication.sPackageName,
            COLOR_NORMAL, " does not contain an application with id ",
            COLOR_INFO, o0UWPApplication.sApplicationId,
            COLOR_NORMAL, ".",
          );
          fTerminate(guExitCodeBadArgument);
      # Apply user provided settings:
      for (sSettingName, xValue) in list(dxUserProvidedConfigSettings.items()):
        # Apply and show result or errors:
        if not fbApplyConfigSetting(sSettingName, xValue, [None, ""][dxConfig["bVerbose"]]):
          fTerminate(guExitCodeBadArgument);
      
      # Check if cdb.exe is found:
      sCdbISA = sApplicationISA or cBugId.sOSISA;
      if not cBugId.fbCdbFound(sCdbISA):
        oConsole.fLock();
        try:
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " BugId depends on ",
            COLOR_INFO, "Debugging Tools for Windows",
            COLOR_NORMAL, " which was not found.",
          );
          oConsole.fOutput();
          oConsole.fOutput("  To install, download the Windows 10 SDK installer at:");
          oConsole.fOutput();
          oConsole.fOutput("    ", COLOR_INFO, "https://developer.microsoft.com/en-US/windows/downloads/windows-10-sdk");
          oConsole.fOutput();
          oConsole.fOutput("  After downloading, run the installer. You can deselect all other features");
          oConsole.fOutput("  of the SDK before installation; only ", COLOR_INFO, "Debugging Tools for Windows", COLOR_NORMAL, " is required.");
          oConsole.fOutput();
          oConsole.fOutput("  Once you have completed these steps, please try again.");
        finally:
          oConsole.fUnlock();
        fTerminate(guExitCodeBadArgument);
      
      # Check license
      (asLicenseErrors, asLicenseWarnings) = mProductDetails.ftasGetLicenseErrorsAndWarnings();
      if asLicenseErrors:
        oConsole.fLock();
        try:
          oConsole.fOutput("┌───[", COLOR_ERROR, " Software license error ", COLOR_NORMAL, "]", sPadding = "─");
          for sLicenseError in asLicenseErrors:
            oConsole.fOutput("│ ", COLOR_ERROR, CHAR_ERROR, COLOR_INFO, " ", sLicenseError);
          oConsole.fOutput("└", sPadding = "─");
        finally:
          oConsole.fUnlock();
        fTerminate(guExitCodeLicenseError);
      if asLicenseWarnings:
        oConsole.fLock();
        try:
          oConsole.fOutput("┌───[", COLOR_WARNING, " Software license warning ", COLOR_NORMAL, "]", sPadding = "─");
          for sLicenseWarning in asLicenseWarnings:
            oConsole.fOutput("│ ", COLOR_WARNING, CHAR_WARNING, COLOR_INFO, " ", sLicenseWarning);
          oConsole.fOutput("└", sPadding = "─");
        finally:
          oConsole.fUnlock();
      
      asLocalSymbolPaths = dxConfig["a0sLocalSymbolPaths"] or [];
      if asAdditionalLocalSymbolPaths:
        asLocalSymbolPaths += asAdditionalLocalSymbolPaths;
      while 1:
        nStartTimeInSeconds = time.time();
        if fSetup:
          # Call setup before the application is started. Argument is boolean value indicating if this is the first time
          # the function is being called.
          oConsole.fStatus(COLOR_BUSY, CHAR_BUSY, COLOR_NORMAL, " Applying special application configuration settings...");
          fSetup(bFirstRun = uNumberOfTimesTheApplicationHasBeenRun == 0);
        oBugId = cBugId(
          sCdbISA = sCdbISA,
          s0ApplicationBinaryPath = s0ApplicationBinaryPath or None,
          a0uApplicationProcessIds = auApplicationProcessIds or None,
          u0JITDebuggerEventId = u0JITDebuggerEventId,
          o0UWPApplication = o0UWPApplication,
          asApplicationArguments = asApplicationArguments,
          asLocalSymbolPaths = asLocalSymbolPaths,
          azsSymbolCachePaths = dxConfig["azsSymbolCachePaths"], 
          azsSymbolServerURLs = dxConfig["azsSymbolServerURLs"],
          d0sURLTemplate_by_srSourceFilePath = dsApplicationURLTemplate_by_srSourceFilePath,
          bGenerateReportHTML = dxConfig["bGenerateReportHTML"],
          u0ProcessMaxMemoryUse = dxConfig["u0ProcessMaxMemoryUse"],
          u0TotalMaxMemoryUse = dxConfig["u0TotalMaxMemoryUse"],
          u0MaximumNumberOfBugs = gu0MaximumNumberOfBugsEachRun,
          f0iCollateralInteractiveAskForValue = fiCollateralInteractiveAskForValue if dxConfig["bInteractive"] else None,
        );
        oConsole.fLock();
        try:
          if s0ApplicationBinaryPath:
            # make the binary path absolute because relative paths don't work.
            s0ApplicationBinaryPath = cFileSystemItem(s0ApplicationBinaryPath).sPath;
            if not dxConfig["bQuiet"]:
              asCommandLine = [s0ApplicationBinaryPath] + asApplicationArguments;
              oConsole.fOutput(
                COLOR_INFO, CHAR_INFO,
                COLOR_NORMAL, " Command line: ",
                COLOR_INFO, " ".join(asCommandLine),
              );
            oConsole.fStatus(COLOR_BUSY, CHAR_BUSY, COLOR_NORMAL, " The debugger is starting the application...");
          else:
            if auApplicationProcessIds:
              asProcessIdsOutput = [];
              for uApplicationProcessId in auApplicationProcessIds:
                if asProcessIdsOutput: asProcessIdsOutput.append(", ");
                asProcessIdsOutput.extend([COLOR_INFO, str(uApplicationProcessId), COLOR_NORMAL]);
              oConsole.fOutput(
                COLOR_INFO, CHAR_INFO,
                COLOR_NORMAL, " Running process ids: ",
                COLOR_INFO, *asProcessIdsOutput,
              );
            if o0UWPApplication and not dxConfig["bQuiet"]:
              oConsole.fOutput(*(
                [
                  COLOR_INFO, CHAR_INFO,
                  COLOR_NORMAL, " UWP application id: ",
                  COLOR_INFO, oBugId.o0UWPApplication.sApplicationId,
                  COLOR_NORMAL, ", package name: ",
                  COLOR_INFO, oBugId.o0UWPApplication.sPackageName,
                ] + ([
                  COLOR_NORMAL, ", Arguments: ",
                  COLOR_INFO, " ".join(asApplicationArguments),
                ] if asApplicationArguments else []) + [
                  COLOR_NORMAL, "."
                ]
              ));
            if not o0UWPApplication:
              oConsole.fStatus(COLOR_BUSY, CHAR_BUSY, COLOR_NORMAL, " The debugger is attaching to processes...");
            elif auApplicationProcessIds:
              oConsole.fStatus(COLOR_BUSY, CHAR_BUSY, COLOR_NORMAL, " The debugger is attaching to processes and starting the Windows App...");
            else:
              oConsole.fStatus(COLOR_BUSY, CHAR_BUSY, COLOR_NORMAL, " The debugger is starting the Windows App...");
        finally:
          oConsole.fUnlock();
        oBugId.fAddCallback("Application resumed", fApplicationResumedCallbackHandler);
        oBugId.fAddCallback("Application running", fApplicationRunningCallbackHandler);
        oBugId.fAddCallback("Application suspended", fApplicationSuspendedCallbackHandler);
        oBugId.fAddCallback("Application debug output", fApplicationDebugOutputCallbackHandler);
        oBugId.fAddCallback("Application stderr output", fApplicationStdErrOutputCallbackHandler);
        oBugId.fAddCallback("Application stdout output", fApplicationStdOutOutputCallbackHandler);
        oBugId.fAddCallback("ASan detected", fASanDetectedCallbackHandler);
        oBugId.fAddCallback("Bug cannot be ignored", fCollateralCannotIgnoreBugCallbackHandler);
        oBugId.fAddCallback("Bug ignored", fCollateralBugIgnoredCallbackHandler);
        oBugId.fAddCallback("Bug report", fBugReportCallback);
        oBugId.fAddCallback("Cdb command started executing", fCdbCommandStartedExecutingCallbackHandler);
        oBugId.fAddCallback("Cdb command finished executing", fCdbCommandFinishedExecutingCallbackHandler);
        oBugId.fAddCallback("Cdb stderr output", fCdbStdErrOutputCallbackHandler);
        if dxConfig["bVerbose"]:
          oBugId.fAddCallback("Cdb stdin input", fCdbStdInInputCallbackHandler);
          oBugId.fAddCallback("Cdb stdout output", fCdbStdOutOutputCallbackHandler);
          oBugId.fAddCallback("Log message", fLogMessageCallbackHandler);
        oBugId.fAddCallback("Failed to apply application memory limits", fFailedToApplyApplicationMemoryLimitsCallback);
        oBugId.fAddCallback("Failed to apply process memory limits", fFailedToApplyProcessMemoryLimitsCallback);
        oBugId.fAddCallback("Failed to debug application", fFailedToDebugApplicationCallback);
        oBugId.fAddCallback("Internal exception", fInternalExceptionCallback);
        oBugId.fAddCallback("License warnings", fLicenseWarningsCallback);
        oBugId.fAddCallback("License errors", fLicenseErrorsCallback);
        oBugId.fAddCallback("Page heap not enabled", fPageHeapNotEnabledCallback);
        oBugId.fAddCallback("Cdb ISA not ideal", fCdbISANotIdealCallback);
        oBugId.fAddCallback("Process attached", fProcessAttachedCallback);
        oBugId.fAddCallback("Process started", fProcessStartedCallbackHandler);
        oBugId.fAddCallback("Process terminated", fProcessTerminatedCallbackHandler);
        
        if dxConfig["n0ApplicationMaxRunTimeInSeconds"] is not None:
          oBugId.foSetTimeout(
            sDescription = "Maximum application runtime",
            nTimeoutInSeconds = dxConfig["n0ApplicationMaxRunTimeInSeconds"],
            f0Callback = fApplicationMaxRunTimeCallbackHandler,
         );
        if dxConfig["bExcessiveCPUUsageCheckEnabled"] and dxConfig["nExcessiveCPUUsageCheckInitialTimeoutInSeconds"]:
          oBugId.fSetCheckForExcessiveCPUUsageTimeout(dxConfig["nExcessiveCPUUsageCheckInitialTimeoutInSeconds"]);
        guDetectedBugsCount = 0;
        oBugId.fStart();
        oBugId.fWait();
        if gbAnInternalErrorOccured:
          if fCleanup:
            # Call cleanup after runnning the application, before exiting BugId
            oConsole.fStatus(COLOR_BUSY, CHAR_BUSY, COLOR_NORMAL, " Cleaning up application state...");
            fCleanup();
          fTerminate(guExitCodeInternalError);
        if guDetectedBugsCount == 0:
          oConsole.fOutput("─── The application terminated without a bug being detected ", sPadding = "─");
          gduNumberOfRepros_by_sBugIdAndLocation.setdefault("No crash", 0);
          gduNumberOfRepros_by_sBugIdAndLocation["No crash"] += 1;
        if dxConfig["bVerbose"]:
          nApplicationRunTimeInSeconds = oBugId.fnApplicationRunTimeInSeconds();
          nBugIdRunTimeInSeconds = time.time() - nStartTimeInSeconds;
          sApplicationRunTime = cDateTimeDuration.foFromSeconds(
            nApplicationRunTimeInSeconds
          ).fsToHumanReadableString(u0MaxNumberOfUnitsInOutput = 2);
          sOverHeadTime = cDateTimeDuration.foFromSeconds(
            nBugIdRunTimeInSeconds - nApplicationRunTimeInSeconds
          ).fsToHumanReadableString(u0MaxNumberOfUnitsInOutput = 2);
          oConsole.fOutput("  Application time: ", COLOR_INFO, sApplicationRunTime, COLOR_NORMAL, ".");
          oConsole.fOutput("  BugId overhead:   ", COLOR_INFO, sOverHeadTime, COLOR_NORMAL, ".");
        uNumberOfTimesTheApplicationHasBeenRun += 1;
        if not bRepeatForever and uNumberOfTimesTheApplicationHasBeenRun == guNumberOfTimesToRunTheApplication:
          if fCleanup:
            # Call cleanup after runnning the application, before exiting BugId
            oConsole.fStatus(COLOR_BUSY, CHAR_BUSY, COLOR_NORMAL, " Cleaning up application state...");
            fCleanup();
          fTerminate(guExitCodeSuccess if guDetectedBugsCount > 0 else guExitCodeNoBugsDetected);
        sStatistics = "";
        auOrderedNumberOfRepros = sorted(list(set(gduNumberOfRepros_by_sBugIdAndLocation.values())));
        auOrderedNumberOfRepros.reverse();
        for uNumberOfRepros in auOrderedNumberOfRepros:
          for sBugIdAndLocation in gduNumberOfRepros_by_sBugIdAndLocation.keys():
            if gduNumberOfRepros_by_sBugIdAndLocation[sBugIdAndLocation] == uNumberOfRepros:
              sStatistics += "%d \xD7 %s (%d%%)\r\n" % (uNumberOfRepros, str(sBugIdAndLocation), \
                  round(100.0 * uNumberOfRepros / uNumberOfTimesTheApplicationHasBeenRun));
        sStatisticsFileName = fsGetFileName(
          "Reproduction statistics.txt",
          bPrefixWithBugIdStartDateTime = True,
        );
        if dxConfig["sReportFolderPath"] is not None:
          oStatisticsFile = cFileSystemItem(dxConfig["sReportFolderPath"]).foGetChild(sStatisticsFileName);
        else:
          oStatisticsFile = cFileSystemItem(sStatisticsFileName);
        oConsole.fStatus(
          COLOR_BUSY, CHAR_BUSY,
          COLOR_NORMAL, " Saving statistics to file ",
          COLOR_INFO, oStatisticsFile.sPath,
          COLOR_NORMAL, "...",
        );
        try:
          if oStatisticsFile.fbIsFile():
            oStatisticsFile.fWrite(sStatistics);
          else:
            oStatisticsFile.fCreateAsFile(sStatistics, bCreateParents = True);
        except Exception as oException:
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " Statistics file ",
            COLOR_INFO, oStatisticsFile.sPath,
            COLOR_NORMAL, " could not be saved!",
          );
          oConsole.fOutput("  ", COLOR_ERROR, str(oException));
        else:
          oConsole.fOutput(
            "  Statistics:       ",
            COLOR_INFO, oStatisticsFile.sPath,
            COLOR_NORMAL, " (",
            COLOR_INFO, str(len(sStatistics)),
            COLOR_NORMAL, " bytes)",
          );
        oConsole.fOutput(); # and loop
      raise AssertionError("Not reached!"); #  lgtm [py/unreachable-statement]
      
    # Apply settings in dxConfig["cBugId"] to cBugId.dxConfig, then replace dxConfig["cBugId"] with cBugId.dxConfig.
    for (sName, xValue) in dxConfig["cBugId"].items():
      # Note that this does not allow modifying individual properties of dictionaries in dxConfig for cBugId.
      # But at this time, there are no dictionaries in dxConfig, so this is not required.
      cBugId.dxConfig[sName] = xValue;
    dxConfig["cBugId"] = cBugId.dxConfig;
    oConsole.fEnableLog();
    try:
      fMain();
    except KeyboardInterrupt:
      oConsole.fOutput(
        COLOR_ERROR, CHAR_ERROR,
        COLOR_NORMAL, " Interrupted.",
      );
    except Exception as oException:
      gbAnErrorOccured = True;
      cException, oException, oTraceBack = sys.exc_info();
      fSaveInternalExceptionReportAndExit(oException, oTraceBack);
except Exception as oException:
  if m0DebugOutput:
    m0DebugOutput.fTerminateWithException(
      oException = oException,
      uExitCode = guExitCodeInternalError,
    );
  raise;
