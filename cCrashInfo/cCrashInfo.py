import os, re, subprocess, threading, time;

from cCrashInfo_foCdbRunApplicationAndGetErrorReport import cCrashInfo_foCdbRunApplicationAndGetErrorReport;
from dxCrashInfoConfig import dxCrashInfoConfig;

sOSISA = os.getenv("PROCESSOR_ARCHITEW6432") or os.getenv("PROCESSOR_ARCHITECTURE"); # "x86" or "AMD64"
sMicrosoftSymbolServerURL = "http://msdl.microsoft.com/download/symbols";

class cCrashInfo(object):
  def __init__(oCrashInfo, asApplicationCommandLine, auApplicationProcessIds, asSymbolServerURLs, \
      fApplicationRunningCallback, fExceptionDetectedCallback, fFinishedCallback, fInternalExceptionCallback):
    oCrashInfo._fApplicationRunningCallback = fApplicationRunningCallback;
    oCrashInfo._fExceptionDetectedCallback = fExceptionDetectedCallback;
    oCrashInfo._fFinishedCallback = fFinishedCallback;
    oCrashInfo._fInternalExceptionCallback = fInternalExceptionCallback;
    oCrashInfo.dafEventCallbacks_by_sEventName = {
      "load module": set(),
    };
    uSymbolOptions = sum([
      0x00000001, # SYMOPT_CASE_INSENSITIVE
      0x00000002, # SYMOPT_UNDNAME
      0x00000004, # SYMOPT_DEFERRED_LOAD
#      0x00000020, # SYMOPT_OMAP_FIND_NEAREST
#      0x00000040, # SYMOPT_LOAD_ANYTHING
      0x00000100, # SYMOPT_NO_UNQUALIFIED_LOADS
      0x00000200, # SYMOPT_FAIL_CRITICAL_ERRORS
      0x00000400, # SYMOPT_EXACT_SYMBOLS
      0x00000800, # SYMOPT_ALLOW_ABSOLUTE_SYMBOLS
      0x00010000, # SYMOPT_AUTO_PUBLICS
#      0x00020000, # SYMOPT_NO_IMAGE_SEARCH
      0x00080000, # SYMOPT_NO_PROMPTS
      dxCrashInfoConfig["bEnhancedSymbolLoading"] and 0x80000000 or 0, # SYMOPT_DEBUG
    ]);
    oCrashInfo.sCdbISA = sOSISA;
    oCrashInfo._sCurrentISA = None;
    sCdbBinaryPath = dxCrashInfoConfig["sCdbBinaryPath_%s" % sOSISA];
    asCommandLine = [sCdbBinaryPath, "-o", "-sflags", "0x%08X" % uSymbolOptions];
    # -o => debug child processes, -sflags 0xXXXXXXXX => symbol options:
    set_asSymbolServerURLs = set(asSymbolServerURLs + [sMicrosoftSymbolServerURL]);
    sSymbolsPath = ";".join(
      ["cache*%s" % sSymbolCachePath for sSymbolCachePath in dxCrashInfoConfig["asSymbolCachePaths"]] +
      ["srv*%s" % sSymbolServerURL for sSymbolServerURL in set_asSymbolServerURLs]
    );
    asCommandLine.extend(["-y", sSymbolsPath]);
    if asApplicationCommandLine is not None:
      asCommandLine += asApplicationCommandLine;
    oCrashInfo._auProcessIds = [];
    oCrashInfo._auProcessIdsPendingAttach = [];
    oCrashInfo._auApplicationProcessIds = auApplicationProcessIds; # TODO: remove once bug has been fixed.
    if auApplicationProcessIds is not None and len(auApplicationProcessIds) > 0:
      asCommandLine += ["-p", str(auApplicationProcessIds[0])];
      oCrashInfo._auProcessIdsPendingAttach = auApplicationProcessIds;
    
    asCommandLine = [
      (sArg.find(" ") == -1 or sArg[0] == '"')        and sArg               or '"%s"' % sArg.replace('"', '\\"')
      for sArg in asCommandLine
    ];
    if dxCrashInfoConfig["bOutputCommandLine"]:
      print "* Starting %s" % " ".join(asCommandLine);
    oCrashInfo._asCdbStdIO = [];
    oCrashInfo._asCdbStdErr = [];
    oCrashInfo._oErrorReport = None;
    oCrashInfo._uLastProcessId = None;
    oCrashInfo._oCdbProcess = subprocess.Popen(args = " ".join(asCommandLine), stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE);
    oCrashInfo._bCdbRunning = True;
    oCrashInfo._bCdbTerminated = False;
    # Create a thread that interacts with the debugger to debug the application
    oCrashInfo._oCdbDebuggerThread = threading.Thread(target = oCrashInfo._fCdbDebuggerThread);
    oCrashInfo._oCdbDebuggerThread.start();
    # Create a thread that reads stderr output and shows it in the console
    oCrashInfo._oCdbStdErrThread = threading.Thread(target = oCrashInfo._fCdbStdErrThread);
    oCrashInfo._oCdbStdErrThread.start();
    # Create a thread that waits for the debugger to terminate and cleans up after it.
    oCrashInfo._oCdbCleanupThread = threading.Thread(target = oCrashInfo._fCdbCleanupThread);
    oCrashInfo._oCdbCleanupThread.start();
    # NB. The above two are separated to make handling exceptions in the code run in the first thread possible without
    # the code running in the second thread interfering. If both were in the same thread, the cleanup code would have
    # to intercept exceptions from the debug code to make sure the cleanup code is always run. It would need to do the
    # cleanup before throwing the original exception again to make sure the exception is visible to the user. This is
    # complex and any exception thrown in the cleanup code would prevent the original exception from the debug code
    # from getting thrown, potentially hiding the root cause of all these exceptions. This has happened before, hence
    # the two threads solution.
  
  def __del__(oCrashInfo):
    # Check to make sure the debugger process is not running
    oProcess = oCrashInfo._oCdbProcess;
    if oProcess is not None and oProcess.poll() == None:
        print "*** INTERNAL ERROR: CrashInfo was not stopped, the cdb process is still running.";
  
  def fStop(oCrashInfo):
    oCrashInfo._bCdbTerminated = True;
    oCrashInfo._oCdbProcess.terminate();
    oCrashInfo._oCdbDebuggerThread.join();
    oCrashInfo._oCdbCleanupThread.join();
  
  def fFireEvent(oCrashInfo, sEventName, *axEventInforamtion):
    for fEventCallback in oCrashInfo.dafEventCallbacks_by_sEventName[sEventName]:
      fEventCallback(oCrashInfo, *axEventInforamtion);
  
  def _fCdbDebuggerThread(oCrashInfo):
    try:
      # Read the initial cdb output related to starting/attaching to the first process.
      asIntialOutput = oCrashInfo._fasReadOutput();
      if not oCrashInfo._bCdbRunning: return;
      oCrashInfo._oErrorReport = cCrashInfo_foCdbRunApplicationAndGetErrorReport(oCrashInfo, asIntialOutput);
    except Exception, oException:
      oCrashInfo._fInternalExceptionCallback(oException);
      oCrashInfo._bCdbTerminated = True;
      oCrashInfo._oCdbProcess.terminate();
      raise;
  
  def _fCdbCleanupThread(oCrashInfo):
    try:
      # wait for debugger thread to terminate.
      oCrashInfo._oCdbDebuggerThread.join();
      # wait for stderr thread to terminate.
      oCrashInfo._oCdbStdErrThread.join();
      # wait for debugger to terminate.
      oCrashInfo._oCdbProcess.wait();
      # wait for any processes that were being debugged to terminate
      sTasklistBinaryPath = os.path.join(os.getenv("WinDir"), "System32", "tasklist.exe");
      # The last process that terminated was open when cdb reported it and may not have been closed by the OS yet.
      # It needs to be added to the list of processes that need to terminate before debugging is truely finished.
      if oCrashInfo._uLastProcessId is not None:
        oCrashInfo._auProcessIds.append(oCrashInfo._uLastProcessId);
      while oCrashInfo._auProcessIds:
        uProcessId = oCrashInfo._auProcessIds.pop();
        while 1:
          sCommand = '%s /FI "PID eq %d" /NH /FO CSV' % (sTasklistBinaryPath, uProcessId);
          oTaskListProcess = subprocess.Popen(args=sCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE);
          sStdOut, sStdErr = oTaskListProcess.communicate(input=None);
          oTaskListProcess.stdout.close();
          oTaskListProcess.stderr.close();
          oTaskListProcess.terminate();
          assert not sStdErr, "Error running tasklist.exe: %s" % repr(sStdErr);
          if sStdOut != "INFO: No tasks are running which match the specified criteria.\r\n":
            time.sleep(0.1);
          else:
            break;
      # report that we're finished.
      oCrashInfo._fFinishedCallback(oCrashInfo._oErrorReport);
    except Exception, oException:
      oCrashInfo._fInternalExceptionCallback(oException);
      raise;
  
  def _fCdbStdErrThread(oCrashInfo):
    sLine = "";
    while 1:
      sChar = oCrashInfo._oCdbProcess.stderr.read(1);
      if sChar == "\r":
        pass; # ignored.
      elif sChar in ("\n", ""):
        if sChar == "\n" or sLine:
          oCrashInfo._asCdbStdErr.append(sLine);
          if dxCrashInfoConfig["bOutputErrIO"]:
            print "cdb:stderr>%s" % repr(sLine)[1:-1];
        if sChar == "":
          break;
        sLine = "";
      else:
        sLine += sChar;
    # Cdb stdout was closed: the process is terminating.
    assert oCrashInfo._bCdbTerminated or len(oCrashInfo._auProcessIds) == 0, \
        "Cdb terminated unexpectedly! Output:\r\n%s" % "\r\n".join(oCrashInfo.asCdbStdErrIO);
    oCrashInfo._bCdbRunning = False;
    return None;
    
  def _fasReadOutput(oCrashInfo):
    from cCrashInfo_fasReadOutput import cCrashInfo_fasReadOutput;
    return cCrashInfo_fasReadOutput(oCrashInfo);
  
  def _fasSendCommandAndReadOutput(oCrashInfo, sCommand):
    if dxCrashInfoConfig["bOutputIO"] or dxCrashInfoConfig["bOutputCommands"]:
      print "cdb<%s" % repr(sCommand)[1:-1];
    oCrashInfo._asCdbStdIO[-1] += sCommand;
    try:
      oCrashInfo._oCdbProcess.stdin.write("%s\r\n" % sCommand);
    except Exception, oException:
      assert oCrashInfo._bCdbTerminated or len(oCrashInfo._auProcessIds) == 0, \
          "Cdb terminated unexpectedly! Last output:\r\n%s" % "\r\n".join(oCrashInfo._asCdbStdIO[-20:]);
      oCrashInfo._bCdbRunning = False;
      return None;
    asOutput = oCrashInfo._fasReadOutput();
    # Detect obvious errors executing the command. (this will not catch everything, but does help development)
    assert asOutput is None or len(asOutput) != 1 or not re.match(r"^\s*\^ .*$", asOutput[0]), \
        "There was a problem executing the command %s: %s" % (repr(sCommand), repr(asOutput));
    return asOutput;
  
  def fiEvaluateExpression(oCrashInfo, sExpression):
    from cCrashInfo_fiEvaluateExpression import cCrashInfo_fiEvaluateExpression;
    return cCrashInfo_fiEvaluateExpression(oCrashInfo, sExpression);
  
  def fuEvaluateExpression(oCrashInfo, sExpression):
    from cCrashInfo_fuEvaluateExpression import cCrashInfo_fuEvaluateExpression;
    return cCrashInfo_fuEvaluateExpression(oCrashInfo, sExpression);
  
  def fHandleCreateExitProcess(oCrashInfo, sCreateExit, uProcessId):
    from cCrashInfo_fHandleCreateExitProcess import cCrashInfo_fHandleCreateExitProcess;
    return cCrashInfo_fHandleCreateExitProcess(oCrashInfo, sCreateExit, uProcessId);
  
  def fasGetModuleCdbNames(oCrashInfo, sModuleFileName):
    from cCrashInfo_fasGetModuleCdbNames import cCrashInfo_fasGetModuleCdbNames;
    return cCrashInfo_fasGetModuleCdbNames(oCrashInfo, sModuleFileName);