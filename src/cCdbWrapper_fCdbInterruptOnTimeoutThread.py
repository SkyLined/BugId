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
      # See if there have been any timeouts and remove them from the list.
      nSleep = dxBugIdConfig["nTimeoutGranularity"];
      # Time spent running before the application was resumed + time since the application was resumed.
      nApplicationRunTime = oCdbWrapper.nApplicationRunTime;
      # TODO: According to my calculations, this should never be None, but it can be, so added temporary check.
      if oCdbWrapper.nApplicationResumeTime: # this is a stop-gap and the reasons for this value being None should be found and addressed.
        nApplicationRunTime += time.clock() - oCdbWrapper.nApplicationResumeTime;
      for xTimeout in oCdbWrapper.axTimeouts[:]: # Make a copy so modifcation during the loop does not affect it.
        (nTime, fCallback) = xTimeout;
        nTimeout = nTime - nApplicationRunTime;
        if nTimeout <= 0:
          # This timeout should be fired.
          bTimeout = True;
          oCdbWrapper.axTimeouts.remove(xTimeout);
          oCdbWrapper.afActivatedTimeoutCallbacks.append(fCallback);
        elif nTimeout < nSleep:
          # This timeout is sooner than the standard sleep time: sleep shorter.
          nSleep = nTimeout;
      if bTimeout:
        # If there was a timeout, and there is no interrupt pending, interrupt cdb.
        if not oCdbWrapper.bInterruptPending:
          oCdbWrapper.bInterruptPending = True;
          oCdbWrapper.oCdbProcess.send_signal(signal.CTRL_BREAK_EVENT);
    finally:
      oCdbWrapper.oCdbLock.release();
    time.sleep(nSleep);
