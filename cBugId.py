import threading;
from cCdbWrapper import cCdbWrapper;

class cBugId(object):
  def __init__(oBugId, **dxArguments):
    oBugId.__fExternalFinishedCallback = dxArguments.get("fFinishedCallback");
    dxArguments["fFinishedCallback"] = oBugId.__fInternalFinishedHandler;
    oBugId.__oFinishedEvent = threading.Event();
    oBugId.__oCdbWrapper = cCdbWrapper(**dxArguments);
  
  def fStop(oBugId):
    oBugId.__oCdbWrapper.fStop();
  
  def fWait(oBugId):
    oBugId.__oFinishedEvent.wait();
  
  def __fInternalFinishedHandler(oBugId, oErrorReport):
    oBugId.oErrorReport = oErrorReport;
    oBugId.__oFinishedEvent.set();
    oBugId.__fExternalFinishedCallback and oBugId.__fExternalFinishedCallback(oErrorReport);