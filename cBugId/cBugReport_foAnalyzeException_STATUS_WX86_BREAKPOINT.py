from cBugReport_foAnalyzeException_STATUS_BREAKPOINT import cBugReport_foAnalyzeException_STATUS_BREAKPOINT;

def cBugReport_foAnalyzeException_STATUS_WX86_BREAKPOINT(oBugReport, oCdbWrapper, oException):
  # Treated as if it was a STATUS_BREAKPOINT
  return cBugReport_foAnalyzeException_STATUS_BREAKPOINT(oBugReport, oCdbWrapper, oException);

