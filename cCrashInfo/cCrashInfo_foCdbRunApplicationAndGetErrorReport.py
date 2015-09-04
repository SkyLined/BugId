import re;
from cErrorReport import cErrorReport;
from cException import cException;
from cProcess import cProcess;
from dxCrashInfoConfig import dxCrashInfoConfig;
from NTSTATUS import *;

daxExceptionHandling = {
  "sxe": [ # break on first chance exceptions
    # To be able to track which processes are running at any given time while the application being debugged, cpr and
    # epr must be enabled. Additionally, if epr is disabled the debugger will silently exit when the application
    # terminates. To distinguish this from other unexpected terminations of the debugger, epr must also be enabled.
    "cpr", "ibp", "epr",
    "wkd", # Wake debugger
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

def fDetectFailedAttach(asLines):
  # Attaching to a process may fail, this code detects that failure and throws an assertion failure.
  for sLine in asLines:
    oFailedAttachMatch = re.match(r"^Cannot debug pid (\d+),\s*(.*?)\s*$", sLine);
    assert not oFailedAttachMatch, "\r\n".join(
        ["Failed to attach to process %s: %s" % oFailedAttachMatch.groups()] + 
        asLines
    );

def cCrashInfo_foCdbRunApplicationAndGetErrorReport(oCrashInfo, asIntialOutput):
  # cdb can either start an application, or attach to paused processes; which is it?
  bCdbStartedAnApplication = len(oCrashInfo._auProcessIdsPendingAttach) == 0;
  bDebuggerIsAttachingToProcesses = not bCdbStartedAnApplication;
  # If cdb was asked to attach to a process, make sure it worked.
  if bDebuggerIsAttachingToProcesses:
    fDetectFailedAttach(asIntialOutput);
  # If the debugger started a process, we should set up exception handling now. Otherwise wait until the debugger has
  # attached to all the processes.
  bExceptionHandlersHaveBeenSet = False;
  # While no error has been reported:
  oErrorReport = None;
  while oErrorReport is None:
    # Find out what event caused the debugger break
    asLastEventOutput = oCrashInfo._fasSendCommandAndReadOutput(".lastevent");
    if not oCrashInfo._bCdbRunning: return None;
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
    if sCreateExitProcess:
      # Make sure the created/exited process is the current process.
      assert sProcessIdHex == sCreateExitProcessIdHex, "%s vs %s" % (sProcessIdHex, sCreateExitProcessIdHex);
      oCrashInfo.fHandleCreateExitProcess(sCreateExitProcess, uProcessId);
      if len(oCrashInfo._auProcessIds) == 0:
        break; # The last process was terminated.
    else:
      uExceptionCode = int(sExceptionCode, 16);
      if uExceptionCode == STATUS_BREAKPOINT and uProcessId not in oCrashInfo._auProcessIds:
        # This is assumed to be the initial breakpoint after starting/attaching to the first process or after a new
        # process was created by the application. This assumption may not be correct, in which case the code needs to
        # be modifed to check the stack to determine if this really is the initial breakpoint. But that comes at a
        # performance cost, so until proven otherwise, the code is based on this assumption.
        oCrashInfo.fHandleCreateExitProcess("Create", uProcessId);
      else:
        # Report that analysis is starting...
        oCrashInfo._fExceptionDetectedCallback(uExceptionCode, sExceptionDescription);
        # Turn off noizy symbol loading; it can mess up the output of commands, making it unparsable.
        asOutput = oCrashInfo._fasSendCommandAndReadOutput("!sym quiet");
        if not oCrashInfo._bCdbRunning: return None;
        # Gather relevant information...
        oProcess = cProcess.foCreate(oCrashInfo);
        oException = cException.foCreate(oCrashInfo, oProcess, uExceptionCode, sExceptionDescription);
        if not oCrashInfo._bCdbRunning: return None;
        # Save the exception report for returning when we're finished.
        oErrorReport = cErrorReport.foCreateFromException(oCrashInfo, oException);
        if not oCrashInfo._bCdbRunning: return None;
        # Stop the debugger if there was a fatal error that needs to be reported.
        if oErrorReport is not None:
          break;
        # Turn noizy symbol loading back on if it was enabled.
        if dxCrashInfoConfig["bDebugSymbolLoading"]:
          asOutput = oCrashInfo._fasSendCommandAndReadOutput("!sym noizy");
          if not oCrashInfo._bCdbRunning: return None;
    # If there are more processes to attach to, do so:
    if len(oCrashInfo._auProcessIdsPendingAttach) > 0:
      asAttachToProcess = oCrashInfo._fasSendCommandAndReadOutput(".attach 0n%d" % oCrashInfo._auProcessIdsPendingAttach[0]);
      if not oCrashInfo._bCdbRunning: return;
    else:
      # The debugger has started the process or attached to all processes.
      # Set up exception handling if this has not beenm done yet.
      if not bExceptionHandlersHaveBeenSet:
        # Note to self: when rewriting the code, make sure not to set up exception handling before the debugger has
        # attached to all processes. But do so before resuming the threads. Otherwise one or more of the processes can
        # end up having only one thread that has a suspend count of 2 and no amount of resuming will cause the process
        # to run. The reason for this is unknown, but if things are done in the correct order, this problem is avoided.
        bExceptionHandlersHaveBeenSet = False;
        oCrashInfo._fasSendCommandAndReadOutput(sExceptionHandlingCommands);
        if not oCrashInfo._bCdbRunning: return;
      # If the debugger attached to processes, mark that as done and resume threads in all processes.
      if bDebuggerIsAttachingToProcesses:
        bDebuggerIsAttachingToProcesses = False;
        for uProcessId in oCrashInfo._auProcessIds:
          oCrashInfo._fasSendCommandAndReadOutput("|~[0n%d]s;~*m;~" % uProcessId);
          if not oCrashInfo._bCdbRunning: return;
    # Run the application
    asRunApplicationOutput = oCrashInfo._fasSendCommandAndReadOutput("g");
    if not oCrashInfo._bCdbRunning: return;
    # If cdb is attaching to a process, make sure it worked.
    if bDebuggerIsAttachingToProcesses:
      fDetectFailedAttach(asRunApplicationOutput);
  # Terminate cdb.
  oCrashInfo._bCdbTerminated = True;
  oCrashInfo._fasSendCommandAndReadOutput("q");
  assert not oCrashInfo._bCdbRunning, "Debugger did not terminate when requested";
  return oErrorReport;

  # For each process that was started/attached to, do the following:
