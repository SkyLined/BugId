import re;
from dxBugIdConfig import dxBugIdConfig;

def cCdbWrapper_fHandleCreateExitProcess(oCdbWrapper, sCreateExit, uProcessId):
  # Returns true if the debugger is ready to debug the application and false if the debugger is still attaching to the
  # intial processes.
  if sCreateExit == "Create":
    # A new process was created, or attached to.
    # If cdb has created this process (i.e. it is not attaching to any process ids), this is the "main" process. If
    # fApplicationExitCallback is provided, we need to detect when the main process exists.
    if oCdbWrapper.fApplicationExitCallback and len(oCdbWrapper.auProcessIdsPendingAttach) == 0 and len(oCdbWrapper.auProcessIds) == 0:
      assert len(oCdbWrapper.auMainProcessIds) == 0, "Only one main process can exist.";
      # Note: when attaching to processes, this list is created earlier as a copy of auProcessIdsPendingAttach.
      oCdbWrapper.auMainProcessIds = [uProcessId];
    oCdbWrapper.auProcessIds.append(uProcessId);
    # Make sure all child processes of this process are debugged as well.
    # This may be superfluous, as I believe this is a global flag, not per-process, but it should have negligable
    # affect on performance and would prevent bugs if this assumption is not true.
    oCdbWrapper.fasSendCommandAndReadOutput(".childdbg 1");
    if not oCdbWrapper.bCdbRunning: return;
    # If the debugger attached to this process, remove it from the list of pending attaches:
    if len(oCdbWrapper.auProcessIdsPendingAttach) > 0:
      uPendingAttachProcessId = oCdbWrapper.auProcessIdsPendingAttach.pop(0);
      assert uPendingAttachProcessId == uProcessId, \
          "Expected to attach to process %d, got %d" % (uPendingAttachProcessId, uProcessId);
      if dxBugIdConfig["bOutputProcesses"]:
        print "* Attached to process %d." % uProcessId;
      bInitialProcessesCreated = len(oCdbWrapper.auProcessIdsPendingAttach) == 0;
    else:
      if dxBugIdConfig["bOutputProcesses"]:
        print "* New process %d." % uProcessId;
  elif sCreateExit == "Exit":
    if len(oCdbWrapper.auProcessIdsPendingAttach) > 0 and uProcessId == oCdbWrapper.auProcessIdsPendingAttach[0]:
      # The debugger attached to the process, but it terminated: first report the attach, then process the termination.
      if dxBugIdConfig["bOutputProcesses"]:
        print "* Attached to process %d." % uProcessId;
    elif len(oCdbWrapper.auProcessIdsPendingAttach) > 0 and oCdbWrapper.auProcessIdsPendingAttach[0] == uProcessId:
      # The process we just attached to has terminated (can this really happen!?)
      oCdbWrapper.auProcessIdsPendingAttach.pop(0);
    else:
      assert uProcessId in oCdbWrapper.auProcessIds, "Missing process id: %d" % uProcessId;
      oCdbWrapper.auProcessIds.remove(uProcessId);
    if oCdbWrapper.fApplicationExitCallback and (uProcessId in oCdbWrapper.auMainProcessIds):
      oCdbWrapper.fApplicationExitCallback();
    oCdbWrapper.uLastProcessId = uProcessId;
    if dxBugIdConfig["bOutputProcesses"]:
      print "* Terminated process %d" % uProcessId;
  else:
    raise AssertionError("Unknown sCreateExit value %s" % sCreateExit);
