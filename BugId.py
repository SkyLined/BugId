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

import json, os, sys, time;

from fInitializeProduct import fInitializeProduct;
fInitializeProduct();

try: # mDebugOutput use is Optional
  import mDebugOutput as m0DebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  m0DebugOutput = None;

try:
  # Load the stuff from external modules that we need.
  from mBugId import cBugId;
  from mFileSystemItem import cFileSystemItem;
  import mProductDetails, mWindowsAPI;
  from mConsole import oConsole;
  from mNotProvided import *;
  
  from ddxApplicationSettings_by_sKeyword import ddxApplicationSettings_by_sKeyword;
  from dxConfig import dxConfig;
  from fbApplyConfigSetting import fbApplyConfigSetting;
  from fbInstallAsJITDebugger import fbInstallAsJITDebugger;
  from fCheckPythonVersion import fCheckPythonVersion;
  from fPrintApplicationKeyWordHelp import fPrintApplicationKeyWordHelp;
  from fPrintCurrentJITDebuggerSettings import fPrintCurrentJITDebuggerSettings;
  from fPrintExceptionInformation import fPrintExceptionInformation;
  from fatsArgumentLowerNameAndValue import fatsArgumentLowerNameAndValue;
  from mColors import *;
  
  if __name__ == "__main__":
    asTestedPythonVersions = ["3.9.1"];
    
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
    gsInternalErrorReportsFolder = os.path.join(os.path.dirname(__file__), "Internal error reports");
    
    def fTerminate(uExitCode):
      oConsole.fCleanup();
      if gbPauseBeforeExit:
        oConsole.fOutput("Press ENTER to quit...");
        input();
      os._exit(uExitCode);
    
    def fApplicationMaxRunTimeCallback(oBugId):
      oConsole.fOutput("+ T+%.1f The application has been running for %.1f seconds without crashing." % \
          (oBugId.fnApplicationRunTimeInSeconds(), dxConfig["nzApplicationMaxRunTimeInSeconds"]));
      oConsole.fOutput();
      oConsole.fStatus(INFO, "* BugId is stopping...");
      oBugId.fStop();
    
    def fApplicationResumedCallback(oBugId):
      oConsole.fStatus("* The application is running...");
    
    def fApplicationRunningCallback(oBugId):
      oConsole.fStatus("* The application was started successfully and is running...");
    
    def fApplicationSuspendedCallback(oBugId, sReason):
      oConsole.fStatus("* T+%.1f The application is suspended (%s)..." % (oBugId.fnApplicationRunTimeInSeconds(), sReason));
    
    def fFailedToDebugApplicationCallback(oBugId, sErrorMessage):
      global gbAnInternalErrorOccured;
      gbAnInternalErrorOccured = True;
      oConsole.fLock();
      try:
        oConsole.fOutput(ERROR, "\u250C\u2500", ERROR_INFO, " Failed to debug the application ", ERROR, sPadding = "\u2500");
        for sLine in sErrorMessage.split("\n"):
          oConsole.fOutput(ERROR, "\u2502 ", ERROR_INFO, sLine.rstrip("\r"));
        oConsole.fOutput(ERROR, "\u2514", sPadding = "\u2500");
        oConsole.fOutput();
      finally:
        oConsole.fUnlock();
    
    def fInternalExceptionCallback(oBugId, oThread, oException, oTraceBack):
      global gbAnInternalErrorOccured;
      gbAnInternalErrorOccured = True;
      fSaveInternalExceptionReportAndExit(oException, oTraceBack);
    
    def fSaveInternalExceptionReportAndExit(oException, oTraceBack):
      fPrintExceptionInformation(oException, oTraceBack);
      uIndex = 0;
      while True:
        uIndex += 1;
        sErrorReportFilePath = os.path.join(gsInternalErrorReportsFolder, "BugId error report #%d.txt" % uIndex);
        if not os.path.isfile(sErrorReportFilePath):
          break;
      oConsole.fStatus("Creating a copy of the error report in %s..." % (sErrorReportFilePath,));
      if oConsole.fbCopyOutputToFilePath(sErrorReportFilePath, bOverwrite = True, bThrowErrors = False):
        oConsole.fOutput("A copy of the error report can be found in ", INFO, sErrorReportFilePath, NORMAL, "...");
      oConsole.fCleanup();
      fTerminate(3);
    
    def fLicenseErrorsCallback(oBugId, asErrors):
      # These should have been reported before cBugId was even instantiated, so this is kind of unexpected.
      # But rather than raise AssertionError("NOT REACHED"), we'll report the license error gracefully:
      global gbAnInternalErrorOccured;
      gbAnInternalErrorOccured = True;
      oConsole.fLock();
      try:
        oConsole.fOutput(ERROR, "\u250C\u2500", ERROR_INFO, " Software license error ", ERROR, sPadding = "\u2500");
        for sError in asErrors:
          oConsole.fOutput(ERROR, "\u2502 ", ERROR_INFO, sError);
        oConsole.fOutput(ERROR, "\u2514", sPadding = "\u2500");
      finally:
        oConsole.fUnlock();
      fTerminate(5);
    
    def fLicenseWarningsCallback(oBugId, asWarnings):
      # These were already reported when BugId started; ignore them.
      pass;
    #  oConsole.fLock();
    #  try:
    #    oConsole.fOutput(WARNING, u"\u250C\u2500", WARNING_INFO, " Warning ", WARNING, sPadding = u"\u2500");
    #    for sWarning in asWarnings:
    #      oConsole.fOutput(WARNING, u"\u2502 ", WARNING_INFO, sWarning);
    #    oConsole.fOutput(WARNING, u"\u2514", sPadding = u"\u2500");
    #  finally:
    #    oConsole.fUnlock();
    
    def fCdbISANotIdealCallback(oBugId, oProcess, bIsMainProcess, sCdbISA, bPreventable):
      global \
          gasBinaryNamesThatAreAllowedToRunWithNonIdealCdbISA, \
          gasReportedBinaryNameWithNonIdealCdbISA, \
          gbAnInternalErrorOccured;
      sBinaryName = oProcess.sBinaryName;
      if sBinaryName.lower() in gasBinaryNamesThatAreAllowedToRunWithNonIdealCdbISA:
        return;
      if not bPreventable:
        if not gbQuiet and sBinaryName not in gasReportedBinaryNameWithNonIdealCdbISA:
          gasReportedBinaryNameWithNonIdealCdbISA.append(sBinaryName);
          oConsole.fLock();
          try:
            oConsole.fOutput(
              WARNING, "- You are debugging an ",
              WARNING_INFO, oProcess.sISA, WARNING, " process running ",
              WARNING_INFO, sBinaryName, WARNING, " with a ",
              WARNING_INFO, sCdbISA, WARNING, " cdb.exe."
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
            ERROR, "- You are debugging an ",
            ERROR_INFO, oProcess.sISA, WARNING, " process running ",
            ERROR_INFO, sBinaryName, WARNING, " with a ",
            ERROR_INFO, sCdbISA, WARNING, " cdb.exe."
          );
          oConsole.fOutput(
            "  You should use the ", INFO, "--isa=", oProcess.sISA, NORMAL, " command line argument to let BugId know",
            "it should be using a ", oProcess.sISA, " cdb.exe.");
          oConsole.fOutput("  Please restart BugId with the aboce command line argument to try again.");
          oConsole.fOutput();
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
          gasReportedLowercaseBinaryNamesWithoutPageHeap;
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
        oConsole.fOutput(WARNING, "- Full page heap is not enabled for ", WARNING_INFO, oProcess.sBinaryName,
                        WARNING, " in process ", WARNING_INFO, "0x%X" % oProcess.uId, WARNING, ".");
        if bPreventable:
          oConsole.fOutput("  Without page heap enabled, detection and anaylsis of any bugs will be sub-");
          oConsole.fOutput("  optimal. Please enable page heap to improve detection and analysis.");
          oConsole.fOutput();
          oConsole.fOutput("  You can enabled full page heap for ", sLowerBinaryName, " by running:");
          oConsole.fOutput();
          oConsole.fOutput("      ", INFO, 'PageHeap.cmd "', oProcess.sBinaryName, '" ON');
        else:
          oConsole.fOutput("  This appears to be due to a bug in page heap that prevents it from");
          oConsole.fOutput("  determining the binary name correctly. Unfortunately, there is no known fix");
          oConsole.fOutput("  or work-around for this. BugId will continue, but detection and analysis of");
          oConsole.fOutput("  any bugs in this process will be sub-optimal.");
        oConsole.fOutput();
      finally:
        oConsole.fUnlock();
    
    def fCdbStdInInputCallback(oBugId, sbInput):
      oConsole.fOutput(HILITE, "<stdin<", NORMAL, str(sbInput, 'latin1'), uConvertTabsToSpaces = 8);
    def fCdbStdOutOutputCallback(oBugId, sbOutput):
      oConsole.fOutput(HILITE, "stdout>", NORMAL, str(sbOutput, 'latin1'), uConvertTabsToSpaces = 8);
    def fCdbStdErrOutputCallback(oBugId, sbOutput):
      oConsole.fOutput(ERROR_INFO, "stderr>", ERROR, str(sbOutput, 'latin1'), uConvertTabsToSpaces = 8);
    def fLogMessageCallback(oBugId, sMessage, dsData = None):
      sData = dsData and ", ".join(["%s: %s" % (sName, sValue) for (sName, sValue) in dsData.items()]);
      oConsole.fOutput(DIM, "log>%s%s" % (sMessage, sData and " (%s)" % sData or ""));
    
    # Helper function to format messages that are specific to a process.
    def fPrintMessageForProcess(sHeaderChar, oProcess, bIsMainProcess, *tsMessage):
      # oProcess is a mWindowsAPI.cProcess or derivative.
      sIntegrityLevel = "?" if oProcess.uIntegrityLevel is None else (
        str(oProcess.uIntegrityLevel >> 12) +
        ("+" if oProcess.uIntegrityLevel & 0x100 else "")
      );
      axHeader = [
        sHeaderChar or " ", " ", bIsMainProcess and "Main" or "Sub", " process ",
        INFO, "%d" % oProcess.uId, NORMAL, "/", INFO , "0x%X" % oProcess.uId, 
        NORMAL, " (",
          INFO, oProcess.sBinaryName,
          NORMAL, ", ", INFO, oProcess.sISA,
          NORMAL, ", IL:", INFO, sIntegrityLevel,
        NORMAL, "): ",
      ];
      if sHeaderChar is None:
        # Just blanks for the header (used for multi-line output to reduce redundant output).
        oConsole.fOutput(
          " " * len("".join(s for s in axHeader if isinstance(s, str))),
          *tsMessage,
          uConvertTabsToSpaces = 8
        );
      else:
        oConsole.fOutput(
          axHeader,
          *tsMessage,
          uConvertTabsToSpaces = 8
        );
    
    def fFailedToApplyApplicationMemoryLimitsCallback(oBugId, oProcess, bIsMainProcess):
      global gbFailedToApplyMemoryLimitsErrorShown, gbQuiet, gbVerbose;
      if not gbQuiet:
        fPrintMessageForProcess("-", oProcess, bIsMainProcess,
            ERROR_INFO, "Cannot apply application memory limits");
        gbFailedToApplyMemoryLimitsErrorShown = True;
        if not gbVerbose:
          oConsole.fOutput("  Any additional failures to apply memory limits to processess will not be shown.");
    def fFailedToApplyProcessMemoryLimitsCallback(oBugId, oProcess, bIsMainProcess):
      global gbFailedToApplyMemoryLimitsErrorShown, gbVerbose;
      if gbVerbose or not gbFailedToApplyMemoryLimitsErrorShown:
        fPrintMessageForProcess("-", oProcess, bIsMainProcess,
            ERROR_INFO, "Cannot apply process memory limits");
        gbFailedToApplyMemoryLimitsErrorShown = True;
        if not gbVerbose:
          oConsole.fOutput("  Any additional failures to apply memory limits to processess will not be shown.");
    
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
    
    def fApplicationDebugOutputCallback(oBugId, oProcess, bIsMainProcess, asbMessages):
      uCount = 0;
      sDebug = "debug";
      oConsole.fLock();
      for sbMessage in asbMessages:
        uCount += 1;
        if uCount == 1:
          sHeader = "*";
          # we will create a box shape to show which messages belong together.
          # On the first line we will branch down and right if the message is multi-line.
          sPrefix = " " if len(asbMessages) == 1 else "\u252c";
        else:
          sHeader = None;
          # if more lines folow, show a vertical stripe, otherwise bend right on the last line
          sPrefix = "\u2514" if uCount == len(asbMessages) else "\u2502";
        fPrintMessageForProcess(sHeader, oProcess, bIsMainProcess,
          INFO, sDebug, NORMAL, sPrefix, HILITE, str(sbMessage, 'latin1'),
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
    def fASanDetectedCallback(oBugId, oProcess, bIsMainProcess):
      fPrintMessageForProcess("*", oProcess, bIsMainProcess, 
        " has ", INFO, "Address Sanitizer", NORMAL, " enabled."
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
             gduNumberOfRepros_by_sBugIdAndLocation, \
             gbAnInternalErrorOccured;
      guDetectedBugsCount += 1;
      oConsole.fLock();
      try:
        oConsole.fOutput("\u250C\u2500 ", HILITE, "A bug was detected ", NORMAL, sPadding = "\u2500");
        if oBugReport.sBugLocation:
          oConsole.fOutput("\u2502 Id @ Location:    ", INFO, oBugReport.sId, NORMAL, " @ ", INFO, oBugReport.sBugLocation);
          sBugIdAndLocation = "%s @ %s" % (oBugReport.sId, oBugReport.sBugLocation);
        else:
          oConsole.fOutput("\u2502 Id:               ", INFO, oBugReport.sId);
          sBugIdAndLocation = oBugReport.sId;
        gduNumberOfRepros_by_sBugIdAndLocation.setdefault(sBugIdAndLocation, 0);
        gduNumberOfRepros_by_sBugIdAndLocation[sBugIdAndLocation] += 1;
        if oBugReport.sBugSourceLocation:
          oConsole.fOutput("\u2502 Source:           ", INFO, oBugReport.sBugSourceLocation);
        oConsole.fOutput("\u2502 Description:      ", INFO, oBugReport.s0BugDescription or "None provided");
        oConsole.fOutput("\u2502 Security impact:  ", INFO, (oBugReport.s0SecurityImpact or "None"));
        if oBugReport.asVersionInformation:
          oConsole.fOutput("\u2502 Version:          ", NORMAL, oBugReport.asVersionInformation[0]); # The process' binary.
          for sVersionInformation in oBugReport.asVersionInformation[1:]: # There may be two if the crash was in a
            oConsole.fOutput("\u2502                   ", NORMAL, sVersionInformation); # different binary (e.g. a .dll)
        if dxConfig["bGenerateReportHTML"]:
          # Use a report file name base on the BugId.
          sDesiredReportFileName = "%s" % sBugIdAndLocation;
          # In collateral mode, we will number the reports so you know in which order bugs were reported.
          if guMaximumNumberOfBugs > 1:
            sDesiredReportFileName = "#%d %s" % (guDetectedBugsCount, sDesiredReportFileName);
          # Translate characters that are not valid in file names.
          sValidReportFileName = cFileSystemItem.fsGetValidName(sDesiredReportFileName, bUseUnicodeHomographs = dxConfig["bUseUnicodeReportFileNames"]);
          if dxConfig["sReportFolderPath"] is not None:
            sReportFilePath = os.path.join(dxConfig["sReportFolderPath"], sValidReportFileName + ".html");
          else:
            sReportFilePath = sValidReportFileName + ".html";
          oConsole.fStatus("\u2502 Bug report:       ", INFO, sValidReportFileName, ".html", NORMAL, "...");
          try:
            oReportFile = cFileSystemItem(sReportFilePath);
            sbReportHTML = bytes(oBugReport.sReportHTML, "utf-8")
            if oReportFile.fbIsFile(bParseZipFiles = True):
              oReportFile.fbWrite(sbReportHTML, bKeepOpen = False, bParseZipFiles = True, bThrowErrors = True);
            else:
              oReportFile.fbCreateAsFile(sbReportHTML, bCreateParents = True, bParseZipFiles = True, bKeepOpen = False, bThrowErrors = True);
          except Exception as oException:
            oConsole.fOutput("\u2502 ", ERROR, "Bug report:       ", ERROR_INFO, sValidReportFileName, ".html", ERROR, " not saved!");
            oConsole.fOutput("\u2502   Error:          ", ERROR_INFO, str(oException));
            gbAnInternalErrorOccured = True;
          else:
            oConsole.fOutput("\u2502 Bug report:       ", INFO, sValidReportFileName, ".html", NORMAL, ".");
          if gbSaveOutputWithReport:
            if dxConfig["sReportFolderPath"] is not None:
              sLogOutputFilePath = os.path.join(dxConfig["sReportFolderPath"], sValidReportFileName + " BugId output.txt");
            else:
              sLogOutputFilePath = sValidReportFileName + " BugId output.txt";
            oConsole.fStatus("\u2502 BugId output log: ", INFO, sValidReportFileName, ".txt", NORMAL, "...");
            try:
              oConsole.fbCopyOutputToFilePath(sLogOutputFilePath);
            except Exception as oException:
              oConsole.fCleanup();
              oConsole.fOutput("\u2502 BugId output log: ", ERROR_INFO, sValidReportFileName, ".txt", ERROR, " not saved!");
              oConsole.fOutput("\u2502   Error:          ", ERROR_INFO, str(oException));
              gbAnInternalErrorOccured = True;
            else:
              oConsole.fOutput("\u2502 BugId output log: ", INFO, sValidReportFileName, ".txt", NORMAL, ".");
          if gbSaveDump:
            sValidDumpFileName = "".join([sChar if 0x20 <= ord(sChar) < 0x7F else "." for sChar in sValidReportFileName]);
            if dxConfig["sReportFolderPath"] is not None:
              sDumpFilePath = os.path.join(dxConfig["sReportFolderPath"], sValidDumpFileName + ".dmp");
            else:
              sDumpFilePath = sValidDumpFileName + ".dmp";
            oConsole.fStatus("\u2502 Dump file:        ", INFO, sValidDumpFileName, ".dmp", NORMAL, "...");
            oBugId.fSaveDumpToFile(sDumpFilePath, True, gbSaveFullDump);
            oConsole.fOutput("\u2502 Dump file:        ", INFO, sValidDumpFileName, ".dmp", NORMAL, ".");
        oConsole.fOutput("\u2514", sPadding = "\u2500");
      finally:
        oConsole.fUnlock();
    
    def fMain():
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
        oConsole.fOutput(ERROR, "Error: unfortunately BugId only runs on Windows 10 at this time.");
        fTerminate(3);
      if mWindowsAPI.oSystemInfo.sOSISA == "x64" and mWindowsAPI.fsGetPythonISA() == "x86":
        oConsole.fLock();
        try:
          oConsole.fOutput(WARNING, "\u250C\u2500", WARNING_INFO, " Warning ", WARNING, sPadding = "\u2500");
          oConsole.fOutput(WARNING, "\u2502 You are running a ", WARNING_INFO, "32-bit", WARNING, " version of Python on a ",
              WARNING_INFO, "64-bit", WARNING, " version of Windows.");
          oConsole.fOutput(WARNING, "\u2502 BugId will not be able to debug 64-bit applications unless you run it in a 64-bit " +
              "version of Python.");
          oConsole.fOutput(WARNING, "\u2502 If you experience any issues, use a 64-bit version of Python and try again.");
          oConsole.fOutput(WARNING, "\u2514", sPadding = "\u2500");
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
      bRepeat = False;
      uNumberOfRepeats = None;
      bCheckForUpdates = False;
      dxUserProvidedConfigSettings = {};
      asAdditionalLocalSymbolPaths = [];
      bFast = False;
      a0sJITDebuggerArguments = None;
      for (sArgument, s0LowerName, s0Value) in fatsArgumentLowerNameAndValue():
        if a0sJITDebuggerArguments is not None:
          # Stop processing arguments after "-I"
          a0sJITDebuggerArguments.append(sArgument);
          continue;
        if s0LowerName in ["q", "quiet"]:
          if s0Value is None or s0Value.lower() == "true":
            gbQuiet = True;
          elif s0Value.lower() == "false":
            gbQuiet = False;
          else:
            oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
                " must be \"", ERROR_INFO, "true", ERROR, "\" (default) or \"", ERROR_INFO, "false", ERROR, "\".");
            fTerminate(2);
        elif s0LowerName in ["v", "verbose"]:
          if s0Value is None or s0Value.lower() == "true":
            gbVerbose = True;
          elif s0Value.lower() == "false":
            gbVerbose = False;
          else:
            oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
                " must be \"", ERROR_INFO, "true", ERROR, "\" (default) or \"", ERROR_INFO, "false", ERROR, "\".");
            fTerminate(2);
        elif s0LowerName in ["p", "pause"]:
          if s0Value is None or s0Value.lower() == "true":
            gbPauseBeforeExit = True;
          elif s0Value.lower() == "false":
            gbPauseBeforeExit = False;
          else:
            oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
                " must be \"", ERROR_INFO, "true", ERROR, "\" (default) or \"", ERROR_INFO, "false", ERROR, "\".");
            fTerminate(2);
        elif s0LowerName in ["f", "fast", "quick"]:
          if s0Value is None or s0Value.lower() == "true":
            bFast = True;
          elif s0Value.lower() == "false":
            bFast = False;
          else:
            oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
                " must be \"", ERROR_INFO, "true", ERROR, "\" (default) or \"", ERROR_INFO, "false", ERROR, "\".");
            fTerminate(2);
        elif s0LowerName in ["r", "repeat", "forever"]:
          if s0Value is None or s0Value.lower() == "true":
            bRepeat = True;
          elif s0Value.lower() == "false":
            bRepeat = False;
          elif s0LowerName in ["forever"]:
            oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
                " must be \"", ERROR_INFO, "true", ERROR, "\" (default) or \"", ERROR_INFO, "false", ERROR, "\".");
            fTerminate(2);
          else:
            bRepeat = True;
            try:
              uNumberOfRepeats = int(s0Value);
              if uNumberOfRepeats < 2:
                uNumberOfRepeats = None;
              elif str(uNumberOfRepeats) != s0Value:
                uNumberOfRepeats = None;
            except:
              uNumberOfRepeats = None;
            if uNumberOfRepeats is None:
              oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
                  " must be \"", ERROR_INFO, "true", ERROR, "\" (default), \"", ERROR_INFO, "false", ERROR, "\", or ",
                  ERROR_INFO, "an integer larger than 1", ERROR, ".");
              fTerminate(2);
        elif s0LowerName in ["d", "dump", "full-dump"]:
          if s0Value is None or s0Value.lower() == "true":
            gbSaveDump = True;
            if s0LowerName in ["full-dump"]:
              gbSaveFullDump = True; # --full-dump[=true] enables dump & full dump
          elif s0Value.lower() == "false":
            if s0LowerName in ["full-dump"]:
              gbSaveFullDump = False; # --full-dump=false disables full dump only (not dump)
            else:
              gbSaveDump = False;
          else:
            oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
                " must be \"", ERROR_INFO, "true", ERROR, "\" (default) or \"", ERROR_INFO, "false", ERROR, "\".");
            fTerminate(2);
        elif s0LowerName in ["i"]:
          if s0Value is not None:
            oConsole.fOutput(ERROR, "- The option ", ERROR_INFO, sArgument, ERROR, " does not accept a value.")
            fTerminate(2);
          # Install as JIT Debugger. Remaining arguments are passed on the command line to the JIT debugger.
          a0sJITDebuggerArguments = []; # Remaining arguments will be added to this list.
        elif s0LowerName in ["c", "collateral"]:
          if s0Value is None:
            guMaximumNumberOfBugs = guDefaultCollateralMaximumNumberOfBugs;
          else:
            # -- collateral=1 means one collateral bug in addition to the first bug.
            try:
              guMaximumNumberOfBugs = int(s0Value) + 1;
              if guMaximumNumberOfBugs < 1:
                guMaximumNumberOfBugs = None;
            except:
              guMaximumNumberOfBugs = None;
            if guMaximumNumberOfBugs is None:
              oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
                  " must be empty or ", ERROR_INFO, "an integer larger than 0", ERROR, ".");
              fTerminate(2);
        elif s0LowerName in ["pid", "pids"]:
          if not s0Value:
            oConsole.fOutput(ERROR, "- You must provide at least one process id.");
            fTerminate(2);
          if s0ApplicationBinaryPath is not None:
            oConsole.fOutput(ERROR, "- You cannot provide an application binary and process ids.");
            fTerminate(2);
          if o0UWPApplication is not None:
            oConsole.fOutput(ERROR, "- You cannot provide UWP application details and process ids.");
            fTerminate(2);
          for sPid in s0Value.split(","):
            try:
              auApplicationProcessIds.append(int(sPid));
            except ValueError:
              oConsole.fOutput(ERROR, "- You cannot provide ", ERROR_INFO, repr(sPid), ERROR, " as a process ids, as it is not a number.");
              oConsole.fOutput(ERROR, "  Full argument: ", ERROR_INFO, repr(sArgument), ERROR, ".");
              fTerminate(2);
        elif s0LowerName in ["handle-jit-event"]:
          if not s0Value:
            oConsole.fOutput(ERROR, "- No event handle provided!");
            fTerminate(2);
          u0JITDebuggerEventId = int(s0Value);
        elif s0LowerName in ["uwp", "uwp-app"]:
          if not s0Value:
            oConsole.fOutput(ERROR, "- You must provide UWP application details.");
            fTerminate(2);
          if o0UWPApplication is not None:
            oConsole.fOutput(ERROR, "- You cannot provide UWP application details more than once.");
            fTerminate(2);
          if s0ApplicationBinaryPath is not None:
            oConsole.fOutput(ERROR, "- You cannot provide an application binary and UWP application details.");
            fTerminate(2);
          if len(auApplicationProcessIds) > 0:
            oConsole.fOutput(ERROR, "- You cannot provide process ids and UWP application details.");
            fTerminate(2);
          tsUWPApplicationPackageNameAndId = s0Value.split("!", 1);
          sUWPApplicationPackageName = tsUWPApplicationPackageNameAndId[0];
          sUWPApplicationId = tsUWPApplicationPackageNameAndId[1] if len(tsUWPApplicationPackageNameAndId) == 2 else None;
          o0UWPApplication = mWindowsAPI.cUWPApplication(sUWPApplicationPackageName, sUWPApplicationId);
        elif s0LowerName in ["jit"]:
          fPrintCurrentJITDebuggerSettings();
          fTerminate(0);
        elif s0LowerName in ["log-output"]:
          gbSaveOutputWithReport = True;
        elif s0LowerName in ["isa", "cpu"]:
          if not s0Value:
            oConsole.fOutput(ERROR, "- You must provide an Instruction Set Architecture.");
            fTerminate(2);
          if s0Value not in ["x86", "x64"]:
            oConsole.fOutput(ERROR, "- Unknown Instruction Set Architecture ", repr(s0Value));
            fTerminate(2);
          sApplicationISA = s0Value;
        elif s0LowerName in ["symbols"]:
          if s0Value is None or not cFileSystemItem(s0Value).fbIsFolder():
            oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
                " must be a valid folder path.");
            fTerminate(2);
          asAdditionalLocalSymbolPaths.append(s0Value);
        elif s0LowerName in ["report", "reports", "report-folder", "reports-folder", "report-folder-path", "reports-folder-path"]:
          if s0Value is None:
            oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
                " must be a valid folder path.");
            fTerminate(2);
          oReportFolder = cFileSystemItem(s0Value);
          if not oReportFolder.fbIsFolder(bParseZipFiles = True) and not oReportFolder.fbCreateAsFolder(bCreateParents = True, bParseZipFiles = True):
            oConsole.fOutput(ERROR, "- The folder ", ERROR_INFO, s0Value, ERROR, " does not exist and cannot be created.");
            fTerminate(2);
          dxConfig["sReportFolderPath"] = s0Value;
        elif s0LowerName in ["test-internal-error", "internal-error-test"]:
          raise Exception("Testing internal error");
        elif s0LowerName:
          if not s0Value:
            oConsole.fOutput(ERROR, "- You cannot provide an argument (", ERROR_INFO, sArgument, ERROR, \
                ") without a value.");
            fTerminate(2);
          try:
            xValue = json.loads(s0Value);
          except ValueError as oError:
            oConsole.fOutput(ERROR, "- Cannot decode argument JSON value ", ERROR_INFO, sArgument, ERROR, "=", \
                ERROR_INFO, s0Value, ERROR, ": ", ERROR_INFO, " ".join(oError.args), ERROR, ".");
            fTerminate(2);
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
                oConsole.fOutput(ERROR, "- Unknown application keyword ", ERROR_INFO, sApplicationKeyword, ERROR, ".");
                fTerminate(2);
              fPrintApplicationKeyWordHelp(sApplicationKeyword, dxApplicationSettings);
              fTerminate(0);
            else:
              if len(auApplicationProcessIds) > 0:
                oConsole.fOutput(ERROR, "- You cannot provide process ids and an application binary.");
                fTerminate(2);
              if o0UWPApplication is not None:
                oConsole.fOutput(ERROR, "- You cannot provide an application UWP package name and a binary.");
                fTerminate(2);
              s0ApplicationBinaryPath = sArgument;
          else:
            oConsole.fOutput(ERROR, "- Unknown argument: ", ERROR_INFO, sArgument, ERROR, ".");
        else: # After "--":
          if len(auApplicationProcessIds) > 0:
            oConsole.fOutput(ERROR, "- You cannot provide process ids and application arguments.");
            fTerminate(2);
          asApplicationOptionalArguments.append(sArgument);
      
      if a0sJITDebuggerArguments is not None:
        if fbInstallAsJITDebugger(a0sJITDebuggerArguments):
          fTerminate(0);
        fTerminate(3);
      if bFast:
        gbQuiet = True;
        dxUserProvidedConfigSettings["bGenerateReportHTML"] = False;
        dxUserProvidedConfigSettings["azsSymbolServerURLs"] = [];
        dxUserProvidedConfigSettings["cBugId.bUse_NT_SYMBOL_PATH"] = False;
      
      if u0JITDebuggerEventId is not None and dxConfig["sReportFolderPath"] is None:
        oConsole.fOutput(ERROR, "- JIT debugging is not possible without providing a value for ", ERROR_INFO, "sReportFolderPath", ERROR, ".");
        fTerminate(2);
      
      dsApplicationURLTemplate_by_srSourceFilePath = {};
      
      if gbSaveOutputWithReport:
        oConsole.fEnableLog();
      
      fSetup = None; # Function specific to a keyword application, used to setup stuff before running.
      fCleanup = None; # Function specific to a keyword application, used to cleanup stuff before & after running.
      if s0ApplicationKeyword:
        dxApplicationSettings = ddxApplicationSettings_by_sKeyword.get(s0ApplicationKeyword);
        if not dxApplicationSettings:
          oConsole.fOutput(ERROR, "- Unknown application keyword ", ERROR_INFO, s0ApplicationKeyword, ERROR, ".");
          fTerminate(2);
        fSetup = dxApplicationSettings.get("fSetup");
        fCleanup = dxConfig["bCleanup"] and dxApplicationSettings.get("fCleanup");
        # Get application binary/UWP package name/process ids as needed:
        if "sBinaryPath" in dxApplicationSettings:
          # This application is started from the command-line.
          if auApplicationProcessIds:
            oConsole.fOutput(ERROR, "- You cannot provide process ids for application keyword ", ERROR_INFO, \
                s0ApplicationKeyword, ERROR, ".");
            fTerminate(2);
          if o0UWPApplication:
            oConsole.fOutput(ERROR, "- You cannot provide an application UWP package name for application keyword ", \
                ERROR_INFO, s0ApplicationKeyword, ERROR, ".");
            fTerminate(2);
          if s0ApplicationBinaryPath is None:
            s0ApplicationBinaryPath = dxApplicationSettings["sBinaryPath"];
            if s0ApplicationBinaryPath is None:
              oConsole.fOutput(ERROR, "- The main application binary for ", ERROR_INFO, s0ApplicationKeyword, \
                  ERROR, " could not be detected on your system.");
              oConsole.fOutput(ERROR, "  Please provide the path to this binary in the arguments.");
              fTerminate(4);
        elif "dxUWPApplication" in dxApplicationSettings:
          dxUWPApplication = dxApplicationSettings["dxUWPApplication"];
          # This application is started as a Universal Windows Platform application.
          if s0ApplicationBinaryPath:
            oConsole.fOutput(ERROR, "- You cannot provide an application binary for application keyword ", \
                ERROR_INFO, s0ApplicationKeyword, ERROR, ".");
            fTerminate(2);
          if auApplicationProcessIds:
            oConsole.fOutput(ERROR, "- You cannot provide process ids for application keyword ", ERROR_INFO, \
                s0ApplicationKeyword, ERROR, ".");
            fTerminate(2);
          sUWPApplicationPackageName = dxUWPApplication["sPackageName"];
          sUWPApplicationId = dxUWPApplication["sId"];
          o0UWPApplication = mWindowsAPI.cUWPApplication(sUWPApplicationPackageName, sUWPApplicationId);
        elif not auApplicationProcessIds:
          # This application is attached to.
          oConsole.fOutput(ERROR, "- You must provide process ids for application keyword ", \
              ERROR_INFO, s0ApplicationKeyword, ERROR, ".");
          fTerminate(2);
        elif asApplicationOptionalArguments:
          # Cannot provide arguments if we're attaching to processes
          oConsole.fOutput(ERROR, "- You cannot provide arguments for application keyword ", \
              ERROR_INFO, s0ApplicationKeyword, ERROR, ".");
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
          asApplicationOptionalArguments = fasGetApplicationOptionalArguments(dxConfig, bForHelp = False);
        asApplicationArguments = asApplicationStaticArguments + asApplicationOptionalArguments;
        # Apply application specific settings
        if dxApplicationSettings.get("dxConfigSettings"):
          dxApplicationConfigSettings = dxApplicationSettings["dxConfigSettings"];
          if gbVerbose:
            oConsole.fOutput("* Applying application specific configuration for %s:" % s0ApplicationKeyword);
          for (sSettingName, xValue) in dxApplicationConfigSettings.items():
            if sSettingName not in dxUserProvidedConfigSettings:
              # Apply and show result indented or errors.
              if not fbApplyConfigSetting(sSettingName, xValue, [None, "  "][gbVerbose]):
                fTerminate(2);
          if gbVerbose:
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
          oConsole.fOutput(ERROR, "- You must provide something to debug. This can be either one or more process");
          oConsole.fOutput(ERROR, "  ids, an application command-line or an UWP application package name.");
          oConsole.fOutput("Run \"", INFO, "BugId -h", NORMAL, "\" for help on command-line arguments.");
        finally:
          oConsole.fUnlock();
        fTerminate(2);
      
      # Check that the UWP application exists if needed.
      if o0UWPApplication:
        if not o0UWPApplication.bPackageExists:
          oConsole.fOutput(ERROR, "- UWP application package ", ERROR_INFO, o0UWPApplication.sPackageName,
              ERROR, " does not exist.");
          fTerminate(2);
        elif not o0UWPApplication.bIdExists:
          oConsole.fOutput(ERROR, "- UWP application package ", ERROR_INFO, o0UWPApplication.sPackageName,
              ERROR, " does not contain an application with id ", ERROR_INFO, o0UWPApplication.sApplicationId,
              ERROR, ".");
          fTerminate(2);
      # Apply user provided settings:
      for (sSettingName, xValue) in list(dxUserProvidedConfigSettings.items()):
        # Apply and show result or errors:
        if not fbApplyConfigSetting(sSettingName, xValue, [None, ""][gbVerbose]):
          fTerminate(2);
      
      # Check if cdb.exe is found:
      sCdbISA = sApplicationISA or cBugId.sOSISA;
      if not cBugId.fbCdbFound(sCdbISA):
        oConsole.fLock();
        try:
          oConsole.fOutput(ERROR, "- BugId depends on ", ERROR_INFO, "Debugging Tools for Windows", ERROR, " which was not found.");
          oConsole.fOutput();
          oConsole.fOutput("To install, download the Windows 10 SDK installer at:");
          oConsole.fOutput();
          oConsole.fOutput("  ", INFO, "https://developer.microsoft.com/en-US/windows/downloads/windows-10-sdk");
          oConsole.fOutput();
          oConsole.fOutput("After downloading, run the installer. You can deselect all other features");
          oConsole.fOutput("of the SDK before installation; only ", INFO, "Debugging Tools for Windows", NORMAL, " is required.");
          oConsole.fOutput();
          oConsole.fOutput("Once you have completed these steps, please try again.");
        finally:
          oConsole.fUnlock();
        fTerminate(2);
      
      # Check license
      (asLicenseErrors, asLicenseWarnings) = mProductDetails.ftasGetLicenseErrorsAndWarnings();
      if asLicenseErrors:
        oConsole.fLock();
        try:
          oConsole.fOutput(ERROR, "\u250C\u2500", ERROR_INFO, " Software license error ", ERROR, sPadding = "\u2500");
          for sLicenseError in asLicenseErrors:
            oConsole.fOutput(ERROR, "\u2502 ", ERROR_INFO, sLicenseError);
          oConsole.fOutput(ERROR, "\u2514", sPadding = "\u2500");
        finally:
          oConsole.fUnlock();
        fTerminate(5);
      if asLicenseWarnings:
        oConsole.fLock();
        try:
          oConsole.fOutput(WARNING, "\u250C\u2500", WARNING_INFO, " Software license warning ", WARNING, sPadding = "\u2500");
          for sLicenseWarning in asLicenseWarnings:
            oConsole.fOutput(WARNING, "\u2502 ", WARNING_INFO, sLicenseWarning);
          oConsole.fOutput(WARNING, "\u2514", sPadding = "\u2500");
        finally:
          oConsole.fUnlock();
      
      asLocalSymbolPaths = dxConfig["a0sLocalSymbolPaths"] or [];
      if asAdditionalLocalSymbolPaths:
        asLocalSymbolPaths += asAdditionalLocalSymbolPaths;
      uRunCounter = 0;
      while 1: # Will only loop if bRepeat is True
        nStartTimeInSeconds = time.time();
        if fSetup:
          # Call setup before the application is started. Argument is boolean value indicating if this is the first time
          # the function is being called.
          oConsole.fStatus("* Applying special application configuration settings...");
          fSetup(bFirstRun = uRunCounter == 0);
        uRunCounter += 1;
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
          uMaximumNumberOfBugs = guMaximumNumberOfBugs,
        );
        oConsole.fLock();
        try:
          if s0ApplicationBinaryPath:
            # make the binary path absolute because relative paths don't work.
            s0ApplicationBinaryPath = os.path.abspath(s0ApplicationBinaryPath);
            if not gbQuiet:
              asCommandLine = [s0ApplicationBinaryPath] + asApplicationArguments;
              oConsole.fOutput("* Command line: ", INFO, " ".join(asCommandLine));
            oConsole.fStatus("* The debugger is starting the application...");
          else:
            if auApplicationProcessIds:
              asProcessIdsOutput = [];
              for uApplicationProcessId in auApplicationProcessIds:
                if asProcessIdsOutput: asProcessIdsOutput.append(", ");
                asProcessIdsOutput.extend([INFO, str(uApplicationProcessId), NORMAL]);
              oConsole.fOutput("* Running process ids: ", INFO, *asProcessIdsOutput);
            if o0UWPApplication and not gbQuiet:
              oConsole.fOutput(*(
                ["* UWP application id: ", INFO, oBugId.o0UWPApplication.sApplicationId, NORMAL] +
                [", package name: ", INFO, oBugId.o0UWPApplication.sPackageName, NORMAL] +
                ([", Arguments: ", INFO, " ".join(asApplicationArguments), NORMAL] if asApplicationArguments else []) +
                ["."]
              ));
            if not o0UWPApplication:
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
        oBugId.fAddCallback("ASan detected", fASanDetectedCallback);
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
        
        if fbIsProvided(dxConfig["nzApplicationMaxRunTimeInSeconds"]):
          oBugId.foSetTimeout(
            sDescription = "Maximum application runtime",
            nTimeoutInSeconds = dxConfig["nzApplicationMaxRunTimeInSeconds"],
            f0Callback = fApplicationMaxRunTimeCallback,
         );
        if dxConfig["bExcessiveCPUUsageCheckEnabled"] and dxConfig["nExcessiveCPUUsageCheckInitialTimeoutInSeconds"]:
          oBugId.fSetCheckForExcessiveCPUUsageTimeout(dxConfig["nExcessiveCPUUsageCheckInitialTimeoutInSeconds"]);
        guDetectedBugsCount = 0;
        oBugId.fStart();
        oBugId.fWait();
        if gbAnInternalErrorOccured:
          if fCleanup:
            # Call cleanup after runnning the application, before exiting BugId
            oConsole.fStatus("* Cleaning up application state...");
            fCleanup();
          fTerminate(3);
        if guDetectedBugsCount == 0:
          oConsole.fOutput("\u2500\u2500 The application terminated without a bug being detected ", sPadding = "\u2500");
          gduNumberOfRepros_by_sBugIdAndLocation.setdefault("No crash", 0);
          gduNumberOfRepros_by_sBugIdAndLocation["No crash"] += 1;
        if gbVerbose:
          oConsole.fOutput("  Application time: %s seconds" % (int(oBugId.fnApplicationRunTimeInSeconds() * 1000) / 1000.0));
          nOverheadTimeInSeconds = time.time() - nStartTimeInSeconds - oBugId.fnApplicationRunTimeInSeconds();
          oConsole.fOutput("  BugId overhead:   %s seconds" % (int(nOverheadTimeInSeconds * 1000) / 1000.0));
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
        sStatisticsFileName = "Reproduction statistics.txt";
        if dxConfig["sReportFolderPath"] is not None:
          sStatisticsFilePath = os.path.join(dxConfig["sReportFolderPath"], sStatisticsFileName);
        else:
          sStatisticsFilePath = sStatisticsFileName;
        try:
          oStatisticsFile = cFileSystemItem(sStatisticsFilePath);
          if oStatisticsFile.fbIsFile(bParseZipFiles = True):
            oStatisticsFile.fbWrite(sStatistics, bKeepOpen = False, bParseZipFiles = True, bThrowErrors = True);
          else:
            oStatisticsFile.fbCreateAsFile(sStatistics, bCreateParents = True, bParseZipFiles = True, bKeepOpen = False, bThrowErrors = True);
        except Exception as oException:
          oConsole.fOutput("  Statistics:       ", ERROR, "Cannot be saved (", ERROR_INFO, str(oException), ERROR, ")");
        else:
          oConsole.fOutput("  Statistics:       ", INFO, sStatisticsFilePath, NORMAL, " (%d bytes)" % len(sStatistics));
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
      oConsole.fOutput("+ Interrupted.");
    except Exception as oException:
      gbAnErrorOccured = True;
      cException, oException, oTraceBack = sys.exc_info();
      fSaveInternalExceptionReportAndExit(oException, oTraceBack);
except Exception as oException:
  if m0DebugOutput:
    m0DebugOutput.fTerminateWithException(oException);
  raise;
