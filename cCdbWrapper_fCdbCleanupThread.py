import os, signal, time;

def cCdbWrapper_fCdbCleanupThread(oCdbWrapper):
  # wait for debugger thread to terminate.
  oCdbWrapper.oCdbDebuggerThread.join();
  # wait for stderr thread to terminate.
  oCdbWrapper.oCdbStdErrThread.join();
  # Make sure all stdio pipes are closed and wait for debugger to terminate.
  oCdbWrapper.oCdbProcess.stdout.close();
  oCdbWrapper.oCdbProcess.stderr.close();
  oCdbWrapper.oCdbProcess.stdin.close();
  oCdbWrapper.oCdbProcess.wait();
  # Destroy the subprocess object to make even more sure all stdio pipes are closed.
  del oCdbWrapper.oCdbProcess;
  # Determine if the debugger was terminated or if the application terminated. If not, an exception is thrown later, as
  # the debugger was not expected to stop, which is an unexpected error.
  bTerminationWasExpected = oCdbWrapper.bCdbWasTerminatedOnPurpose or len(oCdbWrapper.auProcessIds) == 0;
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
  assert bTerminationWasExpected, \
      "Cdb terminated unexpectedly! StdIO:\r\n%s\r\nStdErr:\r\n%s" % (
        "\r\n".join(["\r\n".join(asCdbStdIO) for asCdbStdIO in oCdbWrapper.aasCdbStdIO]),
        "\r\n".join(oCdbWrapper.asCdbStdErr)
      );
