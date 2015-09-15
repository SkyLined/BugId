import re;
from cException_fSetSecurityImpact import cException_fSetSecurityImpact;
from cException_fSetTypeId import cException_fSetTypeId;
from cStack import cStack;
from cStowedException import cStowedException;
from NTSTATUS import *;

class cException(object):
  def __init__(oException, oProcess, uCode, sCodeDescription, _asExceptionRecord):
    oException.oProcess = oProcess;
    oException.uCode = uCode;
    oException.sCodeDescription = sCodeDescription;
    oException._asExceptionRecord = _asExceptionRecord; # This is here merely to be able to debug issues - it is not used.
    oException.uAddress = None;
    oException.sAddressSymbol = None;
    oException.uFlags = None;
    oException.auParameters = None;
    oException.sDetails = None;
    oException.sTypeId = None;
    oException.sDescription = None;
    oException.sSecurityImpact = None;
  
  def foGetStack(oException, oCrashInfo):
    # This is not going to chance, so we can cache it:
    if not hasattr(oException, "oStack"):
      oException.oStack = cStack.foCreate(oCrashInfo, oException.oProcess);
    return oException.oStack;
  
  @classmethod
  def foCreate(cException, oCrashInfo, oProcess, uCode, sCodeDescription):
    asExceptionRecord = oCrashInfo._fasSendCommandAndReadOutput(".exr -1");
    oException = cException(oProcess, uCode, sCodeDescription, asExceptionRecord);
    if not oCrashInfo._bCdbRunning: return None;
    # Sample output:
    # |ExceptionAddress: 00007ff6b0f81204 (Tests_x64!fJMP+0x0000000000000004)
    # |   ExceptionCode: c0000005 (Access violation)
    # |  ExceptionFlags: 00000000
    # |NumberParameters: 2
    # |   Parameter[0]: 0000000000000000
    # |   Parameter[1]: ffffffffffffffff
    # |Attempt to read from address ffffffffffffffff
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
        uValue = long(sValue.replace("`", ""), 16);
        if sName == "ExceptionAddress":
          oException.uAddress = uValue;
          oException.sAddressSymbol = sDetails;
        elif sName == "ExceptionCode":
          assert uValue == uCode, \
              "Exception record has an unexpected ExceptionCode value (0x%08X vs 0x%08X)" % (uValue, uCode);
          assert sDetails is None or sDetails == sCodeDescription, \
              "Exception record has an unexpected ExceptionCode description (%s vs %s)" % \
                  (repr(sDetails), repr(sCodeDescription));
        elif sName == "ExceptionFlags":
          oException.uFlags = uValue;
        elif sName == "NumberParameters":
          uParameterCount = uValue;
          uParameterIndex = 0;
          oException.auParameters = [];
        elif sName == "Parameter":
          assert long(sIndex, 16) == uParameterIndex, \
              "Unexpected parameter #0x%s vs 0x%X" % (sIndex, uParameterIndex);
          oException.auParameters.append(uValue);
          uParameterIndex += 1;
        else:
          raise AssertionError("Unknown exception record value %s" % sLine);
      elif oException.sDetails is None:
        oException.sDetails = sLine;
      else:
        raise AssertionError("Superfluous exception record line %s" % sLine);
    assert oException.uAddress is not None, \
        "Exception record is missing an ExceptionAddress value";
    assert oException.uFlags is not None, \
        "Exception record is missing an ExceptionFlags value";
    assert uParameterCount is not None, \
        "Exception record is missing an NumberParameters value";
    assert uParameterCount == len(oException.auParameters), \
        "Unexpected number of parameters (%d vs %d)" % (len(oException.auParameters), uParameterCount);
    # Now handle the information in the exception record to create an exception id that uniquely identifies the
    # type of exception and a description of the exception.
    cException_fSetTypeId(oException);
    oException.sDescription = "%s (code 0x%08X)" % (sCodeDescription, uCode);
    cException_fSetSecurityImpact(oException);
    return oException;
