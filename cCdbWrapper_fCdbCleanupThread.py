import os, signal, time;

def cCdbWrapper_fCdbCleanupThread(oCdbWrapper):
  # All processes started by BugId must be stopped in order to do a clean exit. The first process to get started is
  # the cdb.exe process:
  auProcessIdsToKill = [oCdbWrapper.oCdbProcess.pid]
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
  # It was originally assumed that waiting for the cdb process to terminate would mean all process were terminated.
  # However, it turns out that if the application terminates, cdb.exe reports that the last process is terminated
  # while it is busy terminating; the process itself still exists according to the OS. There have also been cases where
  # processes associated with an application were running after this point in the code. I have been unable to determine
  # how this could happen but, in an attempt to fix this, all process ids that should be terminated at this point are
  # added to the list. This includes:
  # * the cdb.exe process (which was added to the list before)
  # * all processes that are being debugged (if the application hasn't terminated).
  auProcessIdsToKill.extend(oCdbWrapper.auProcessIds);
  # * the last process that terminated (if the application has terminated).
  if oCdbWrapper.uLastProcessId is not None:
    auProcessIdsToKill.append(oCdbWrapper.uLastProcessId);
  # Calling os.kill for a running process should kill it without throwing an exception. Calling os.kill for a
  # terminated process should throw an exception. So repeatedly calling os.kill until an exception is thrown makes
  # sure the process is terminated. Do this for all processes that should be terminated:
  for uProcessId in set(auProcessIdsToKill):
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
