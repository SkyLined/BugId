import re;
from cException_fSetSecurityImpact import cException_fSetSecurityImpact;
from cException_fSetTypeId import cException_fSetTypeId;
from cStack import cStack;
from cStowedException import cStowedException;
from NTSTATUS import *;

class cException(object):
  def __init__(oSelf, oProcess, uCode, sCodeDescription, _asExceptionRecord):
    oSelf.oProcess = oProcess;
    oSelf.uCode = uCode;
    oSelf.sCodeDescription = sCodeDescription;
    oSelf._asExceptionRecord = _asExceptionRecord; # This is here merely to be able to debug issues - it is not used.
    oSelf.uAddress = None;
    oSelf.sAddressSymbol = None;
    oSelf.uFlags = None;
    oSelf.auParameters = None;
    oSelf.sDetails = None;
    oSelf.sTypeId = None;
    oSelf.sDescription = None;
    oSelf.sSecurityImpact = None;
  
  def foGetStack(oSelf, oCrashInfo):
    # This is not going to chance, so we can cache it:
    if not hasattr(oSelf, "oStack"):
      oSelf.oStack = cStack.foCreate(oCrashInfo, oSelf.oProcess);
    return oSelf.oStack;
  
  @classmethod
  def foCreate(cSelf, oCrashInfo, oProcess, uCode, sCodeDescription):
    asExceptionRecord = oCrashInfo._fasSendCommandAndReadOutput(".exr -1");
    oSelf = cSelf(oProcess, uCode, sCodeDescription, asExceptionRecord);
    if not oCrashInfo._bCdbRunning: return None;
    uParameterCount = None;
    uParameterIndex = None;
    for sLine in asExceptionRecord:
      oNameValueMatch = re.match(r"^\s*%s\s*$" % (
        r"(\w+)(?:\[(\d+)\])?\:\s+"     # (name) optional{ "[" (index) "]" } ":" whitespace
        r"([0-9A-F`]+)"                  # (value)
        r"(?:\s+\((.*)\))?"             # optional{ whitespace "(" (symbol || description) ")" }
      ), sLine, re.I);
      if oNameValueMatch:
        sName, sIndex, sValue, sDetails = oNameValueMatch.groups();
        uValue = int(sValue.replace("`", ""), 16);
        if sName == "ExceptionAddress":
          oSelf.uAddress = uValue;
          oSelf.sAddressSymbol = sDetails;
        elif sName == "ExceptionCode":
          assert uValue == uCode, \
              "Exception record has an unexpected ExceptionCode value (0x%08X vs 0x%08X)" % (uValue, uCode);
          assert sDetails is None or sDetails == sCodeDescription, \
              "Exception record has an unexpected ExceptionCode description (%s vs %s)" % \
                  (repr(sDetails), repr(sCodeDescription));
        elif sName == "ExceptionFlags":
          oSelf.uFlags = uValue;
        elif sName == "NumberParameters":
          uParameterCount = uValue;
          uParameterIndex = 0;
          oSelf.auParameters = [];
        elif sName == "Parameter":
          assert int(sIndex, 16) == uParameterIndex, \
              "Unexpected parameter #0x%s vs 0x%X" % (sIndex, uParameterIndex);
          oSelf.auParameters.append(uValue);
          uParameterIndex += 1;
        else:
          raise AssertionError("Unknown exception record value %s" % sLine);
      elif oSelf.sDetails is None:
        oSelf.sDetails = sLine;
      else:
        raise AssertionError("Superfluous exception record line %s" % sLine);
    assert oSelf.uAddress is not None, \
        "Exception record is missing an ExceptionAddress value";
    assert oSelf.uFlags is not None, \
        "Exception record is missing an ExceptionFlags value";
    assert uParameterCount is not None, \
        "Exception record is missing an NumberParameters value";
    assert uParameterCount == len(oSelf.auParameters), \
        "Unexpected number of parameters (%d vs %d)" % (len(oSelf.auParameters), uParameterCount);
    # Now handle the information in the exception record to create an exception id that uniquely identifies the
    # type of exception and a description of the exception.
    cException_fSetTypeId(oSelf);
    oSelf.sDescription = "%s (code 0x%08X)" % (sCodeDescription, uCode);
    cException_fSetSecurityImpact(oSelf);
    return oSelf;
