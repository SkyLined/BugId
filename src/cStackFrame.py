import hashlib;
from dxBugIdConfig import dxBugIdConfig;

class cStackFrame(object):
  def __init__(oStackFrame, uNumber, sCdbSource, uAddress, sUnloadedModuleFileName, oModule, uModuleOffset, oFunction, uFunctionOffset):
    oStackFrame.uNumber = uNumber;
    oStackFrame.sCdbSource = sCdbSource;
    oStackFrame.uAddress = uAddress;
    oStackFrame.sUnloadedModuleFileName = sUnloadedModuleFileName;
    oStackFrame.oModule = oModule;
    oStackFrame.uModuleOffset = uModuleOffset;
    oStackFrame.oFunction = oFunction;
    oStackFrame.uFunctionOffset = uFunctionOffset;
    oStackFrame.bIsHidden = False; # Set to true if this frame should be hidden because it is not relevant.
    if oFunction:
      oStackFrame.sAddress = oFunction.sName;
      if uFunctionOffset:
        oStackFrame.sAddress += " %s 0x%X" % (uFunctionOffset > 0 and "+" or "-", abs(uFunctionOffset));
      oStackFrame.sSimplifiedAddress = oFunction.sSimplifiedName;
      sIdInput = oFunction.sIdInput;
      if uFunctionOffset not in xrange(dxBugIdConfig["uMaxFunctionOffset"]):
        # The offset is negative or very large: this may not be the correct symbol. If it is, the offset is very likely
        # to change between builds. The offset should not be part of the id and a warning about the symbol is added.
        oStackFrame.sAddress += " (this may not be correct)";
    elif oModule:
      oStackFrame.sAddress = "%s + 0x%X" % (oModule.sBinaryName, uModuleOffset);
      oStackFrame.sSimplifiedAddress = "%s+0x%X" % (oModule.sBinaryName, uModuleOffset);
      # Adding offset makes it more unique and thus allows distinction between two different crashes, but seriously
      # reduces the chance of getting the same id for the same crash in different builds.
      sIdInput = "%s+0x%X" % (oModule.sIdInput, uModuleOffset);
    elif sUnloadedModuleFileName:
      if uModuleOffset is not None:
        oStackFrame.sAddress = "%s + 0x%X" % (sUnloadedModuleFileName, uModuleOffset);
        oStackFrame.sSimplifiedAddress = "%s+0x%X" % (sUnloadedModuleFileName, uModuleOffset);
      else:
        oStackFrame.sAddress = "%s + ??" % sUnloadedModuleFileName;
        oStackFrame.sSimplifiedAddress = "sUnloadedModuleFileName+??";
      sIdInput = None;
    else:
      oStackFrame.sAddress = "0x%X" % uAddress;
      oStackFrame.sSimplifiedAddress = "(unknown)";
      sIdInput = None;
    if sIdInput is None:
      oStackFrame.sId = None;
    else:
      oHasher = hashlib.md5();
      oHasher.update(sIdInput);
      oStackFrame.sId = "%02X" % ord(oHasher.digest()[0]);

  def fbHide(oStackFrame, asFrameAddresses, bFrameAddressesAreAlreadyLowered = False):
    # Hide the frame if the address or simplified address matches any of the supplied values (ignoring case):
    if not bFrameAddressesAreAlreadyLowered:
      asFrameAddresses = [s.lower() for s in asFrameAddresses];
    if oStackFrame.sAddress.lower() in asFrameAddresses or oStackFrame.sSimplifiedAddress.lower() in asFrameAddresses:
      oStackFrame.bIsHidden = True; # hide it.
    return oStackFrame.bIsHidden;
