from cBugReport_CdbTerminatedUnexpectedly import cBugReport_CdbTerminatedUnexpectedly;
try:
  from Kill import fKillProcessesUntilTheyAreDead;
except:
  print "*" * 80;
  print "BugId depends on Kill, which you can download at https://github.com/SkyLined/Kill/";
  print "*" * 80;
  raise;

def cCdbWrapper_fCdbCleanupThread(oCdbWrapper):
  # wait for debugger thread to terminate.
  oCdbWrapper.oCdbStdInOutThread.join();
  # wait for stderr thread to terminate.
  oCdbWrapper.oCdbStdErrThread.join();
  # Terminate the cdb process in case it somehow is still running.
  oCdbWrapper.oCdbProcess.terminate();
  # Make sure all stdio pipes are closed.
  oCdbWrapper.oCdbProcess.stdout.close();
  oCdbWrapper.oCdbProcess.stderr.close();
  oCdbWrapper.oCdbProcess.stdin.close();
  # Wait for the cdb process to terminate
  uExitCode = oCdbWrapper.oCdbProcess.wait();
  # Destroy the subprocess object to make even more sure all stdio pipes are closed.
  del oCdbWrapper.oCdbProcess;
  # Determine if the debugger was terminated or if the application terminated. If not, an exception is thrown later, as
  # the debugger was not expected to stop, which is an unexpected error.
  bTerminationWasExpected = oCdbWrapper.bCdbWasTerminatedOnPurpose or len(oCdbWrapper.auProcessIds) == 0;
  # It was originally assumed that waiting for the cdb process to terminate would mean all process being debugged would
  # also be terminated. However, it turns out that if the application terminates, cdb.exe reports that the last process
  # is terminated while that last process is still busy terminating; the process still exists according to the OS.
  if oCdbWrapper.uLastProcessId:
    fKillProcessesUntilTheyAreDead([oCdbWrapper.uLastProcessId]);
  # There have also been cases where processes associated with an application were still running after this point in
  # the code. I have been unable to determine how this could happen but in an attempt to fix this, all process ids that
  # should be terminated are killed until they are confirmed they have terminated:
  if oCdbWrapper.auProcessIds:
    fKillProcessesUntilTheyAreDead(oCdbWrapper.auProcessIds);
  if not bTerminationWasExpected:
    oCdbWrapper.oBugReport = cBugReport_CdbTerminatedUnexpectedly(oCdbWrapper, uExitCode);
  oCdbWrapper.fFinishedCallback and oCdbWrapper.fFinishedCallback(oCdbWrapper.oBugReport);


