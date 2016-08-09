import re;

# Hide some functions at the top of the stack that are merely helper functions and not relevant to the bug:
asHiddenTopFrames = [
  "KERNELBASE.dll!RaiseException",
  "msvcrt.dll!CxxThrowException",
  "msvcrt.dll!_CxxThrowException",
  "MSVCR110.dll!CxxThrowException",
  "MSVCR110.dll!_CxxThrowException",
]
# Some C++ exceptions may indicate an out-of-memory bug.
ddtxBugTranslations_by_uExceptionCode = {
  0xe06d7363: { # This entry was created before the code determined the exception class name...
    "OOM": (
      "The process triggered a C++ exception to indicate it was unable to allocate enough memory",
      None,
      [
        [
          "KERNELBASE.dll!RaiseException",
          "msvcrt.dll!_CxxThrowException",
          "jscript9.dll!Js::Throw::OutOfMemory",
        ],
      ],
    ),
  },
};
ddtxBugTranslations_by_sExceptionCallName = {
  "std::bad_alloc": {
    "OOM": (
      "The process triggered a std::bad_alloc C++ exception to indicate it was unable to allocate enough memory",
      None,
      [
        [
          "KERNELBASE.dll!RaiseException",
          "msvcrt.dll!_CxxThrowException",
        ],
      ],
    ),
  },
};

def cBugReport_foAnalyzeException_Cpp(oBugReport, oCdbWrapper, oException):
  # Attempt to get the symbol of the virtual function table of the object that was thrown and add that the the type id:
  assert len(oException.auParameters) >= 3, \
      "Expected a C++ Exception to have at least 3 parameters, got %d" % len(oException.auParameters);
  poException = oException.auParameters[1];
  asExceptionVFtablePointer = oCdbWrapper.fasSendCommandAndReadOutput(
    "dps 0x%X L1; $$ Get C++ exception vftable pointer" % poException,
    bOutputIsInformative = True,
  );
  if not oCdbWrapper.bCdbRunning: return None;
  sCarriedLine = "";
  for sLine in asExceptionVFtablePointer:
    oExceptionVFtablePointerMatch = re.match(r"^[0-9A-F`]+\s*[0-9A-F`\?]+(?:\s+(.+))?\s*$", asExceptionVFtablePointer[0], re.I);
    assert oExceptionVFtablePointerMatch, "Unexpected dps result:\r\n%s" % "\r\n".join(asExceptionVFtablePointer);
    sExceptionObjectVFTablePointerSymbol = oExceptionVFtablePointerMatch.group(1);
    if sExceptionObjectVFTablePointerSymbol is None: break;
    sExceptionObjectSymbol = sExceptionObjectVFTablePointerSymbol.rstrip("::`vftable'");
    if "!" not in sExceptionObjectSymbol:
      # No symbol information available, just an address
      dtxBugTranslations = ddtxBugTranslations_by_uExceptionCode.get(oException.uCode);
      if dtxBugTranslations:
        oBugReport = oBugReport.foTranslate(dtxBugTranslations);
      break;
    sModuleCdbId, sExceptionClassName = sExceptionObjectSymbol.split("!", 1);
    oBugReport.sBugTypeId += ":%s" % sExceptionClassName;
    dtxBugTranslations = ddtxBugTranslations_by_sExceptionCallName.get(sExceptionClassName);
    if dtxBugTranslations:
      oBugReport = oBugReport.foTranslate(dtxBugTranslations);
    break;
  if oBugReport:
    oBugReport.oStack.fHideTopFrames(asHiddenTopFrames);
  return oBugReport;
