import re;
from dxCrashInfoConfig import dxCrashInfoConfig;
from cProcess import cProcess;
from NTSTATUS import *;

auFirstChanceExceptionCodes = [
  STATUS_GUARD_PAGE_VIOLATION,
  STATUS_DATATYPE_MISALIGNMENT,
  STATUS_ACCESS_VIOLATION,
  STATUS_IN_PAGE_ERROR,
  STATUS_ILLEGAL_INSTRUCTION,
  STATUS_ARRAY_BOUNDS_EXCEEDED,
  STATUS_PRIVILEGED_INSTRUCTION,
  STATUS_STACK_BUFFER_OVERRUN,
  STATUS_FAIL_FAST_EXCEPTION,
];
asSecondChanceExceptions = [
  "*", "asrt", "aph", "bpe", "dz", "eh", "iov", 
  "isc", "lsq", "sov", "sse", "ssec", "vcpp", "wkd", "wob", "wos",
];
asIgnoredExceptions = [
  "ch", "hc", "ibp", "ld", "ud", "wos",
  # "cpr" and "epr" are missing because they are special-cased in the code, see below
];

def fDetectFailedAttach(asLines):
  for sLine in asLines:
    oFailedAttachMatch = re.match(r"^Cannot debug pid (\d+),\s*(.*?)\s*$", sLine);
    assert not oFailedAttachMatch, "\r\n".join(
        ["Failed to attach to process %s: %s" % oFailedAttachMatch.groups()] + 
        asAttachToProcess
    );

def cCrashInfo_fbInitialize(oCrashInfo):
  # Read the initial cdb output related to starting/attaching to the first process.
  asAttachToProcess = oCrashInfo._fasReadOutput()
  if asAttachToProcess is None: return False;
  fDetectFailedAttach(asAttachToProcess);
  # If the debugger is attaching to processes, it must resume them later.
  bMustResumeProcesses = len(oCrashInfo._auProcessIdsPendingAttach) > 0
  # For each process that was started/attached to, do the following:
  while 1:
    # Get the process id and name of the binary of the current process:
    uProcessId, sBinaryName = cProcess.ftxGetCurrentProcessIdAndBinaryName(oCrashInfo);
    if uProcessId is None: return False;
    # Make sure all child processes are debugged as well.
    if oCrashInfo._fasSendCommandAndReadOutput(".childdbg 1") is None: return False;
    oCrashInfo._auProcessIds.append(uProcessId);
    # If the debugger attached to this process, remove it from the list of pending attaches:
    if len(oCrashInfo._auProcessIdsPendingAttach) > 0:
      uAttachedProcessId = oCrashInfo._auProcessIdsPendingAttach.pop(0);
      assert uAttachedProcessId == uProcessId, \
          "Expected to attach to process %d, got %d" % (uAttachedProcessId, uProcessId);
      if dxCrashInfoConfig.get("bOutputProcesses", False):
        print "* Attached to process %d/0x%X (%s)" % (uProcessId, uProcessId, sBinaryName);
    else:
      if dxCrashInfoConfig.get("bOutputProcesses", False):
        print "* Started process %d/0x%X (%s)" % (uProcessId, uProcessId, sBinaryName);
    # If there are more processes to attach to, do so:
    if len(oCrashInfo._auProcessIdsPendingAttach) > 0:
      asAttachToProcess = oCrashInfo._fasSendCommandAndReadOutput(".attach 0n%d" % oCrashInfo._auProcessIdsPendingAttach[0]);
      if asAttachToProcess is None: return False;
      fDetectFailedAttach(asAttachToProcess);
      # Continue the application to attach to the process.
      if oCrashInfo._fasSendCommandAndReadOutput("g") is None: return False;
    else:
      # otherwise stop.
      break;
  if bMustResumeProcesses:
    # All processes that the debugger attached to must be resumed:
    for uProcessId in oCrashInfo._auProcessIds:
      if oCrashInfo._fasSendCommandAndReadOutput("|~[0n%d]s;~*m" % uProcessId) is None: return False;
  
  # Set up exception handling
  asExceptionHandlingCommands = [];
  # request second chance debugger break for certain exceptions that indicate the application has a bug.
  for uExceptionCode in auFirstChanceExceptionCodes:
    asExceptionHandlingCommands.append("sxe 0x%08X" % uExceptionCode);
  for sException in asSecondChanceExceptions:
    asExceptionHandlingCommands.append("sxd %s" % sException);
  # ignore certain other exceptions
  for sException in asIgnoredExceptions:
    asExceptionHandlingCommands.append("sxi %s" % sException);
  # To be able to track which processes are running at any given time while the application being debugged,
  # cpr and epr must be enabled.
  # Also, if epr is disabled the debugger will silently exit when the application terminates.
  # To distinguish this from other unexpected terminations of the debugger, epr must also be enabled.
  asExceptionHandlingCommands.append("sxe cpr");
  asExceptionHandlingCommands.append("sxe epr");

  # Execute all commands in the list and stop if cdb terminates in the mean time.
  for sCommand in asExceptionHandlingCommands:
    if oCrashInfo._fasSendCommandAndReadOutput(sCommand) is None:
      return False;

  return True;