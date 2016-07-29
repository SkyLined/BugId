import threading;
from cCdbWrapper import cCdbWrapper;

class cBugId(object):
  def __init__(oBugId, **dxArguments):
    # Replace fFinishedCallback with a wrapper that signals the finished event.
    # This event is used by the fWait function to wait for the process to
    # finish.
    oBugId.__fExternalFinishedCallback = dxArguments.get("fFinishedCallback");
    dxArguments["fFinishedCallback"] = oBugId.__fInternalFinishedHandler;
    oBugId.__oFinishedEvent = threading.Event();
    # Run the application in a debugger and catch exceptions.
    oBugId.__oCdbWrapper = cCdbWrapper(**dxArguments);
  
  def fStop(oBugId):
    oBugId.__oCdbWrapper.fStop();
  
  def fWait(oBugId):
    while 1:
      try:
        oBugId.__oFinishedEvent.wait();
      except KeyboardInterrupt:
        continue;
      break;
  
  def fSetCheckForExcessiveCPUUsageTimeout(oBugId, nTimeout):
    oBugId.__oCdbWrapper.fSetCheckForExcessiveCPUUsageTimeout(nTimeout);
  
  def fxSetTimeout(oBugId, nTimeout, fCallback, *axArguments):
    return oBugId.__oCdbWrapper.fxSetTimeout(nTimeout, fCallback, *axArguments);
  
  def fClearTimeout(oBugId, xTimeout):
    oBugId.__oCdbWrapper.fClearTimeout(xTimeout);
  
  def fnApplicationRunTime(oBugId):
    return oBugId.__oCdbWrapper.fnApplicationRunTime();
  
  def fbFinished(oBugId):
    oBugId.__oFinishedEvent.isSet();
  
  def __fInternalFinishedHandler(oBugId, oBugReport):
    oBugId.oBugReport = oBugReport;
    oBugId.__oFinishedEvent.set();
    oBugId.__fExternalFinishedCallback and oBugId.__fExternalFinishedCallback(oBugReport);
