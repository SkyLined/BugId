import os, signal, time;

def cCdbWrapper_fCdbCleanupThread(oCdbWrapper):
  # wait for debugger thread to terminate.
  oCdbWrapper.oCdbDebuggerThread.join();
  # wait for stderr thread to terminate.
  oCdbWrapper.oCdbStdErrThread.join();
  # wait for debugger to terminate.
  oCdbWrapper.oCdbProcess.wait();
  # wait for any processes that were being debugged to terminate
  sTasklistBinaryPath = os.path.join(os.getenv("WinDir"), "System32", "tasklist.exe");
  # The last process that terminated was open when cdb reported it and may not have been closed by the OS yet.
  # It needs to be added to the list of processes that need to terminate before debugging is truely finished.
  if oCdbWrapper.uLastProcessId is not None:
    oCdbWrapper.auProcessIds.append(oCdbWrapper.uLastProcessId);
  for uProcessId in set(oCdbWrapper.auProcessIds):
    while 1:
      try:
        os.kill(uProcessId, signal.SIGTERM);
      except:
        break;
      time.sleep(0.1);
  # report that we're finished.
  oCdbWrapper.fFinishedCallback and oCdbWrapper.fFinishedCallback(oCdbWrapper.oErrorReport);
