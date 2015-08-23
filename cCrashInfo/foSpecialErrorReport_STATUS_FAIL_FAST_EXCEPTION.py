aasOOMExceptionTopStackFrames = [
  [
    "EDGEHTML.dll!Abandonment::InduceAbandonment",
    "EDGEHTML.dll!Abandonment::OutOfMemory",
  ],
];
def foSpecialErrorReport_STATUS_FAIL_FAST_EXCEPTION(oErrorReport, oCrashInfo, oException):
  for asOOMExceptionTopStackFrames in aasOOMExceptionTopStackFrames:
    uFrameIndex = 0;
    for sOOMExceptionTopStackFrame in asOOMExceptionTopStackFrames:
      oFrame = oException.oStack.aoFrames[uFrameIndex];
      if oFrame.sSimplifiedAddress != sOOMExceptionTopStackFrame:
        # These frames don't match: stop checking frames
        break;
    else:
      # All frames matched: stop checking
      return fConvertToOOMException(oErrorReport, oCrashInfo, oException);
  # None of them matched: this is a regular fail fast exception. There's nothing extra here for now.
  return oException;

def fConvertToOOMException(oErrorReport, oCrashInfo, oException):
  oErrorReport.sExceptionTypeId = "OOM";
  oErrorReport.sExceptionDescription = "The process was unable to allocate enough memory";
  oErrorReport.sSecurityImpact = "This is not a security issue";
  return oException;
