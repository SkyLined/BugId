import os, re, subprocess, threading, time;

from cCrashInfo_foCdbRunApplicationAndGetErrorReport import cCrashInfo_foCdbRunApplicationAndGetErrorReport;
from dxCrashInfoConfig import dxCrashInfoConfig;

sOSISA = os.getenv("PROCESSOR_ARCHITEW6432") or os.getenv("PROCESSOR_ARCHITECTURE"); # "x86" or "AMD64"
sMicrosoftSymbolServerURL = "http://msdl.microsoft.com/download/symbols";

class cCrashInfo(object):
  def __init__(oSelf, asApplicationCommandLine, auApplicationProcessIds, asSymbolServerURLs, \
      fApplicationRunningCallback, fExceptionDetectedCallback, fFinishedCallback, fInternalExceptionCallback):
    oSelf._fApplicationRunningCallback = fApplicationRunningCallback;
    oSelf._fExceptionDetectedCallback = fExceptionDetectedCallback;
    oSelf._fFinishedCallback = fFinishedCallback;
    oSelf._fInternalExceptionCallback = fInternalExceptionCallback;
    oSelf.dafEventCallbacks_by_sEventName = {
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
#      0x80000000, # SYMOPT_DEBUG
    ]);
    # For historic reasons, the ISA of the OS is used to determine which ISA version of cdb to use. It is not known if
    # this was originally done to avoid problems with x86 cdb debugging x86 applications of AMD64 windows, or if it
    # doesn't really matter which cdb ISA version is used in this case.
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
    oSelf._auProcessIds = [];
    oSelf._auProcessIdsPendingAttach = [];
    oSelf._auApplicationProcessIds = auApplicationProcessIds; # TODO: remove once bug has been fixed.
    if auApplicationProcessIds is not None and len(auApplicationProcessIds) > 0:
      asCommandLine += ["-p", str(auApplicationProcessIds[0])];
      oSelf._auProcessIdsPendingAttach = auApplicationProcessIds;
    
    asCommandLine = [
      (sArg.find(" ") == -1 or sArg[0] == '"')        and sArg               or '"%s"' % sArg.replace('"', '\\"')
      for sArg in asCommandLine
    ];
    if dxCrashInfoConfig["bOutputCommandLine"]:
      print "* Starting %s" % " ".join(asCommandLine);
    oSelf.asCdbIO = [];
    oSelf._asCdbStdErrIO = [];
    oSelf._oErrorReport = None;
    oSelf._uLastProcessId = None;
    oSelf._oCdbProcess = subprocess.Popen(args = " ".join(asCommandLine), stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE);
    oSelf._bCdbRunning = True;
    oSelf._bCdbTerminated = False;
    # Create a thread that interacts with the debugger to debug the application
    oSelf._oCdbDebuggerThread = threading.Thread(target = oSelf._fCdbDebuggerThread);
    oSelf._oCdbDebuggerThread.start();
    # Create a thread that reads stderr output and shows it in the console
    oSelf._oCdbStdErrThread = threading.Thread(target = oSelf._fCdbStdErrThread);
    oSelf._oCdbStdErrThread.start();
    # Create a thread that waits for the debugger to terminate and cleans up after it.
    oSelf._oCdbCleanupThread = threading.Thread(target = oSelf._fCdbCleanupThread);
    oSelf._oCdbCleanupThread.start();
    # NB. The above two are separated to make handling exceptions in the code run in the first thread possible without
    # the code running in the second thread interfering. If both were in the same thread, the cleanup code would have
    # to intercept exceptions from the debug code to make sure the cleanup code is always run. It would need to do the
    # cleanup before throwing the original exception again to make sure the exception is visible to the user. This is
    # complex and any exception thrown in the cleanup code would prevent the original exception from the debug code
    # from getting thrown, potentially hiding the root cause of all these exceptions. This has happened before, hence
    # the two threads solution.
  
  def __del__(oSelf):
    # Check to make sure the debugger process is not running
    oProcess = oSelf._oCdbProcess;
    if oProcess is not None and oProcess.poll() == None:
        print "*** INTERNAL ERROR: CrashInfo was not stopped, the cdb process is still running.";
  
  def fStop(oSelf):
    oSelf._bCdbTerminated = True;
    oSelf._oCdbProcess.terminate();
    oSelf._oCdbDebuggerThread.join();
    oSelf._oCdbCleanupThread.join();
  
  def fAddEventCallback(oSelf, sEventName, fEventCallback):
    oSelf.dafEventCallbacks_by_sEventName[sEventName].add(fEventCallback);
  
  def fFireEvent(oSelf, sEventName, *axEventInforamtion):
    for fEventCallback in oSelf.dafEventCallbacks_by_sEventName[sEventName]:
      fEventCallback(oSelf, *axEventInforamtion);
  
  def _fCdbDebuggerThread(oSelf):
    try:
      # Read the initial cdb output related to starting/attaching to the first process.
      asIntialOutput = oSelf._fasReadOutput();
      if not oSelf._bCdbRunning: return;
      oSelf._oErrorReport = cCrashInfo_foCdbRunApplicationAndGetErrorReport(oSelf, asIntialOutput);
    except Exception, oException:
      oSelf._fInternalExceptionCallback(oException);
      oSelf._bCdbTerminated = True;
      oSelf._oCdbProcess.terminate();
      raise;
  
  def _fCdbCleanupThread(oSelf):
    try:
      # wait for debugger thread to terminate.
      oSelf._oCdbDebuggerThread.join();
      # wait for stderr thread to terminate.
      oSelf._oCdbStdErrThread.join();
      # wait for debugger to terminate.
      oSelf._oCdbProcess.wait();
      # wait for any processes that were being debugged to terminate
      sTasklistBinaryPath = os.path.join(os.getenv("WinDir"), "System32", "tasklist.exe");
      oSelf.asTest = [];
      # The last process that terminated was open when cdb reported it and may not have been closed by the OS yet.
      # It needs to be added to the list of processes that need to terminate before debugging is truely finished.
      if oSelf._uLastProcessId is not None:
        oSelf._auProcessIds.append(oSelf._uLastProcessId);
      while oSelf._auProcessIds:
        uProcessId = oSelf._auProcessIds.pop();
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
      oSelf._fFinishedCallback(oSelf._oErrorReport);
    except Exception, oException:
      oSelf._fInternalExceptionCallback(oException);
      raise;
  
  def _fCdbStdErrThread(oSelf):
    sLine = "";
    while 1:
      sChar = oSelf._oCdbProcess.stderr.read(1);
      if sChar == "\r":
        pass; # ignored.
      elif sChar in ("\n", ""):
        if sChar == "\n" or sLine:
          oSelf._asCdbStdErrIO.append(sLine);
          if dxCrashInfoConfig["bOutputErrIO"]:
            print "cdb:stderr>%s" % repr(sLine)[1:-1];
        if sChar == "":
          break;
        sLine = "";
      else:
        sLine += sChar;
    # Cdb stdout was closed: the process is terminating.
    assert oSelf._bCdbTerminated or len(oSelf._auProcessIds) == 0, \
        "Cdb terminated unexpectedly! Output:\r\n%s" % "\r\n".join(oSelf.asCdbStdErrIO);
    oSelf._bCdbRunning = False;
    return None;
    
  def _fasReadOutput(oSelf):
    from cCrashInfo_fasReadOutput import cCrashInfo_fasReadOutput;
    return cCrashInfo_fasReadOutput(oSelf);
  
  def _fasSendCommandAndReadOutput(oSelf, sCommand):
    if dxCrashInfoConfig["bOutputIO"] or dxCrashInfoConfig["bOutputCommands"]:
      print "cdb<%s" % repr(sCommand)[1:-1];
    oSelf.asCdbIO[-1] += sCommand;
    try:
      oSelf._oCdbProcess.stdin.write("%s\r\n" % sCommand);
    except Exception, oException:
      assert oSelf._bCdbTerminated or len(oSelf._auProcessIds) == 0, \
          "Cdb terminated unexpectedly! Last output:\r\n%s" % "\r\n".join(oSelf.asCdbIO[-20:]);
      oSelf._bCdbRunning = False;
      return None;
    asOutput = oSelf._fasReadOutput();
    # Detect obvious errors executing the command. (this will not catch everything, but does help development)
    assert asOutput is None or len(asOutput) != 1 or not re.match(r"^\s*\^ .*$", asOutput[0]), \
        "There was a problem executing the command %s: %s" % (repr(sCommand), repr(asOutput));
    return asOutput;
  
  def fiEvaluateExpression(oSelf, sExpression):
    from cCrashInfo_fiEvaluateExpression import cCrashInfo_fiEvaluateExpression;
    return cCrashInfo_fiEvaluateExpression(oSelf, sExpression);
  
  def fuEvaluateExpression(oSelf, sExpression):
    from cCrashInfo_fuEvaluateExpression import cCrashInfo_fuEvaluateExpression;
    return cCrashInfo_fuEvaluateExpression(oSelf, sExpression);
  
