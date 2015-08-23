import re;

def foSpecialErrorReport_STATUS_STOWED_EXCEPTION(oErrorReport, oCrashInfo, oException):
  # Parameter[0] = paStowedExceptionInformationArray;
  # Parameter[1] = uStowedExceptionInformationArrayLength;
  assert len(oSelf.auParameters) == 2, \
      "Unexpected number of WinRT language exception parameters (%d vs 2)" % len(oSelf.auParameters);
  pStowedExceptionsAddress = oSelf.auParameters[0];
  uStowedExceptionsCount = oSelf.auParameters[1];
  assert uStowedExceptionsCount == 1, \
      "Unexpected number of WinRT language exception stowed exceptions (%d vs 1)" % uStowedExceptionsCount;
  # The stowed exception replaces this exception:
  return cStowedException.foCreate(oCrashInfo, oProcess, pStowedExceptionsAddress);
