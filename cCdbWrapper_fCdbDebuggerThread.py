import re;
from cErrorReport import cErrorReport;
from dxBugIdConfig import dxBugIdConfig;
from NTSTATUS import *;

daxExceptionHandling = {
  "sxe": [ # break on first chance exceptions
    # To be able to track which processes are running at any given time while the application being debugged, cpr and
    # epr must be enabled. Additionally, if epr is disabled the debugger will silently exit when the application
    # terminates. To distinguish this from other unexpected terminations of the debugger, epr must also be enabled.
    "cpr", "ibp", "epr",
    "aph", # Application has stopped responding
    STATUS_ACCESS_VIOLATION,
    STATUS_ARRAY_BOUNDS_EXCEEDED,
    STATUS_BREAKPOINT,
    STATUS_DATATYPE_MISALIGNMENT,
    STATUS_FAIL_FAST_EXCEPTION,
    STATUS_GUARD_PAGE_VIOLATION,
    STATUS_ILLEGAL_INSTRUCTION,
    STATUS_IN_PAGE_ERROR,
    STATUS_PRIVILEGED_INSTRUCTION,
    STATUS_SINGLE_STEP,
    STATUS_STACK_BUFFER_OVERRUN,
    STATUS_WAKE_SYSTEM_DEBUGGER,
    STATUS_WX86_BREAKPOINT,
    STATUS_WX86_SINGLE_STEP,
  ],
  "sxd": [ # break on second chance exceptions
    CPP_EXCEPTION_CODE,
    STATUS_ASSERTION_FAILURE,
    STATUS_INTEGER_DIVIDE_BY_ZERO,
    STATUS_INTEGER_OVERFLOW, 
    STATUS_STACK_OVERFLOW,
    STATUS_INVALID_HANDLE,
  ],
  "sxi": [ # ignored
    "ld", "ud", # Load/unload module
  ],
};

# Create a list of commands to set up event handling. The default for any exception not explicitly mentioned is to be
# handled as a second chance exception.
asExceptionHandlingCommands = ["sxd *"];
# request second chance debugger break for certain exceptions that indicate the application has a bug.
for sCommand, axExceptions in daxExceptionHandling.items():
  for xException in axExceptions:
    if isinstance(xException, str):
      asExceptionHandlingCommands.append("%s %s" % (sCommand, xException));
    else:
      asExceptionHandlingCommands.append("%s 0x%08X" % (sCommand, xException));
sExceptionHandlingCommands = ";".join(asExceptionHandlingCommands);

