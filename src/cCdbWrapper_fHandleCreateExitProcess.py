import re;
from dxBugIdConfig import dxBugIdConfig;

def cCdbWrapper_fHandleCreateExitProcess(oCdbWrapper, sCreateExit, uProcessId):
  # Returns true if the debugger is ready to debug the application and false if the debugger is still attaching to the
  # intial processes.
  if sCreateExit == "Create":
    # A new process was created, or attached to.
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
    else:
      if dxBugIdConfig["bOutputProcesses"]:
        print "* New process %d." % uProcessId;
  elif sCreateExit == "Exit":
    assert uProcessId in oCdbWrapper.auProcessIds, "Missing process id: %d" % uProcessId;
    oCdbWrapper.auProcessIds.remove(uProcessId);
    oCdbWrapper.uLastProcessId = uProcessId;
    if dxBugIdConfig["bOutputProcesses"]:
      print "* Terminated process %d" % uProcessId;
  else:
    raise AssertionError("Unknown sCreateExit value %s" % sCreateExit);
