import re;
from fsGetAddressId import fsGetAddressId;
from fsGetExceptionTypeId import fsGetExceptionTypeId;
from cProcess import cProcess;
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
    oSelf.oStack = None;
    oSelf.sTypeId = None;
    oSelf.sDescription = None;
    oSelf.sSecurityImpact = None;
  
  @classmethod
  def foCreate(cSelf, oCrashInfo, uCode, sCodeDescription):
    oProcess = cProcess.foCreate(oCrashInfo);
    oSelf = cSelf(oProcess, uCode, sCodeDescription);
    # We do this twice to make sure symbols are loaded the first time, which may create additional symbal warnings and
    # errors that makes the output harder to parse. The second time, there will be no such output, so we can parse it
    # a lot easier.
    asExceptionRecord = oCrashInfo._fasSendCommandAndReadOutput(".exr -1");
    if asExceptionRecord is None: return None;
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
    
    # Now handle the information in the exception record and perform additional tasks as needed. Create an exception
    # id that uniquely identifies the exception and a description of the exception.
    if uCode == 0xC000027B:
      # Parameter[0] = paStowedExceptionInformationArray;
      # Parameter[1] = uStowedExceptionInformationArrayLength;
      assert len(oSelf.auParameters) == 2, \
          "Unexpected number of WinRT language exception parameters (%d vs 2)" % len(oSelf.auParameters);
      pStowedExceptionsAddress = oSelf.auParameters[0];
      uStowedExceptionsCount = oSelf.auParameters[1];
      assert uStowedExceptionsCount == 1, \
          "Unexpected number of WinRT language exception stowed exceptions (%d vs 1)" % uStowedExceptionsCount;
      # The stowed exception replaces this exception:
      return cStowedException.foCreate(oCrashInfo, oProcess, pStowedExceptionsAddress);
    elif uCode == STATUS_ACCESS_VIOLATION:
      # Access violation: add the type of operation and the location to the exception id.
      sViolationTypeId = "AV" + {0:"R", 1:"W", 8:"E"}.get(oSelf.auParameters[0], "?");
      sViolationTypeDescription = {0:"reading", 1:"writing", 8:"executing"}.get(oSelf.auParameters[0], "?");
      uAddress = oSelf.auParameters[1];
      sAddressId = fsGetAddressId(uAddress);
      oSelf.sTypeId = "%s@%s" % (sViolationTypeId, sAddressId);
      oSelf.sDescription = "%s while %s memory at 0x%X (%s)" % (sCodeDescription, sViolationTypeDescription, uAddress, sAddressId);
      uNULLMinusOffsetMinAddress = {"x64": 0xFFFFFFFFFFFF0000, "x86": 0xFFFF0000}[oProcess.sISA];
      oSelf.sSecurityImpact = ((uAddress > uNULLMinusOffsetMinAddress or uAddress < 0x10000)
        and "Not a security issue"
        or "Probably a security issue"
      );
    else:
      oSelf.sTypeId = fsGetExceptionTypeId(uCode);
      oSelf.sDescription = "%s (code 0x%08X)" % (sCodeDescription, uCode);
      oSelf.sSecurityImpact = fsGetSecurityImpact(uCode);
    
    # Get the stack
    oSelf.oStack = cStack.foCreate(oCrashInfo, oSelf.oProcess);
    if oSelf.oStack is None: return None;
    
    return oSelf;
