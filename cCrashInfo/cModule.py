from cFunction import cFunction;

class cModule(object):
  def __init__(oSelf, oProcess, sBinaryName, uStartAddress, uEndAddress):
    oSelf.oProcess = oProcess;
    oSelf.sBinaryName = sBinaryName;
    oSelf.uStartAddress = uStartAddress;
    oSelf.uEndAddress = uEndAddress;
    oSelf._doFunction_by_sSymbol = {};
  
  def foGetOrCreateFunction(oSelf, sSymbol):
    if sSymbol not in oSelf._doFunction_by_sSymbol:
      oSelf._doFunction_by_sSymbol[sSymbol] = cFunction(oSelf, sSymbol);
    return oSelf._doFunction_by_sSymbol[sSymbol];
  
