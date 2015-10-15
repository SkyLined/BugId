import os, re;
from cModule import cModule;

class cProcess(object):
  def __init__(oProcess, uProcessId, sBinaryName):
    oProcess.uProcessId = uProcessId;
    oProcess.sBinaryName = sBinaryName;
  
  def __str__(oProcess):
    return 'Process(%s #%d)' % (oProcess.sBinaryName, oProcess.uProcessId);
  
  @classmethod
  def foCreate(cProcess, oCdbWrapper):
    (uProcessId, sBinaryName) = oCdbWrapper.ftxGetProcessIdAndBinaryNameForCurrentProcess();
    if not oCdbWrapper.bCdbRunning: return None;
    return cProcess(uProcessId, sBinaryName);
