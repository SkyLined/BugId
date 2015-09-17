import hashlib;
from dxCrashInfoConfig import dxCrashInfoConfig;

class cStackFrame(object):
  def __init__(oStackFrame, uNumber, uAddress, sUnloadedModuleFileName, oModule, uModuleOffset, oFunction, uFunctionOffset):
    oStackFrame.uNumber = uNumber;
    oStackFrame.uAddress = uAddress;
    oStackFrame.sUnloadedModuleFileName = sUnloadedModuleFileName;
    oStackFrame.oModule = oModule;
    oStackFrame.uModuleOffset = uModuleOffset;
    oStackFrame.oFunction = oFunction;
    oStackFrame.uFunctionOffset = uFunctionOffset;
    oStackFrame.bIsHidden = False; # Set to true if this frame should be hidden because it is not relevant.
    if oStackFrame.oFunction:
      oStackFrame.sAddress = oStackFrame.oFunction.sName;
      if oStackFrame.uFunctionOffset > 0:
        oStackFrame.sAddress += " + 0x%X" % oStackFrame.uFunctionOffset;
      elif oStackFrame.uFunctionOffset:
        oStackFrame.sAddress += " - 0x%X" % abs(oStackFrame.uFunctionOffset);
      oStackFrame.sSimplifiedAddress = oStackFrame.oFunction.sSimplifiedName;
      sIdInput = oStackFrame.oFunction.sName;
      if uFunctionOffset not in xrange(dxCrashInfoConfig["uMaxFunctionOffset"]):
        # The offset is negative or very large: this may not be the correct symbol. If it is, the offset is very likely
        # to change between builds. The offset should not be part of the id and a warning about the symbol is added.
        oStackFrame.sAddress += " (this may not be correct)";
    elif oStackFrame.oModule:
      oStackFrame.sAddress = "%s + 0x%X" % (oStackFrame.oModule.sBinaryName, oStackFrame.uModuleOffset);
      oStackFrame.sSimplifiedAddress = "%s+0x%X" % (oStackFrame.oModule.sBinaryName, oStackFrame.uModuleOffset);
      sIdInput = oStackFrame.sAddress;
    elif sUnloadedModuleFileName:
      oStackFrame.sAddress = "%s + ??" % sUnloadedModuleFileName;
      oStackFrame.sSimplifiedAddress = "sUnloadedModuleFileName+??";
      sIdInput = None;
    else:
      oStackFrame.sAddress = "0x%X" % oStackFrame.uAddress;
      oStackFrame.sSimplifiedAddress = "(unknown)";
      sIdInput = None;
    if sIdInput is None:
      oStackFrame.sId = None;
    else:
      oHasher = hashlib.md5();
      oHasher.update(sIdInput);
      oStackFrame.sId = "%02X" % ord(oHasher.digest()[0]);

  def fbHide(oStackFrame, asFrameAddresses):
    if oStackFrame.sAddress in asFrameAddresses or oStackFrame.sSimplifiedAddress in asFrameAddresses: # and it should be,
      oStackFrame.bIsHidden = True; # hide it.
    return oStackFrame.bIsHidden;
