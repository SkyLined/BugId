import re;

def cErrorReport_foHandleException_CppException(oErrorReport, oCrashInfo, oException, oStack):
  assert len(oException.auParameters) >= 3, \
      "Expected a C++ Exception to have at least 3 parameters, got %d" % len(oException.auParameters);
  
  poException = oException.auParameters[1];
  asExceptionVFtablePointer = oCrashInfo._fasSendCommandAndReadOutput("dps 0x%X L1" % poException);
  if not oCrashInfo._bCdbRunning: return None;
  sCarriedLine = "";
  for sLine in asExceptionVFtablePointer:
    oExceptionVFtablePointerMatch = re.match(r"^[0-9A-F`]+\s*[0-9A-F`\?]+(?:\s+(.+))?\s*$", asExceptionVFtablePointer[0], re.I);
    assert oExceptionVFtablePointerMatch, "Unexpected dps result:\r\n%s" % "\r\n".join(asExceptionVFtablePointer);
    sExceptionObjectVFTablePointerSymbol = oExceptionVFtablePointerMatch.group(1);
    if sExceptionObjectVFTablePointerSymbol is None: return oException;
    sExceptionObjectSymbol = sExceptionObjectVFTablePointerSymbol.rstrip("::`vftable'");
    sCdbModuleId, sExceptionClassName = sExceptionObjectSymbol.split("!", 1);
    oErrorReport.sExceptionTypeId += ":%s" % sExceptionClassName;
    break;
  return oException;