#  def fsGetModuleISA(oSelf, sCdbModuleId):
#    from cCrashInfo_fsGetModuleISA import cCrashInfo_fsGetModuleISA;
#    return cCrashInfo_fsGetModuleISA(oSelf, sCdbModuleId);
  
  def fsGetCurrentProcessISA(oSelf):
    from cCrashInfo_fsGetCurrentProcessISA import cCrashInfo_fsGetCurrentProcessISA;
    return cCrashInfo_fsGetCurrentProcessISA(oSelf);
  
  def fPatchVerifierBugInCurrentProcess(oSelf):
    from cCrashInfo_fPatchVerifierBugInCurrentProcess import cCrashInfo_fPatchVerifierBugInCurrentProcess;
    return cCrashInfo_fPatchVerifierBugInCurrentProcess(oSelf);
  
  def fHandleCreateExitProcess(oSelf, sCreateExit, uProcessId):
    from cCrashInfo_fHandleCreateExitProcess import cCrashInfo_fHandleCreateExitProcess;
    return cCrashInfo_fHandleCreateExitProcess(oSelf, sCreateExit, uProcessId);
  
  def fasGetModuleCdbNames(oSelf, sModuleFileName):
    from cCrashInfo_fasGetModuleCdbNames import cCrashInfo_fasGetModuleCdbNames;
    return cCrashInfo_fasGetModuleCdbNames(oSelf, sModuleFileName);