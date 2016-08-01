# Hide some functions at the top of the stack that are merely helper functions and not relevant to the bug:
asHiddenTopFrames = [
  "EDGEHTML.dll!Abandonment::InduceAbandonment",
  "EDGEHTML.dll!Abandonment::OutOfMemory",
  "EDGEHTML.dll!CAttrArray::Set",
  "EDGEHTML.dll!CBuffer::GrowBuffer",
  "EDGEHTML.dll!CHtPvPvBaseT<...>::Grow",
  "EDGEHTML.dll!CImplAry::AppendIndirect<36>",
  "EDGEHTML.dll!CImplAry::EnsureSize",
  "EDGEHTML.dll!CImplAry::EnsureSizeWorker",
  "EDGEHTML.dll!CImplAry::InitSize",
  "EDGEHTML.dll!CModernArray<...>::EnsureLargerCapacity",
  "EDGEHTML.dll!CStr::_Alloc",
  "EDGEHTML.dll!CStr::Set",
  "EDGEHTML.dll!_HeapRealloc<1>",
  "EDGEHTML.dll!Ptls6::TsAllocMemoryCore",
];
# Some fail fast exceptions may indicate an out-of-memory bug:
dtxBugTranslations = {
  "OOM": (
    "The process triggered a fail-fast exception to indicate it was unable to allocate enough memory",
    None,
    [
      [ # Edge
#        "EDGEHTML.dll!Abandonment::InduceAbandonment",
        "EDGEHTML.dll!Abandonment::OutOfMemory",
      ],
    ],
  ),
  "Assert": (
    "An assertion failed",
    None,
    [
      [ # Edge
#        "EDGEHTML.dll!Abandonment::InduceAbandonment",
        "EDGEHTML.dll!Abandonment::CheckHRESULT",
      ],
      [
#        "EDGEHTML.dll!Abandonment::InduceAbandonment",
        "EDGEHTML.dll!Abandonment::CheckHRESULTStrict",
      ],
      [
#        "EDGEHTML.dll!Abandonment::InduceAbandonment",
        "EDGEHTML.dll!Abandonment::InvalidArguments",
      ],
    ],
  ),
};

def cBugReport_foAnalyzeException_STATUS_FAIL_FAST_EXCEPTION(oBugReport, oCdbWrapper, oException):
  # cdb does not known this exception and reports "Unknown exception (code 0xC0000602)" as the description.
  oBugReport.sBugDescription = "Fail fast exception (code 0x%X)" % oException.uCode;
  oBugReport = oBugReport.foTranslate(dtxBugTranslations);
  if oBugReport:
    oBugReport.oStack.fHideTopFrames(asHiddenTopFrames);
  return oBugReport;

