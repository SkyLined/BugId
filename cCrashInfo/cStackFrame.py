from dxCrashInfoConfig import dxCrashInfoConfig;

class cStackFrame(object):
  def __init__(oSelf, uNumber, uAddress, oModule, uModuleOffset, oFunction, uFunctionOffset):
    oSelf.uNumber = uNumber;
    oSelf.uAddress = uAddress;
    oSelf.oModule = oModule;
    oSelf.uModuleOffset = uModuleOffset;
    oSelf.oFunction = oFunction;
    oSelf.uFunctionOffset = uFunctionOffset;
    oSelf.bIsHidden = False; # Set to true if this frame should be hidden because it is not relevant.
    if oSelf.oFunction:
      oSelf.sAddress = oSelf.oFunction.sName;
      if oSelf.uFunctionOffset > 0:
        oSelf.sAddress += " + 0x%X" % oSelf.uFunctionOffset;
      elif oSelf.uFunctionOffset:
        oSelf.sAddress += " - 0x%X" % abs(oSelf.uFunctionOffset);
      oSelf.sSimplifiedAddress = oSelf.oFunction.sSimplifiedName;
      oSelf.sIdAddress = oSelf.oFunction.sName;
      if uFunctionOffset not in xrange(dxCrashInfoConfig["uMaxFunctionOffset"]):
        # The offset is negative or very large: this may not be the correct symbol. If it is, the offset is very likely
        # to change between builds. The offset should not be part of the id and a warning about the symbol is added.
        oSelf.sAddress += " (this may not be correct)";
    elif oSelf.oModule:
      oSelf.sAddress = "%s + 0x%X" % (oSelf.oModule.sBinaryName, oSelf.uModuleOffset);
      oSelf.sSimplifiedAddress = "%s+0x%X" % (oSelf.oModule.sBinaryName, oSelf.uModuleOffset);
      oSelf.sIdAddress = oSelf.sAddress;
    else:
      oSelf.sAddress = "0x%X" % oSelf.uAddress;
      oSelf.sSimplifiedAddress = "(unknown)";
      oSelf.sIdAddress = None;
