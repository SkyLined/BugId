import os, subprocess, threading;
from dxBugIdConfig import dxBugIdConfig;

sOSISA = os.getenv("PROCESSOR_ARCHITEW6432") or os.getenv("PROCESSOR_ARCHITECTURE"); # "x86" or "AMD64"
sMicrosoftSymbolServerURL = "http://msdl.microsoft.com/download/symbols";

class cCdbWrapper(object):
  sCdbISA = sOSISA;
  def __init__(oCdbWrapper,
    asApplicationCommandLine = None,
    auApplicationProcessIds = None,
    asSymbolServerURLs = [],
    fApplicationRunningCallback = None,
    fExceptionDetectedCallback = None,
    fFinishedCallback = None,
    fInternalExceptionCallback = None,
  ):
    oCdbWrapper.fApplicationRunningCallback = fApplicationRunningCallback;
    oCdbWrapper.fExceptionDetectedCallback = fExceptionDetectedCallback;
    oCdbWrapper.fFinishedCallback = fFinishedCallback;
    oCdbWrapper.fInternalExceptionCallback = fInternalExceptionCallback;
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
      dxBugIdConfig["bEnhancedSymbolLoading"] and 0x80000000 or 0, # SYMOPT_DEBUG
    ]);
    # Get the cdb binary path
    sCdbBinaryPath = dxBugIdConfig["sCdbBinaryPath_%s" % oCdbWrapper.sCdbISA];
    assert sCdbBinaryPath, "No %s cdb binary path found" % oCdbWrapper.sCdbISA;
    # Get a list of symbol servers to use:
    sSymbolsPath = ";".join(
      ["cache*%s" % x for x in dxBugIdConfig["asSymbolCachePaths"]] +
      ["srv*%s" % x for x in set(asSymbolServerURLs + [sMicrosoftSymbolServerURL])]
    );
    # Get the command line (without starting/attaching to a process)
    asCommandLine = [sCdbBinaryPath, "-o", "-sflags", "0x%08X" % uSymbolOptions, "-y", sSymbolsPath];
    oCdbWrapper.auProcessIds = [];
    oCdbWrapper.auProcessIdsPendingAttach = auApplicationProcessIds or [];
    if asApplicationCommandLine is not None:
      # If a process must be started, add it to the command line.
      assert not auApplicationProcessIds, "Cannot start a process and attach to processes at the same time";
      asCommandLine += asApplicationCommandLine;
    else:
      assert auApplicationProcessIds, "Must start a process or attach to one";
      # If any processes must be attached to, add the first to the coommand line.
      asCommandLine += ["-p", str(auApplicationProcessIds[0])];
    # Quote any non-quoted argument that contain spaces:
    asCommandLine = [
      (x[0] == '"' or x.find(" ") == -1) and x or '"%s"' % x.replace('"', '\\"')
      for x in asCommandLine
    ];
    # Show the command line if requested.
    if dxBugIdConfig["bOutputCommandLine"]:
      print "* Starting %s" % " ".join(asCommandLine);
    # Initialize some variables
    oCdbWrapper.sCurrentISA = None; # During exception handling, this is set to the ISA for the code that caused it.
    oCdbWrapper.asCdbStdIO = []; # Logs all stdin/stdout communication with cdb.
    oCdbWrapper.asCdbStdErr = []; # Logs all stderr output from cdb.
    oCdbWrapper.oErrorReport = None; # Set to an error report if a bug was detected in the application
    oCdbWrapper.uLastProcessId = None; # Set to the id of the last process to be reported as terminated by cdb.
    oCdbWrapper.bCdbRunning = True; # Set to False after cdb terminated, used to terminate the debugger thread.
    oCdbWrapper.bCdbTerminated = False; # Set to True before terminating cdb, used to detect unexpected termination.
    oCdbWrapper.oCdbProcess = subprocess.Popen(args = " ".join(asCommandLine),
        stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE);
    # Create a thread that interacts with the debugger to debug the application
    from cCdbWrapper_fCdbDebuggerThread import cCdbWrapper_fCdbDebuggerThread;
    oCdbWrapper.oCdbDebuggerThread = oCdbWrapper._fStartThread(cCdbWrapper_fCdbDebuggerThread);
    # Create a thread that reads stderr output and shows it in the console
    from cCdbWrapper_fCdbStdErrThread import cCdbWrapper_fCdbStdErrThread;
    oCdbWrapper.oCdbStdErrThread = oCdbWrapper._fStartThread(cCdbWrapper_fCdbStdErrThread);
    # Create a thread that waits for the debugger to terminate and cleans up after it.
    from cCdbWrapper_fCdbCleanupThread import cCdbWrapper_fCdbCleanupThread;
    oCdbWrapper.oCdbCleanupThread = oCdbWrapper._fStartThread(cCdbWrapper_fCdbCleanupThread);
  
  def _fStartThread(oCdbWrapper, fActivity):
    oThread = threading.Thread(target = oCdbWrapper._fThreadWrapper, args = (fActivity,));
    oThread.start();
    return oThread;
  
  def _fThreadWrapper(oCdbWrapper, fActivity):
    try:
      fActivity(oCdbWrapper);
    except Exception, oException:
      oCdbWrapper.fInternalExceptionCallback and oCdbWrapper.fInternalExceptionCallback(oException);
      if oCdbWrapper.bCdbRunning:
        oCdbWrapper.bCdbTerminated = True;
        oCdbWrapper.oCdbProcess.terminate();
      raise;
  
  def __del__(oCdbWrapper):
    # Check to make sure the debugger process is not running
    oProcess = getattr(oCdbWrapper, "oCdbProcess");
    if oProcess is not None and oProcess.poll() == None:
        print "*** INTERNAL ERROR: cCdbWrapper did not terminate, the cdb process is still running.";
        oProcess.terminate();
  
  def fStop(oCdbWrapper):
    oCdbWrapper.bCdbTerminated = True;
    oCdbWrapper.oCdbProcess.terminate();
    oCdbWrapper.oCdbDebuggerThread.join();
    oCdbWrapper.oCdbStdErrThread.join();
    oCdbWrapper.oCdbCleanupThread.join();
  
  def fasReadOutput(oCdbWrapper):
    from cCdbWrapper_fasReadOutput import cCdbWrapper_fasReadOutput;
    return cCdbWrapper_fasReadOutput(oCdbWrapper);
  
  def fasSendCommandAndReadOutput(oCdbWrapper, sCommand):
    from cCdbWrapper_fasSendCommandAndReadOutput import cCdbWrapper_fasSendCommandAndReadOutput;
    return cCdbWrapper_fasSendCommandAndReadOutput(oCdbWrapper, sCommand);
  
  def fHandleCreateExitProcess(oCdbWrapper, sCreateExit, uProcessId):
    from cCdbWrapper_fHandleCreateExitProcess import cCdbWrapper_fHandleCreateExitProcess;
    return cCdbWrapper_fHandleCreateExitProcess(oCdbWrapper, sCreateExit, uProcessId);
  
  def fiEvaluateExpression(oCdbWrapper, sExpression):
    from cCdbWrapper_fiEvaluateExpression import cCdbWrapper_fiEvaluateExpression;
    return cCdbWrapper_fiEvaluateExpression(oCdbWrapper, sExpression);
  
  def fuEvaluateExpression(oCdbWrapper, sExpression):
    from cCdbWrapper_fuEvaluateExpression import cCdbWrapper_fuEvaluateExpression;
    return cCdbWrapper_fuEvaluateExpression(oCdbWrapper, sExpression);
  
  def ftxGetProcessIdAndBinaryNameForCurrentProcess(oCdbWrapper):
    from cCdbWrapper_ftxGetProcessIdAndBinaryNameForCurrentProcess import cCdbWrapper_ftxGetProcessIdAndBinaryNameForCurrentProcess;
    return cCdbWrapper_ftxGetProcessIdAndBinaryNameForCurrentProcess(oCdbWrapper);
  
  def fasGetCdbIdsForModuleFileNameInCurrentProcess(oCdbWrapper, sModuleFileName):
    from cCdbWrapper_fasGetCdbIdsForModuleFileNameInCurrentProcess import cCdbWrapper_fasGetCdbIdsForModuleFileNameInCurrentProcess;
    return cCdbWrapper_fasGetCdbIdsForModuleFileNameInCurrentProcess(oCdbWrapper, sModuleFileName);
  
  def fdoGetModulesByCdbIdForCurrentProcess(oCdbWrapper):
    from cCdbWrapper_fdoGetModulesByCdbIdForCurrentProcess import cCdbWrapper_fdoGetModulesByCdbIdForCurrentProcess;
    return cCdbWrapper_fdoGetModulesByCdbIdForCurrentProcess(oCdbWrapper);
  
  def fEnhancedSymbolReload(oCdbWrapper):
    from cCdbWrapper_fEnhancedSymbolReload import cCdbWrapper_fEnhancedSymbolReload;
    return cCdbWrapper_fEnhancedSymbolReload(oCdbWrapper);
