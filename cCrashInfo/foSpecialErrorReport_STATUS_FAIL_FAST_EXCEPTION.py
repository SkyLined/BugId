from fbExceptionIsReportedAsOOM import fbExceptionIsReportedAsOOM;

aasOOMExceptionTopStackFrames = [
  [
    "EDGEHTML.dll!Abandonment::InduceAbandonment",
    "EDGEHTML.dll!Abandonment::OutOfMemory",
  ],
];
def foSpecialErrorReport_STATUS_FAIL_FAST_EXCEPTION(oErrorReport, oCrashInfo, oException):
  fbExceptionIsReportedAsOOM(oErrorReport, oCrashInfo, oException, aasOOMExceptionTopStackFrames);
  return oException;

