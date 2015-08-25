def fbExceptionIsReportedAsOOM(oErrorReport, oCrashInfo, oException, aasOOMExceptionTopStackFrames):
  # The last argument is a list of lists of top stack frames that indicate this exception was caused by an
  # out-of-memory (OOM) event and should be reported as such. For each list of top stack frames, see if the stack's
  # frames match and report this error as OOM if they do.
  oStack = oException.foGetStack(oCrashInfo);
  for asOOMExceptionTopStackFrames in aasOOMExceptionTopStackFrames:
    uFrameIndex = 0;
    for sOOMExceptionTopStackFrame in asOOMExceptionTopStackFrames:
      oFrame = oStack.aoFrames[uFrameIndex];
      if oFrame.sSimplifiedAddress != sOOMExceptionTopStackFrame:
        # These frames don't match: stop checking frames
        break;
    else:
      # All frames matched: report as OOM
      oErrorReport.sExceptionTypeId = "OOM";
      oErrorReport.sExceptionDescription = "The process was unable to allocate enough memory";
      oErrorReport.sSecurityImpact = "This is not a security issue";
      return True;
  # None of them matched: this is a regular fail fast exception. There's nothing extra here for now.
  return False;
