import time;

def cCdbWrapper_fxSetTimeout(oCdbWrapper, nTimeout, fTimeoutCallback, *axTimeoutCallbackArguments):
#  print "@@@ timeout in %.1f seconds: %s" % (nTimeout, repr(fTimeoutCallback));
  assert nTimeout >= 0, "Negative timeout does not make sense";
  oCdbWrapper.oApplicationTimeLock.acquire();
  try:
    nTimeoutTime = oCdbWrapper.nApplicationRunTime + nTimeout;
    if oCdbWrapper.nApplicationResumeTime:
      # The application is currently running, make an estimate for how long to determine when to stop the application:
      nTimeoutTime += time.clock() - oCdbWrapper.nApplicationResumeTime;
  finally:
    oCdbWrapper.oApplicationTimeLock.release();
  xTimeout = (nTimeoutTime, fTimeoutCallback, axTimeoutCallbackArguments);
  oCdbWrapper.oTimeoutsLock.acquire();
  try:
    oCdbWrapper.axTimeouts.append(xTimeout);
#    print "@@@ number of timeouts: %d" % len(oCdbWrapper.axTimeouts);
  finally:
    oCdbWrapper.oTimeoutsLock.release();
  return xTimeout;

def cCdbWrapper_fClearTimeout(oCdbWrapper, xTimeout):
  (nTimeoutTime, fTimeoutCallback, axTimeoutCallbackArguments) = xTimeout;
  oCdbWrapper.oTimeoutsLock.acquire();
  try:
    if xTimeout in oCdbWrapper.axTimeouts:
      oCdbWrapper.axTimeouts.remove(xTimeout);
#      print "@@@ cleared timeout: %s" % repr(fTimeoutCallback);
#    else:
#      # Timeout has already fired and been removed.
#      print "@@@ ignored clear fired timeout: %s" % repr(fTimeoutCallback);
#    print "@@@ number of timeouts: %d" % len(oCdbWrapper.axTimeouts);
  finally:
    oCdbWrapper.oTimeoutsLock.release();