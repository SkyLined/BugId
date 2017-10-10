import ctypes;

class cDLL(object):
  def __init__(oDLL, sDLLFilePath):
    oDLL.__oWinDLL = ctypes.WinDLL(sDLLFilePath);
  
  def fDefineFunction(oDLL, xReturnType, sFunctionName, *axArgumenTypes):
    fFunctionConstructor = ctypes.WINFUNCTYPE(xReturnType, *axArgumenTypes);
    fFunction = fFunctionConstructor(
      (sFunctionName, oDLL.__oWinDLL),
      tuple([(1, "p%d" % u, 0) for u in xrange(len(axArgumenTypes))])
    );
    setattr(oDLL, sFunctionName, fFunction);
