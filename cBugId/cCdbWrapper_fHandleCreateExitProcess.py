import re;
from dxBugIdConfig import dxBugIdConfig;

def fDebugOutputProcesses(oCdbWrapper, sMessage, *auArguments):
  asDebugOutput = oCdbWrapper.fasSendCommandAndReadOutput(
    '.printf "%s\\r\\n";' % sMessage,
    bShowOnlyCommandOutput = True,
  );
  if not oCdbWrapper.bCdbRunning: return;
  assert len(asDebugOutput) == 1, "Unexpected output: %s" % repr(asDebugOutput);
  if dxBugIdConfig["bOutputProcesses"]: "@@@ %s" % asDebugOutput[0];

def cCdbWrapper_fHandleNewProcess(oCdbWrapper, uProcessId):
  # If cdb has created this process (i.e. it is not attaching to any process ids), this is the "main" process. If
  # fApplicationExitCallback is provided, we need to detect when the main process exists.
  if oCdbWrapper.fApplicationExitCallback and len(oCdbWrapper.auProcessIdsPendingAttach) == 0 and len(oCdbWrapper.auProcessIds) == 0:
    assert len(oCdbWrapper.auMainProcessIds) == 0, "Only one main process can exist.";
    # Note: when attaching to processes, this list is created earlier as a copy of auProcessIdsPendingAttach.
    oCdbWrapper.auMainProcessIds = [uProcessId];
  oCdbWrapper.auProcessIds.append(uProcessId);
  # If the debugger attached to this process, remove it from the list of pending attaches:
  if len(oCdbWrapper.auProcessIdsPendingAttach) > 0:
    uPendingAttachProcessId = oCdbWrapper.auProcessIdsPendingAttach.pop(0);
    assert uPendingAttachProcessId == uProcessId, \
        "Expected to attach to process %d, got %d" % (uPendingAttachProcessId, uProcessId);
    fDebugOutputProcesses(oCdbWrapper, "* Attached to process %d/0x%X." % (uProcessId, uProcessId));
    bInitialProcessesCreated = len(oCdbWrapper.auProcessIdsPendingAttach) == 0;
  else:
    fDebugOutputProcesses(oCdbWrapper, "* New process %d/0x%X." % (uProcessId, uProcessId));
    # Make sure all child processes of this process are debugged as well.
  # This may be superfluous, as I believe this is a global flag, not per-process, but it should have negligable
  # affect on performance and would prevent bugs if this assumption is not true.
  oCdbWrapper.fasSendCommandAndReadOutput(".childdbg 1; $$ Debug child processes");
  if not oCdbWrapper.bCdbRunning: return;

def cCdbWrapper_fHandleCreateExitProcess(oCdbWrapper, sCreateExit, uProcessId):
  # Returns true if the debugger is ready to debug the application and false if the debugger is still attaching to the
  # intial processes.
  if sCreateExit == "Create":
    # A new process was created, or attached to.
    cCdbWrapper_fHandleNewProcess(oCdbWrapper, uProcessId);
  elif sCreateExit == "Exit":
    if uProcessId not in oCdbWrapper.auProcessIds:
      # A new process was created and terminated immediately: handle creation first:
      cCdbWrapper_fHandleNewProcess(oCdbWrapper, uProcessId);
    oCdbWrapper.auProcessIds.remove(uProcessId);
    if oCdbWrapper.fApplicationExitCallback and (uProcessId in oCdbWrapper.auMainProcessIds):
      oCdbWrapper.fApplicationExitCallback();
    oCdbWrapper.uLastProcessId = uProcessId;
    fDebugOutputProcesses(oCdbWrapper, "* Terminated process %d/0x%X." % (uProcessId, uProcessId));
  else:
    raise AssertionError("Unknown sCreateExit value %s" % sCreateExit);
