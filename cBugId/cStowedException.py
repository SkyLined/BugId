import re;
from cStack import cStack;
from dtsTypeId_and_sSecurityImpact_by_uExceptionCode import dtsTypeId_and_sSecurityImpact_by_uExceptionCode;

class cStowedException(object):
  def __init__(oStowedException, uCode, uAddress = None, pStackTrace = None, uStackTraceSize = 0, sErrorText = None):
    oStowedException.uCode = uCode;
    oStowedException.uAddress = uAddress;
    oStowedException.pStackTrace = pStackTrace; # dpS {pStackTrace} L{uStackTraceSize}
    oStowedException.uStackTraceSize = uStackTraceSize;
    oStowedException.sErrorText = sErrorText;
    oStowedException.sTypeId = None;
    oStowedException.sDescription = None;
    oStowedException.sSecurityImpact = None;
  
  @classmethod
  def foCreate(cSelf, oCdbWrapper, pAddresses):
    pFirstAddress = oCdbWrapper.fuGetValue("poi(0x%X)" % pAddresses);
    asData = oCdbWrapper.fasSendCommandAndReadOutput(
      "dd /c0xA 0x%X L0xA; $$ Read stowed exception information" % pFirstAddress,
      bOutputIsInformative = True,
    );
    # https://msdn.microsoft.com/en-us/library/windows/desktop/dn600343%28v=vs.85%29.aspx
    # https://msdn.microsoft.com/en-us/library/windows/desktop/dn600342%28v=vs.85%29.aspx
    #StowedExceptionInformation = {
    #  0000      DWORD           dsSize
    #  0004      char[4]         sSignature      // "SE01" or "SE02"
    #  0008      HRESULT         hResultCode      
    #  000C      :2 bits         ExceptionForm   // LSB, &3 1 => with exception address and call stack, 2 => with error text
    #            :30 bits        ThreadId        // MSB, &0xfffffffc
    #  {
    #    0010    VOID*           pExceptionAddress
    #    0014    DWORD           dwStackTraceWordSize (4)
    #    0018    DWORD           StackTraceWords
    #    001c    VOID*           pStackTrace
    #  } or {
    #    0010    WCHAR*          sErrorText
    #  }
    #  0020      ULONG           NestedExceptionType; // "SE02" only
    #  0024      VOID*           NestedException;     // "SE02" only
    #}
    adwData = [];
    for sLine in asData:
      asData = re.split(r"\s+", sLine);
      asData.pop(0); # first value is address, the rest is data
      adwData.extend([int(sData, 16) for sData in asData]);
    assert len(adwData) == 10, "Unexpected data size %d extracted from %s" % (len(adwData), repr(asLines));
    dwSignature = adwData[1];
    assert dwSignature in [0x53453031, 0x53453032], "Unexpected signature 0x%X" % dwSignature;
    uCode = adwData[2];
    uExceptionForm = adwData[3] & 3;
    assert uExceptionForm in [1, 2], "Unexpected exception form %d" % uExceptionForm;
    if uExceptionForm == 1:
      oStowedException = cSelf(uCode, uAddress = adwData[4], pStackTrace = adwData[7], uStackTraceSize = adwData[6]);
    else:
      oStowedException = cSelf(uCode, sErrorText = adwData[4]);
    uNestedExceptionType = adwData[8];
    assert dwSignature == 0x53453031 or uNestedExceptionType == 0, "Unexpected nested exception type 0x%X" % adwData[8];
    
    # Create an exception id that uniquely identifies the exception and a description of the exception.
    if oStowedException.uCode in dtsTypeId_and_sSecurityImpact_by_uExceptionCode:
      oStowedException.sTypeId, oStowedException.sSecurityImpact = dtsTypeId_and_sSecurityImpact_by_uExceptionCode[oStowedException.uCode];
    else:
      oStowedException.sTypeId = "0x%08X" % oStowedException.uCode;
      oStowedException.sSecurityImpact = "Unknown";
    oStowedException.sTypeId += "(Stowed)";
    oStowedException.sDescription = "Stowed exception code 0x%08X" % oStowedException.uCode;
    return oStowedException;
