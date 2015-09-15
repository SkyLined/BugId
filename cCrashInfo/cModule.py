from cFunction import cFunction;

class cModule(object):
  def __init__(oModule, oProcess, sCdbId, sBinaryName, uStartAddress, uEndAddress):
    oModule.sCdbId = sCdbId;
    oModule.oProcess = oProcess;
    oModule.sBinaryName = sBinaryName;
    oModule.uStartAddress = uStartAddress;
    oModule.uEndAddress = uEndAddress;
    oModule._doFunction_by_sSymbol = {};
  
  def foGetOrCreateFunction(oModule, sSymbol):
    if sSymbol not in oModule._doFunction_by_sSymbol:
      oModule._doFunction_by_sSymbol[sSymbol] = cFunction(oModule, sSymbol);
    return oModule._doFunction_by_sSymbol[sSymbol];
  
