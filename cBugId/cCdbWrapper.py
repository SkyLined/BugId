import itertools, re, subprocess, threading, time;
from cCdbWrapper_faoGetModulesForFileNameInCurrentProcess import cCdbWrapper_faoGetModulesForFileNameInCurrentProcess;
from cCdbWrapper_fasGetStack import cCdbWrapper_fasGetStack;
from cCdbWrapper_fasReadOutput import cCdbWrapper_fasReadOutput;
from cCdbWrapper_fasSendCommandAndReadOutput import cCdbWrapper_fasSendCommandAndReadOutput;
from cCdbWrapper_fCdbCleanupThread import cCdbWrapper_fCdbCleanupThread;
from cCdbWrapper_fCdbInterruptOnTimeoutThread import cCdbWrapper_fCdbInterruptOnTimeoutThread;
from cCdbWrapper_fCdbStdErrThread import cCdbWrapper_fCdbStdErrThread;
from cCdbWrapper_fCdbStdInOutThread import cCdbWrapper_fCdbStdInOutThread;
from cCdbWrapper_fdoGetModulesByCdbIdForCurrentProcess import cCdbWrapper_fdoGetModulesByCdbIdForCurrentProcess;
from cCdbWrapper_fHandleCreateExitProcess import cCdbWrapper_fHandleCreateExitProcess;
from cCdbWrapper_ftxGetProcessIdAndBinaryNameForCurrentProcess import cCdbWrapper_ftxGetProcessIdAndBinaryNameForCurrentProcess;
from cCdbWrapper_ftxSplitSymbolOrAddress import cCdbWrapper_ftxSplitSymbolOrAddress;
from cCdbWrapper_fsHTMLEncode import cCdbWrapper_fsHTMLEncode;
from cCdbWrapper_f_Timeout import cCdbWrapper_fxSetTimeout, cCdbWrapper_fClearTimeout;
from cCdbWrapper_f_Breakpoint import cCdbWrapper_fuAddBreakpoint, cCdbWrapper_fRemoveBreakpoint;
from cCdbWrapper_fsGetSymbolForAddress import cCdbWrapper_fsGetSymbolForAddress;
from cExcessiveCPUUsageDetector import cExcessiveCPUUsageDetector;
from dxBugIdConfig import dxBugIdConfig;
from sOSISA import sOSISA;
try:
  from Kill import fKillProcessesUntilTheyAreDead;
except:
  print "*" * 80;
  print "BugId depends on Kill, which you can download at https://github.com/SkyLined/Kill/";
  print "*" * 80;
  raise;

