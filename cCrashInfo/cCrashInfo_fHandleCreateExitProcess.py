import re;
from dxCrashInfoConfig import dxCrashInfoConfig;

def cCrashInfo_fHandleCreateExitProcess(oCrashInfo, sCreateExit, uProcessId):
  if sCreateExit == "Create":
    # A new process was created, or attached to.
    oCrashInfo._auProcessIds.append(uProcessId);
    # Make sure all child processes of this process are debugged as well.
    # This may be superfluous, as I believe this is a global flag, not per-process, but it should have negligable
    # affect on performance and would prevent bugs if this assumption is not true.
    oCrashInfo._fasSendCommandAndReadOutput(".childdbg 1");
    if not oCrashInfo._bCdbRunning: return;
    if not oCrashInfo._bCdbRunning: return;
    # If the debugger attached to this process, remove it from the list of pending attaches:
    if len(oCrashInfo._auProcessIdsPendingAttach) > 0:
      uPendingAttachProcessId = oCrashInfo._auProcessIdsPendingAttach.pop(0);
      assert uPendingAttachProcessId == uProcessId, \
          "Expected to attach to process %d, got %d" % (uPendingAttachProcessId, uProcessId);
      if dxCrashInfoConfig["bOutputProcesses"]:
        print "* Attached to process %d." % uProcessId;
    else:
      if dxCrashInfoConfig["bOutputProcesses"]:
        print "* New process %d." % uProcessId;
  elif sCreateExit == "Exit":
    assert uProcessId in oCrashInfo._auProcessIds, \
        "Missing process id: %d\r\n%s" % (uProcessId, "\r\n".join(oCrashInfo.asCdbIO));
    oCrashInfo._auProcessIds.remove(uProcessId);
    oCrashInfo._uLastProcessId = uProcessId;
    if dxCrashInfoConfig["bOutputProcesses"]:
      print "* Terminated process %d" % uProcessId;
  else:
    raise AssertionError("Unknown sCreateExit value %s" % sCreateExit);