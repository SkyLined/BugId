import re;

def foSpecialErrorReport_CppException(oErrorReport, oCrashInfo, oException):
  assert len(oException.auParameters) >= 3, \
      "Expected a C++ Exception to have at least 3 parameters, got %d" % len(oException.auParameters);
  
  poException = oException.auParameters[1];
  asExceptionVFtablePointer = oCrashInfo._fasSendCommandAndReadOutput("dps 0x%X L1" % poException);
  if asExceptionVFtablePointer is None: return oException;
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
## http://blogs.msdn.com/b/oldnewthing/archive/2010/07/30/10044061.aspx
#  def fpReadSpecialPointer(pArray, uIndex):
#    # On x86, the array contains DWORD pointer values
#    # on x64, the array contains DWORD offsets from oException.auParameters[3]
#    uBase = oException.oProcess.sISA == "x64" and oException.auParameters[3] or 0;
#    
#    pElement = pArray + 4 * uIndex;
#    asExpressionValue = oCrashInfo._fasSendCommandAndReadOutput("dd 0x%X" % pArray);
#    if asExpressionValue is None: return None;
#    asExpressionValue = oCrashInfo._fasSendCommandAndReadOutput("? dw(0x%X)" % pElement);
#    if asExpressionValue is None: return None;
#    assert len(asExpressionValue) == 1, "Unexpected expression result:\r\n%s" % "\r\n".join(asExpressionValue);
#    oInvalidAddressMatch = re.match(r"^Memory access error at '\)'$", asExpressionValue[0]);
#    if oInvalidAddressMatch: return None;
#    oExpressionValueMatch = re.match(r"^Evaluate expression: \-?\d+ = ([A-Fa-f0-9`]+)\s*$", asExpressionValue[0]);
#    assert oExpressionValueMatch, "Unexpected expression result:\r\n%s" % "\r\n".join(asExpressionValue);
#    uOffset = int(oExpressionValueMatch.group(1).replace("`", ""), 16);
#    return uBase + uOffset;
#  
#  pExceptionHandlerInformation = oException.auParameters[2];
#  
#  papCatchableTypesPtr = fpReadSpecialPointer(pExceptionHandlerInformation, 3);
#  if papCatchableTypesPtr is None: return True;
#  
#  pFirstCatchableType = fpReadSpecialPointer(papCatchableTypesPtr, 1);
#  if pFirstCatchableType is None: return True;
#  
#  pStdTypeInfo = fpReadSpecialPointer(pFirstCatchableType, 1);
#  if pStdTypeInfo is None: return True;
#  
#  uPointerSize = {"x86": 4, "x64": 8}[oException.oProcess.sISA];
#  pClassName = pStdTypeInfo + 2 * uPointerSize;
#  asClassName = oCrashInfo._fasSendCommandAndReadOutput("da 0x%X" % pClassName);
#  if asClassName is None: return True;
#  oClassNameMatch = len(asClassName) == 1 and re.match(r'^[A-Fa-f0-9`]+\s*"(.*)"\s*$', asClassName[0]);
#  assert oClassNameMatch, "Unexpected class name output:r\n%s" % "\r\n".join(asClassName);
#  sClassName = oClassNameMatch;
#  oErrorReport.sExceptionTypeId += ":%s" % sClassName;
#  return True;
  