class cCdbWrapper(object):
  sCdbISA = sOSISA;
  def __init__(oCdbWrapper,
    asApplicationCommandLine = None,
    auApplicationProcessIds = None,
    asSymbolServerURLs = [],
    dsURLTemplate_by_srSourceFilePath = {},
    rImportantStdOutLines = None,
    rImportantStdErrLines = None,
    # bIgnoreFirstChanceBreakpoints = False, ### This setting has been moved to dxBugIdConfig.py
    # bEnableSourceCodeSupport = True, ### This setting has been moved to dxBugIdConfig.py
    bGetDetailsHTML = False,
    fApplicationRunningCallback = None,
    # fApplicationRunningCallback is called when the application starts and after exception analysis is finished for
    # continuable exceptions that are not considered a bug. In the later case, fExceptionDetectedCallback is called
    # when the application is paused to do the analysis and fApplicationRunningCallback is called when the analysis
    # is finished and the exception was not considered a bug to indicate the application has been resumed.
    fExceptionDetectedCallback = None,
    # fExceptionDetectedCallback is called when an exception is detected in the application that requires analysis.
    # This callback can be used to pause any timeouts you may have set for the application, as the application is
    # paused during analysis. You can resume these timeouts when fApplicationRunningCallback is called when the
    # analysis is finished.
    fApplicationExitCallback = None,
    # Called when (any of) the application's "main" process(es) terminates. This is the first process created when you
    # start an application using BugId, or any of the processes you asked BugId to attach to. This callback is not
    # called when any process spawned by these "main" processes during debugging is terminated. This callback can be
    # used to detect application termination, especially if you are debugging application that consist of multiple
    # processes, such as Microsoft Edge.
    fFinishedCallback = None,
    # Called when BugId has finished debugging the application and either detected a bug or all the application's
    # processes have terminated.
    fInternalExceptionCallback = None,
    # Called when there is a bug in BugId itself. Can be used to make sure BugId is working as expected. If you run
    # into a sitaution where this callback gets called, you can file a bug at https://github.com/SkyLined/BugId/issues
  ):
    oCdbWrapper.dsURLTemplate_by_srSourceFilePath = dsURLTemplate_by_srSourceFilePath;
    oCdbWrapper.rImportantStdOutLines = rImportantStdOutLines;
    oCdbWrapper.rImportantStdErrLines = rImportantStdErrLines;
    oCdbWrapper.bGetDetailsHTML = bGetDetailsHTML;
    oCdbWrapper.fApplicationRunningCallback = fApplicationRunningCallback;
    oCdbWrapper.fExceptionDetectedCallback = fExceptionDetectedCallback;
    oCdbWrapper.fApplicationExitCallback = fApplicationExitCallback;
    oCdbWrapper.fFinishedCallback = fFinishedCallback;
    oCdbWrapper.fInternalExceptionCallback = fInternalExceptionCallback;
    uSymbolOptions = sum([
      0x00000001, # SYMOPT_CASE_INSENSITIVE
      0x00000002, # SYMOPT_UNDNAME
      0x00000004 * (dxBugIdConfig["bDeferredSymbolLoads"] and 1 or 0), # SYMOPT_DEFERRED_LOAD
#     0x00000008, # SYMOPT_NO_CPP
      0x00000010 * (dxBugIdConfig["bEnableSourceCodeSupport"] and 1 or 0), # SYMOPT_LOAD_LINES
#     0x00000020, # SYMOPT_OMAP_FIND_NEAREST
#     0x00000040, # SYMOPT_LOAD_ANYTHING
#     0x00000080, # SYMOPT_IGNORE_CVREC
      0x00000100 * (not dxBugIdConfig["bDeferredSymbolLoads"] and 1 or 0), # SYMOPT_NO_UNQUALIFIED_LOADS
      0x00000200, # SYMOPT_FAIL_CRITICAL_ERRORS
#     0x00000400, # SYMOPT_EXACT_SYMBOLS
      0x00000800, # SYMOPT_ALLOW_ABSOLUTE_SYMBOLS
      0x00001000 * (not dxBugIdConfig["bUse_NT_SYMBOL_PATH"] and 1 or 0), # SYMOPT_IGNORE_NT_SYMPATH
      0x00002000, # SYMOPT_INCLUDE_32BIT_MODULES 
#     0x00004000, # SYMOPT_PUBLICS_ONLY
#     0x00008000, # SYMOPT_NO_PUBLICS
      0x00010000, # SYMOPT_AUTO_PUBLICS
      0x00020000, # SYMOPT_NO_IMAGE_SEARCH
#     0x00040000, # SYMOPT_SECURE
      0x00080000, # SYMOPT_NO_PROMPTS
#     0x80000000, # SYMOPT_DEBUG (don't set here: will be switched on and off later as needed)
    ]);
    # Get the cdb binary path
    sCdbBinaryPath = dxBugIdConfig["sCdbBinaryPath_%s" % oCdbWrapper.sCdbISA];
    assert sCdbBinaryPath, "No %s cdb binary path found" % oCdbWrapper.sCdbISA;
    # Get a list of symbol servers to use:
    sSymbolsPath = ";".join(
      ["cache*%s" % x for x in dxBugIdConfig["asSymbolCachePaths"]] +
      ["srv*%s" % x for x in asSymbolServerURLs]
    );
    # Get the command line (without starting/attaching to a process)
    asCommandLine = [sCdbBinaryPath, "-o", "-sflags", "0x%08X" % uSymbolOptions];
    if dxBugIdConfig["bEnableSourceCodeSupport"]:
      asCommandLine += ["-lines"];
    if sSymbolsPath:
      asCommandLine += ["-y", sSymbolsPath];
    oCdbWrapper.auProcessIds = [];
    oCdbWrapper.auProcessIdsPendingAttach = auApplicationProcessIds or [];
    # When provided, fApplicationExitCallback is called when any of the applications "main" processes exits.
    # If cdb is told to create a process, this first process is the main process. If cdb is attaching o processes, all
    # processes it is attaching to are the main processes. auMainProcessIds keeps track of their ids, so BugId can
    # detect when one of these exits.
    if fApplicationExitCallback:
      oCdbWrapper.auMainProcessIds = oCdbWrapper.auProcessIdsPendingAttach[:];
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
    if bGetDetailsHTML:
      oCdbWrapper.asCdbStdIOBlocksHTML = [""]; # Logs stdin/stdout/stderr for the cdb process, grouped by executed command.
    oCdbWrapper.oBugReport = None; # Set to a bug report if a bug was detected in the application
    oCdbWrapper.uLastProcessId = None; # Set to the id of the last process to be reported as terminated by cdb.
    oCdbWrapper.bCdbRunning = True; # Set to False after cdb terminated, used to terminate the debugger thread.
    oCdbWrapper.bCdbWasTerminatedOnPurpose = False; # Set to True when cdb is terminated on purpose, used to detect unexpected termination.
    if bGetDetailsHTML:
      oCdbWrapper.sImportantOutputHTML = ""; # Lines from stdout/stderr that are marked as potentially important to understanding the bug.
    # cdb variables are in short supply, so a mechanism must be used to allocate and release them.
    # See fuGetVariableId and fReleaseVariableId for implementation details.
    oCdbWrapper.uAvailableVariableIds = list(xrange(20)); # $t0-$t19. 
    # To make it easier to refer to cdb breakpoints by id, a mechanism must be used to allocate and release them
    # See fuGetBreakpointId and fReleaseBreakpointId for implementation details.
    oCdbWrapper.oBreakpointCounter = itertools.count(); # None have been used so far, so start at 0.
    # You can set a breakpoint that results in a bug being reported when it is hit.
    # See fuAddBugBreakpoint and fReleaseBreakpointId for implementation details.
    oCdbWrapper.duAddress_by_uBreakpointId = {};
    oCdbWrapper.duProcessId_by_uBreakpointId = {};
    oCdbWrapper.dfCallback_by_uBreakpointId = {};
    # You can tell BugId to check for excessive CPU usage among all the threads running in the application.
    # See fSetCheckForExcessiveCPUUsageTimeout and cExcessiveCPUUsageDetector.py for more information
    oCdbWrapper.oExcessiveCPUUsageDetector = cExcessiveCPUUsageDetector(oCdbWrapper);
    # Keep track of future timeouts and their callbacks
    oCdbWrapper.axTimeouts = [];
    oCdbWrapper.oTimeoutsLock = threading.Lock();
    # Set to true if cdb has been interrupted by the timeout thread but the stdio thread has not yet handled this. Used
    # to prevent the timeout thread from interrupting it multiple times if the stdio thread is slow.
    oCdbWrapper.bInterruptPending = False;
    # oCdbLock is used by oCdbStdInOutThread and oCdbInterruptOnTimeoutThread to allow the former to execute commands
    # (other than "g") without the later attempting to get cdb to suspend the application with a breakpoint, and vice
    # versa. It's acquired on behalf of the former, to prevent the later from interrupting before the application has
    # even started.
    oCdbWrapper.oCdbLock = threading.Lock();
    oCdbWrapper.oCdbLock.acquire();
    oCdbWrapper.bCdbStdInOutThreadRunning = True; # Will be set to false if the thread terminates for any reason.
    # Keep track of how long the application has been running, used for timeouts (see fxSetTimeout, fCdbStdInOutThread
    # and fCdbInterruptOnTimeoutThread for details. The debugger can tell is what time it thinks it is before we start
    # and resume the application as well as what time it thinks it was when an exception happened. The difference is
    # used to calculate how long the application has been running. We cannot simply use time.clock() before start/
    # resuming and at the time an event is handled as the debugger may take quite some time processing an event before
    # we can call time.clock(): this time would incorrectly be added to the time the application has spent running.
    # However, while the application is running, we cannot ask the debugger what time it thinks it is, so we have to 
    # rely on time.clock(). Hence, both values are tracked.
    oCdbWrapper.oApplicationTimeLock = threading.Lock();
    oCdbWrapper.nApplicationRunTime = 0; # Total time spent running before last interruption
    oCdbWrapper.nApplicationResumeDebuggerTime = None;  # debugger time at the moment the application was last resumed
    oCdbWrapper.nApplicationResumeTime = None;          # time.clock() at the moment the application was last resumed
    oCdbWrapper.oCdbProcess = subprocess.Popen(
      args = " ".join(asCommandLine),
      stdin = subprocess.PIPE,
      stdout = subprocess.PIPE,
      stderr = subprocess.PIPE,
      creationflags = subprocess.CREATE_NEW_PROCESS_GROUP,
    );
    
    # Create a thread that interacts with the debugger to debug the application
    oCdbWrapper.oCdbStdInOutThread = oCdbWrapper._fStartThread(cCdbWrapper_fCdbStdInOutThread);
    # Create a thread that reads stderr output and shows it in the console
    oCdbWrapper.oCdbStdErrThread = oCdbWrapper._fStartThread(cCdbWrapper_fCdbStdErrThread);
    # Create a thread that checks for a timeout to interrupt cdb when needed.
    oCdbWrapper.oCdbInterruptOnTimeoutThread = oCdbWrapper._fStartThread(cCdbWrapper_fCdbInterruptOnTimeoutThread);
    # Create a thread that waits for the debugger to terminate and cleans up after it.
    oCdbWrapper.oCdbCleanupThread = oCdbWrapper._fStartThread(cCdbWrapper_fCdbCleanupThread);
  
  def _fStartThread(oCdbWrapper, fActivity):
    oThread = threading.Thread(target = oCdbWrapper._fThreadWrapper, args = (fActivity,));
    oThread.start();
    return oThread;
  
  def _fThreadWrapper(oCdbWrapper, fActivity):
    try:
      fActivity(oCdbWrapper);
    except Exception, oException:
      # Start another thread to clean up after the exception was handled.
      oThread = threading.Thread(target = oCdbWrapper._fThreadExceptionHandler, args = (oException, threading.currentThread()));
      oThread.start();
      if oCdbWrapper.fInternalExceptionCallback:
        oCdbWrapper.fInternalExceptionCallback(oException);
      else:
        raise;
  
  def _fThreadExceptionHandler(oCdbWrapper, oException, oExceptionThread):
    # Wait for the exception thread to terminate and then clean up.
    oExceptionThread.join();
    oCdbProcess = getattr(oCdbWrapper, "oCdbProcess", None);
    if not oCdbProcess:
      oCdbWrapper.bCdbRunning = False;
      return;
    if oCdbProcess.poll() is not None:
      oCdbWrapper.bCdbRunning = False;
      return;
    oCdbWrapper.bCdbWasTerminatedOnPurpose = True;
    # cdb is still running: try to terminate cdb the normal way.
    try:
      oCdbProcess.terminate();
    except:
      pass;
    else:
      oCdbWrapper.bCdbRunning = False;
      return;
    if oCdbProcess.poll() is not None:
      oCdbWrapper.bCdbRunning = False;
      return;
    # cdb is still running: try to terminate cdb the hard way.
    oKillException = None;
    try:
      fKillProcessesUntilTheyAreDead([oCdbProcess.pid]);
    except Exception, oException:
      oKillException = oException;
    else:
      oCdbWrapper.bCdbRunning = False;
    # if cdb is *still* running, report and raise an internal exception.
    if oCdbProcess.poll() is None:
      oKillException = oKillException or AssertionError("cdb did not die after killing it repeatedly")
      if oCdbWrapper.fInternalExceptionCallback:
        oCdbWrapper.fInternalExceptionCallback(oKillException);
      raise oKillException;
    # cdb finally died.
    oCdbWrapper.bCdbRunning = False;
    return;
  
  def fStop(oCdbWrapper):
    oCdbWrapper.bCdbWasTerminatedOnPurpose = True;
    oCdbProcess = getattr(oCdbWrapper, "oCdbProcess", None);
    if oCdbProcess:
      oCdbProcess.terminate();
    # The below three threads may have called an event callback, which issued this fStop call. Therefore, we cannot
    # wait for them to terminate, as this could mean "waiting until we stop waiting", which takes forever. Since Python
    # won't allow you to wait for yourself, this could thow a RuntimeError exception: "cannot join current thread".
    # oCdbWrapper.oCdbStdInOutThread.join();
    # oCdbWrapper.oCdbStdErrThread.join();
    # oCdbWrapper.oCdbCleanupThread.join();
    # However, this should not be a problem. The first two thread stop running as soon as they notice cdb has
    # terminated. This functions waits for that as well, so the threads should stop at the same time or soon after this
    # function returns. This is assuming they have not called a callback that does not return: that is a bug, but not
    # in BugIg, but in that callback function. The third thread waits for the first two, does some cleanup and then
    # stops running as well. In other words, termination is guaranteed assuming any active callbacks do not block.
    if oCdbProcess:
      oCdbProcess.wait();
    oCdbWrapper.bCdbRunning = False;
  
  def __del__(oCdbWrapper):
    # Check to make sure the debugger process is not running
    oCdbProcess = getattr(oCdbWrapper, "oCdbProcess", None);
    if oCdbProcess and oCdbProcess.poll() is None:
      print "*** INTERNAL ERROR: cCdbWrapper did not terminate, the cdb process is still running.";
      oCdbProcess.terminate();
  
  def fuGetVariableId(oCdbWrapper):
    return oCdbWrapper.uAvailableVariableIds.pop();
  def fReleaseVariableId(oCdbWrapper, uVariableId):
    oCdbWrapper.uAvailableVariableIds.append(uVariableId);
  
  # Select process/thread
  def fSelectProcess(oCdbWrapper, uProcessId):
    return oCdbWrapper.fSelectProcessAndThread(uProcessId = uProcessId);
  def fSelectThread(oCdbWrapper, uThreadId):
    return oCdbWrapper.fSelectProcessAndThread(uThreadId = uThreadId);
  def fSelectProcessAndThread(oCdbWrapper, uProcessId = None, uThreadId = None):
    # Both arguments are optional
    sSelectCommand = "";
    asSelected = [];
    if uProcessId is not None:
      sSelectCommand += "|~[0x%X]s;" % uProcessId;
      asSelected.append("process");
    if uThreadId is not None:
      sSelectCommand += "~~[0x%X]s;" % uThreadId;
      asSelected.append("thread");
    if sSelectCommand:
      sSelectCommand += " $$ Select %s" % " and ".join(asSelected);
      asSelectOutput = oCdbWrapper.fasSendCommandAndReadOutput(sSelectCommand);
      if not oCdbWrapper.bCdbRunning: return;
      srIgnoredErrors = r"^\*\*\* (%s) .*$" % "|".join([
        r"WARNING: Unable to verify checksum for",
        r"ERROR: Module load completed but symbols could not be loaded for",
      ]);
      for sLine in asSelectOutput:
        assert re.match(srIgnoredErrors, sLine), \
            "Unexpected select process/thread output:\r\n%s" % "\r\n".join(asSelectOutput);
  # Excessive CPU usage
  def fSetCheckForExcessiveCPUUsageTimeout(oCdbWrapper, nTimeout):
    oCdbWrapper.oExcessiveCPUUsageDetector.fStartTimeout(nTimeout);
  
  def fnApplicationRunTime(oCdbWrapper):
    oCdbWrapper.oApplicationTimeLock.acquire();
    try:
      if oCdbWrapper.nApplicationResumeTime is None:
        return oCdbWrapper.nApplicationRunTime;
      return oCdbWrapper.nApplicationRunTime + time.clock() - oCdbWrapper.nApplicationResumeTime;
    finally:
      oCdbWrapper.oApplicationTimeLock.release();
  
  def fuGetValue(oCdbWrapper, sValue):
    asValueResult = oCdbWrapper.fasSendCommandAndReadOutput('.printf "%%p\\n", %s; $$ Get value' % sValue);
    if not oCdbWrapper.bCdbRunning: return;
    assert len(asValueResult) == 1, \
        "Unexpected value result:\r\n%s" % "\r\n".join(asValueResult);
    return long(asValueResult[0], 16);
  
  # Breakpoints
  def fuAddBreakpoint(oCdbWrapper, *axArguments, **dxArguments):
    return cCdbWrapper_fuAddBreakpoint(oCdbWrapper, *axArguments, **dxArguments);
  def fRemoveBreakpoint(oCdbWrapper, *axArguments, **dxArguments):
    return cCdbWrapper_fRemoveBreakpoint(oCdbWrapper, *axArguments, **dxArguments);
  # Timeouts
  def fxSetTimeout(oCdbWrapper, *axArguments, **dxArguments):
    return cCdbWrapper_fxSetTimeout(oCdbWrapper, *axArguments, **dxArguments);
  def fClearTimeout(oCdbWrapper, *axArguments, **dxArguments):
    return cCdbWrapper_fClearTimeout(oCdbWrapper, *axArguments, **dxArguments);
  # cdb I/O
  def fasReadOutput(oCdbWrapper, *axArguments, **dxArguments):
    return cCdbWrapper_fasReadOutput(oCdbWrapper, *axArguments, **dxArguments);
  def fasSendCommandAndReadOutput(oCdbWrapper, *axArguments, **dxArguments):
    return cCdbWrapper_fasSendCommandAndReadOutput(oCdbWrapper, *axArguments, **dxArguments);
  
  def fHandleCreateExitProcess(oCdbWrapper, *axArguments, **dxArguments):
    return cCdbWrapper_fHandleCreateExitProcess(oCdbWrapper, *axArguments, **dxArguments);
  
  def ftxGetProcessIdAndBinaryNameForCurrentProcess(oCdbWrapper, *axArguments, **dxArguments):
    return cCdbWrapper_ftxGetProcessIdAndBinaryNameForCurrentProcess(oCdbWrapper, *axArguments, **dxArguments);
  
  def faoGetModulesForFileNameInCurrentProcess(oCdbWrapper, *axArguments, **dxArguments):
    return cCdbWrapper_faoGetModulesForFileNameInCurrentProcess(oCdbWrapper, *axArguments, **dxArguments);
  
  def fdoGetModulesByCdbIdForCurrentProcess(oCdbWrapper, *axArguments, **dxArguments):
    return cCdbWrapper_fdoGetModulesByCdbIdForCurrentProcess(oCdbWrapper, *axArguments, **dxArguments);
  
  def fasGetStack(oCdbWrapper, *axArguments, **dxArguments):
    return cCdbWrapper_fasGetStack(oCdbWrapper, *axArguments, **dxArguments);
  
  def ftxSplitSymbolOrAddress(oCdbWrapper, *axArguments, **dxArguments):
    return cCdbWrapper_ftxSplitSymbolOrAddress(oCdbWrapper, *axArguments, **dxArguments);
  
  def fsHTMLEncode(oCdbWrapper, *axArguments, **dxArguments):
    return cCdbWrapper_fsHTMLEncode(oCdbWrapper, *axArguments, **dxArguments);
  
  def fsGetSymbolForAddress(oCdbWrapper, *axArguments, **dxArguments):
    return cCdbWrapper_fsGetSymbolForAddress(oCdbWrapper, *axArguments, **dxArguments);
