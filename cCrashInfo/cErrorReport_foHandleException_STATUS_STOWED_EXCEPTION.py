import re;
from cStowedException import cStowedException;

def cErrorReport_foHandleException_STATUS_STOWED_EXCEPTION(oErrorReport, oCrashInfo, oException, oStack):
  # Parameter[0] = paStowedExceptionInformationArray;
  # Parameter[1] = uStowedExceptionInformationArrayLength;
  assert len(oException.auParameters) == 2, \
      "Unexpected number of WinRT language exception parameters (%d vs 2)" % len(oException.auParameters);
  pStowedExceptionsAddress = oException.auParameters[0];
  uStowedExceptionsCount = oException.auParameters[1];
  assert uStowedExceptionsCount == 1, \
      "Unexpected number of WinRT language exception stowed exceptions (%d vs 1)" % uStowedExceptionsCount;
  # The stowed exception replaces this exception:
  return cStowedException.foCreate(oCrashInfo, oException.oProcess, pStowedExceptionsAddress);
