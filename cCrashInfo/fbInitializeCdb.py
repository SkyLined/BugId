import re;
from dxCrashInfoConfig import dxCrashInfoConfig;
from cProcess import cProcess;
from fbIsPageHeapEnabledForCurrentProcess import fbIsPageHeapEnabledForCurrentProcess;

def fDetectFailedAttach(asLines):
  for sLine in asLines:
    oFailedAttachMatch = re.match(r"^Cannot debug pid (\d+),\s*(.*?)\s*$", sLine);
    assert not oFailedAttachMatch, "\r\n".join(
        ["Failed to attach to process %s: %s" % oFailedAttachMatch.groups()] + 
        asAttachToProcess
    );

def fbInitializeCdb(oCrashInfo, asDetectedExceptions, asIgnoredExceptions, auProcessIdsPendingAttach):
  # Read the initial cdb output related to starting/attaching to the first process.
  asAttachToProcess = oCrashInfo._fasReadOutput()
  if asAttachToProcess is None: return False;
  fDetectFailedAttach(asAttachToProcess);
  # If the debugger is attaching to processes, it must resume them later.
  bMustResumeProcesses = len(auProcessIdsPendingAttach) > 0
  # For each process that was started/attached to, do the following:
  while 1:
    # Get the process id and name of the binary of the current process:
    uProcessId, sBinaryName = cProcess.ftxGetCurrentProcessIdAndBinaryName(oCrashInfo);
    if uProcessId is None: return False;
    # Make sure all child processes are debugged as well.
    if oCrashInfo._fasSendCommandAndReadOutput(".childdbg 1") is None: return False;
    oCrashInfo._auProcessIds.append(uProcessId);
    # If the debugger attached to this process, remove it from the list of pending attaches:
    if len(auProcessIdsPendingAttach) > 0:
      assert auProcessIdsPendingAttach[0] == uProcessId, \
          "Expected to attach to process %d, got %d" % (auProcessIdsPendingAttach[0], uProcessId);
      auProcessIdsPendingAttach.remove(uProcessId);
      if dxCrashInfoConfig.get("bOutputProcesses", False):
        print "* Attached to process %d/0x%X (%s)" % (uProcessId, uProcessId, sBinaryName);
    else:
      if dxCrashInfoConfig.get("bOutputProcesses", False):
        print "* Started process %d/0x%X (%s)" % (uProcessId, uProcessId, sBinaryName);
    # Make sure page heap is enabled. Not that this does not guarantee the application does not use it's own heap
    # allocator, which bypasses page heap. (eg Chrome and Internet Explorer both require some additional settings to
    # make sure they use page heap).
    bPageHeapIsEnabled = fbIsPageHeapEnabledForCurrentProcess(oCrashInfo);
    if bPageHeapIsEnabled is None: return False;
    assert bPageHeapIsEnabled, "Page heap is not enabled for %s" % sBinaryName;
    # If there are more processes to attach to, do so:
    if len(auProcessIdsPendingAttach) > 0:
      asAttachToProcess = oCrashInfo._fasSendCommandAndReadOutput(".attach 0n%d" % auProcessIdsPendingAttach[0]);
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
  for sException in asDetectedExceptions:
    if dxCrashInfoConfig.get("bOutputFirstChanceExceptions", False):
      asExceptionHandlingCommands.append("sxe %s" % sException);
    else:
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