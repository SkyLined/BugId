import os, re, subprocess, time;
from dxBugIdConfig import dxBugIdConfig;

sOSISA = os.getenv("PROCESSOR_ARCHITEW6432") or os.getenv("PROCESSOR_ARCHITECTURE"); # "x86" or "AMD64"

def fKillProcessesAndWaitForTermination(auProcessIds):
  # Calling os.kill for a running process should kill it without throwing an exception. Calling os.kill for a
  # terminated process should throw an exception with code 87 (invalid argument). So repeatedly calling os.kill until
  # the right exception is thrown can be used to make sure the process is terminated.
  for x in xrange(60):
    assert auProcessIds, "Nothing to kill";
    sKillBinaryPath = dxBugIdConfig["sKillBinaryPath_%s" % sOSISA];
    asKillCommand = [sKillBinaryPath, "--pids"] + [str(uProcessId) for uProcessId in auProcessIds];
    oKillProcess = subprocess.Popen(asKillCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE);
    (sStdOut, sStdErr) = oKillProcess.communicate();
    oKillProcess.stdout.close();
    oKillProcess.stderr.close();
    oKillProcess.wait();
    assert not sStdErr, "Error killing processes:\r\n%s" % sStdErr;
    asErrors = [];
    for sLine in sStdOut.split("\n"):
      oTerminatedOrErrorMatch = re.match(r"^(?:%s)\r?$" % "|".join([
        r"\+ Terminated process (\d+)\.",
        r"\* Process (\d+) does not exist\.",
        r"\* Process (\d+) was already terminated\.",
        r"\- (.*)",
      ]), sLine);
      if oTerminatedOrErrorMatch:
        sProcessId1, sProcessId2, sProcessId3, sError = oTerminatedOrErrorMatch.groups();
        if sError:
          asErrors.append(sError);
        else:
          auProcessIds.remove(long(sProcessId1 or sProcessId2 or sProcessId3));
    if not asErrors:
      return;
    time.sleep(1);
  raise AssertionError("Error killing processes:\r\n%s" % sStdOut);

def cCdbWrapper_fCdbCleanupThread(oCdbWrapper):
  # wait for debugger thread to terminate.
  oCdbWrapper.oCdbDebuggerThread.join();
  # wait for stderr thread to terminate.
  oCdbWrapper.oCdbStdErrThread.join();
  # Make sure all stdio pipes are closed.
  oCdbWrapper.oCdbProcess.stdout.close();
  oCdbWrapper.oCdbProcess.stderr.close();
  oCdbWrapper.oCdbProcess.stdin.close();
  # Make sure the cdb process terminates
  oCdbWrapper.oCdbProcess.wait();
  fKillProcessesAndWaitForTermination([oCdbWrapper.oCdbProcess.pid]);
  # Destroy the subprocess object to make even more sure all stdio pipes are closed.
  del oCdbWrapper.oCdbProcess;
  # Determine if the debugger was terminated or if the application terminated. If not, an exception is thrown later, as
  # the debugger was not expected to stop, which is an unexpected error.
  bTerminationWasExpected = oCdbWrapper.bCdbWasTerminatedOnPurpose or len(oCdbWrapper.auProcessIds) == 0;
  # It was originally assumed that waiting for the cdb process to terminate would mean all process being debugged would
  # also be terminated. However, it turns out that if the application terminates, cdb.exe reports that the last process
  # is terminated while that last process is still busy terminating; the process still exists according to the OS.
  if oCdbWrapper.uLastProcessId:
    fKillProcessesAndWaitForTermination([oCdbWrapper.uLastProcessId]);
  # There have also been cases where processes associated with an application were still running after this point in
  # the code. I have been unable to determine how this could happen but in an attempt to fix this, all process ids that
  # should be terminated are killed until they are confirmed they have terminated:
  if oCdbWrapper.auProcessIds:
    fKillProcessesAndWaitForTermination(oCdbWrapper.auProcessIds);
  assert bTerminationWasExpected, \
      "Cdb terminated unexpectedly! StdIO:\r\n%s\r\nStdErr:\r\n%s" % (
        "\r\n".join(["\r\n".join(asCdbStdIO) for asCdbStdIO in oCdbWrapper.aasCdbStdIO]),
        "\r\n".join(oCdbWrapper.asCdbStdErr)
      );
  oCdbWrapper.fFinishedCallback and oCdbWrapper.fFinishedCallback(oCdbWrapper.oErrorReport);
