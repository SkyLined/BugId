# Hide some functions at the top of the stack that are merely helper functions and not relevant to the bug:
asHiddenTopFrames = [
  # Functions that are used to trigger a breakpoint:
  "KERNELBASE.dll!RaiseFailFastException",
  "KERNELBASE.dll!TerminateProcessOnMemoryExhaustion",
];
def cBugReport_foAnalyzeException_STATUS_FAILFAST_OOM_EXCEPTION(oBugReport, oCdbWrapper, oException):
  oBugReport.oStack.fHideTopFrames(asHiddenTopFrames);
  return oBugReport;
