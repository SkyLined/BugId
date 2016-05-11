from cBugReport_foAnalyzeException_STATUS_BREAKPOINT import cBugReport_foAnalyzeException_STATUS_BREAKPOINT;

dtxBugTranslations = {
  None: (
    None,
    None,
    [
      # When a 32-bit application is running on a 64-bit OS, any new processes will generate a STATUS_BREAKPOINT and
      # a status STATUS_WX86_BREAKPOINT exception. The former is recognized as the initial process breakpoint, and the
      # new process is registered. The later is not, but it can be recognized by its stack and should be ignored:
      [
        "ntdll.dll!LdrpDoDebuggerBreak",
        "ntdll.dll!LdrpInitializeProcess",
      ],
    ],
  ),
};


def cBugReport_foAnalyzeException_STATUS_WX86_BREAKPOINT(oBugReport, oCdbWrapper):
  oBugReport = oBugReport.foTranslate(dtxBugTranslations);
  if oBugReport:
    # If this is not ignored, it is treated the same as a STATUS_BREAKPOINT
    oBugReport = cBugReport_foAnalyzeException_STATUS_BREAKPOINT(oBugReport, oCdbWrapper);
  return oBugReport;

