import signal, time;

from dxBugIdConfig import dxBugIdConfig;

def cCdbWrapper_fCdbInterruptOnTimeoutThread(oCdbWrapper):
  # Thread that checks if a timeout has fired every N seconds (N = nTimeoutInterruptGranularity in dxBugIdConfig).
  while 1:
    bTimeout = False;
    # Wait for cdb to be running or have terminated...
    oCdbWrapper.oCdbLock.acquire();
    try:
      if not oCdbWrapper.bCdbRunning: return;
      if not oCdbWrapper.bCdbStdInOutThreadRunning: return;
      if not oCdbWrapper.bInterruptPending:
        # Time spent running before the application was resumed + time since the application was resumed.
        nApplicationRunTime = oCdbWrapper.nApplicationRunTime + time.clock() - oCdbWrapper.nApplicationResumeTime;
#        print "@@@ time                    : %.3f " % time.clock();
#        print "@@@ application resume time : %.3f " % oCdbWrapper.nApplicationResumeTime;
#        print "@@@ application run time    : %.3f + %.3f = %.3f" % (oCdbWrapper.nApplicationRunTime, time.clock() - oCdbWrapper.nApplicationResumeTime, nApplicationRunTime);
        for (nTimeoutTime, fTimeoutCallback) in oCdbWrapper.axTimeouts: # Make a copy so modifcation during the loop does not affect it.
          if nTimeoutTime <= nApplicationRunTime:
            # If there was a timeout, and there is no interrupt pending, interrupt cdb.
            oCdbWrapper.bInterruptPending = True;
            oCdbWrapper.oCdbProcess.send_signal(signal.CTRL_BREAK_EVENT);
#            print "@@@ timeout for %.3f => %s" % (nTimeoutTime, repr(fTimeoutCallback));
            break;
          else:
#            print "@@@ sleep for %.3f => %s" % (nTimeoutTime, repr(fTimeoutCallback));
            pass;
    finally:
      oCdbWrapper.oCdbLock.release();
    time.sleep(dxBugIdConfig["nTimeoutGranularity"]);