def cCdbWrapper_fCdbDebuggerThread(oCdbWrapper):
  # Read the initial cdb output related to starting/attaching to the first process.
  asIntialCdbOutput = oCdbWrapper.fasReadOutput();
  if not oCdbWrapper.bCdbRunning: return;
  # Exception handlers need to be set up.
  oCdbWrapper.bExceptionHandlersHaveBeenSet = False;
  # Only fire _fApplicationRunningCallback if the application was started for the first time or resumed after it was
  # paused to analyze an exception. 
  bInitialApplicationRunningCallbackFired = False;
  bDebuggerNeedsToResumeAttachedProcesses = len(oCdbWrapper.auProcessIdsPendingAttach) > 0;
  bApplicationWasPausedToAnalyzeAnException = False;
  # An error report will be created when needed; it is returned at the end
  oErrorReport = None;
  while asIntialCdbOutput or len(oCdbWrapper.auProcessIdsPendingAttach) + len(oCdbWrapper.auProcessIds) > 0:
    if asIntialCdbOutput:
      # First parse the intial output
      asCdbOutput = asIntialCdbOutput;
      asIntialCdbOutput = None;
    else:
      # Then attach to a process, or start or resume the application
      if not bInitialApplicationRunningCallbackFired or bApplicationWasPausedToAnalyzeAnException:
        # Application was started or resumed after an exception
        oCdbWrapper.fApplicationRunningCallback and oCdbWrapper.fApplicationRunningCallback();
        bInitialApplicationRunningCallbackFired = True;
      asCdbOutput = oCdbWrapper.fasSendCommandAndReadOutput("g");
      if not oCdbWrapper.bCdbRunning: return;
    # If cdb is attaching to a process, make sure it worked.
    for sLine in asCdbOutput:
      oFailedAttachMatch = re.match(r"^Cannot debug pid \d+, Win32 error 0n\d+\s*$", sLine);
      assert not oFailedAttachMatch, "Failed to attach to process!\r\n%s" % "\r\n".join(asCdbOutput);
    # Find out what event caused the debugger break
    asLastEventOutput = oCdbWrapper.fasSendCommandAndReadOutput(".lastevent");
    if not oCdbWrapper.bCdbRunning: return;
    # Sample output:
    # |Last event: 3d8.1348: Create process 3:3d8                
    # |  debugger time: Tue Aug 25 00:06:07.311 2015 (UTC + 2:00)
    # - or -
    # |Last event: c74.10e8: Exit process 4:c74, code 0          
    # |  debugger time: Tue Aug 25 00:06:07.311 2015 (UTC + 2:00)
    bValidLastEventOutput = len(asLastEventOutput) == 2 and re.match(r"^\s*debugger time: .*$", asLastEventOutput[1]);
    oEventMatch = bValidLastEventOutput and re.match(
      "".join([
        r"^Last event: ([0-9a-f]+)\.[0-9a-f]+: ",
        r"(?:",
          r"(Create|Exit) process [0-9a-f]+\:([0-9a-f]+)(?:, code [0-9a-f]+)?",
        r"|",
          r"(.*?) \- code ([0-9a-f]+) \(!*\s*(?:first|second) chance\s*!*\)",
        r")\s*$",
      ]),
      asLastEventOutput[0],
      re.I
    );
    assert oEventMatch, "Invalid .lastevent output:\r\n%s" % "\r\n".join(asLastEventOutput);
    (
      sProcessIdHex,
        sCreateExitProcess, sCreateExitProcessIdHex,
        sExceptionDescription, sExceptionCode
    ) = oEventMatch.groups();
    uProcessId = long(sProcessIdHex, 16);
    uExceptionCode = sExceptionCode and int(sExceptionCode, 16);
    if uExceptionCode in (STATUS_BREAKPOINT, STATUS_WAKE_SYSTEM_DEBUGGER) and uProcessId not in oCdbWrapper.auProcessIds:
      # This is assumed to be the initial breakpoint after starting/attaching to the first process or after a new
      # process was created by the application. This assumption may not be correct, in which case the code needs to
      # be modifed to check the stack to determine if this really is the initial breakpoint. But that comes at a
      # performance cost, so until proven otherwise, the code is based on this assumption.
      sCreateExitProcess = "Create";
      sCreateExitProcessIdHex = sProcessIdHex;
    if sCreateExitProcess:
      # Make sure the created/exited process is the current process.
      assert sProcessIdHex == sCreateExitProcessIdHex, "%s vs %s" % (sProcessIdHex, sCreateExitProcessIdHex);
      oCdbWrapper.fHandleCreateExitProcess(sCreateExitProcess, uProcessId);
      # If there are more processes to attach to, do so:
      if len(oCdbWrapper.auProcessIdsPendingAttach) > 0:
        asAttachToProcess = oCdbWrapper.fasSendCommandAndReadOutput(".attach 0n%d" % oCdbWrapper.auProcessIdsPendingAttach[0]);
        if not oCdbWrapper.bCdbRunning: return;
      else:
        # Set up exception handling if this has not been done yet.
        if not oCdbWrapper.bExceptionHandlersHaveBeenSet:
          # Note to self: when rewriting the code, make sure not to set up exception handling before the debugger has
          # attached to all processes. But do so before resuming the threads. Otherwise one or more of the processes can
          # end up having only one thread that has a suspend count of 2 and no amount of resuming will cause the process
          # to run. The reason for this is unknown, but if things are done in the correct order, this problem is avoided.
          oCdbWrapper.bExceptionHandlersHaveBeenSet = True;
          oCdbWrapper.fasSendCommandAndReadOutput(sExceptionHandlingCommands);
          if not oCdbWrapper.bCdbRunning: return;
        # If the debugger attached to processes, mark that as done and resume threads in all processes.
        if bDebuggerNeedsToResumeAttachedProcesses:
          bDebuggerNeedsToResumeAttachedProcesses = False;
          for uProcessId in oCdbWrapper.auProcessIds:
            oCdbWrapper.fasSendCommandAndReadOutput("|~[0n%d]s;~*m" % uProcessId);
            if not oCdbWrapper.bCdbRunning: return;
      continue;
    # Report that the application is paused for analysis...
    oCdbWrapper.fExceptionDetectedCallback and oCdbWrapper.fExceptionDetectedCallback(uExceptionCode, sExceptionDescription);
    # And potentially report that the application is resumed later...
    bApplicationWasPausedToAnalyzeAnException = True;
    # Optionally perform enhanced symbol reload
    oCdbWrapper.fEnhancedSymbolReload();
    if not oCdbWrapper.bCdbRunning: return;
    # Create an error report, if the exception is fatal.
    oErrorReport = cErrorReport.foCreate(oCdbWrapper, uExceptionCode, sExceptionDescription);
    if not oCdbWrapper.bCdbRunning: return;
    if oErrorReport is not None:
      break;

  # Terminate cdb.
  oCdbWrapper.bCdbWasTerminatedOnPurpose = True;
  oCdbWrapper.fasSendCommandAndReadOutput("q");
  assert not oCdbWrapper.bCdbRunning, "Debugger did not terminate when requested";
  oCdbWrapper.oErrorReport = oErrorReport;

