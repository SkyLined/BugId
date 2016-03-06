# Hide some functions at the top of the stack that are merely helper functions and not relevant to the error:
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
# Some fail fast exceptions may indicate an out-of-memory error:
dtxErrorTranslations = {
  "OOM": (
    "The process triggered a fail-fast exception to indicate it was unable to allocate enough memory",
    None,
    [
      [ # Edge
        "EDGEHTML.dll!Abandonment::InduceAbandonment",
        "EDGEHTML.dll!Abandonment::OutOfMemory",
      ],
    ],
  ),
  "Assert": (
    "An assertion failed",
    None,
    [
      [ # Edge
        "EDGEHTML.dll!Abandonment::InduceAbandonment",
        "EDGEHTML.dll!Abandonment::CheckHRESULT",
      ],
    ],
  ),
};

def cErrorReport_foSpecialErrorReport_STATUS_FAIL_FAST_EXCEPTION(oErrorReport, oCdbWrapper):
  # cdb does not known this exception and reports "Unknown exception (code 0xC0000602)" as the description.
  oErrorReport.sErrorDescription = "Fail fast exception (code 0x%X)" % oErrorReport.oException.uCode;
  oErrorReport = oErrorReport.foTranslateError(dtxErrorTranslations);
  if oErrorReport:
    oErrorReport.oStack.fHideTopFrames(asHiddenTopFrames);
  return oErrorReport;

