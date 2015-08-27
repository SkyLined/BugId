import re;
from fsGetExceptionTypeId import fsGetExceptionTypeId;
from cStack import cStack;
from cStowedException import cStowedException;
from fsGetSecurityImpact import fsGetSecurityImpact;
from NTSTATUS import *;

class cException(object):
  def __init__(oSelf, oProcess, uCode, sCodeDescription):
    oSelf.oProcess = oProcess;
    oSelf.uCode = uCode;
    oSelf.sCodeDescription = sCodeDescription;
    oSelf.uAddress = None;
    oSelf.sAddressSymbol = None;
    oSelf.uFlags = None;
    oSelf.auParameters = None;
    oSelf.sDetails = None;
    oSelf.sTypeId = None;
    oSelf.sDescription = None;
    oSelf.sSecurityImpact = None;
  
  @classmethod
  def foCreate(cSelf, oCrashInfo, oProcess, uCode, sCodeDescription):
    oSelf = cSelf(oProcess, uCode, sCodeDescription);
    asExceptionRecord = oCrashInfo._fasSendCommandAndReadOutput(".exr -1");
    if asExceptionRecord is None: return None;
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
    oSelf.sTypeId = fsGetExceptionTypeId(uCode);
    oSelf.sDescription = "%s (code 0x%08X)" % (sCodeDescription, uCode);
    oSelf.sSecurityImpact = fsGetSecurityImpact(uCode);
    return oSelf;
  
  def foGetStack(oSelf, oCrashInfo):
    # This is not going to chance, so we can cache it:
    if not hasattr(oSelf, "oStack"):
      oSelf.oStack = cStack.foCreate(oCrashInfo, oSelf.oProcess);
    return oSelf.oStack;

