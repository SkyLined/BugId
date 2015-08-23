from ftsGetAddressIdAndDescription import ftsGetAddressIdAndDescription;

ddsFunctionName_sSpecialTypeId_sTypeId = {
  "AVW@NULL": {
    "chrome_child.dll!blink::reportFatalErrorInMainThread": "FatalError",
    "chrome_child.dll!WTF::partitionOutOfMemory": "OOM",
    "mozalloc.dll!mozalloc_abort": "OOM",
    "xul.dll!js::CrashAtUnhandlableOOM": "OOM",
    "xul.dll!NS_ABORT_OOM": "OOM",
    "xul.dll!StatsCompartmentCallback": "OOM",
    "xul.dll!nsGlobalWindow::ClearDocumentDependentSlots": "OOM",
  },
};

def fsGetSpecialExceptionTypeId(sTypeId, oFrame):
  dsFunctionName_sSpecialTypeId = ddsFunctionName_sSpecialTypeId_sTypeId.get(sTypeId, {});
  return (
    dsFunctionName_sSpecialTypeId.get(oFrame.sAddress)
    or dsFunctionName_sSpecialTypeId.get(oFrame.sSimplifiedAddress)
  );

def foSpecialErrorReport_STATUS_ACCESS_VIOLATION(oErrorReport, oCrashInfo, oException):
  # Parameter[0] = access type (0 = read, 1 = write, 8 = execute)
  # Parameter[1] = address
  assert len(oException.auParameters) == 2, \
      "Unexpected number of access violation exception parameters (%d vs 2)" % len(oException.auParameters);
  # Access violation: add the type of operation and the location to the exception id.
  sViolationTypeId = {0:"R", 1:"W", 8:"E"}.get(oException.auParameters[0], "?");
  sViolationTypeDescription = {0:"reading", 1:"writing", 8:"executing"}.get( \
        oException.auParameters[0], "0x%X-ing" % oException.auParameters[0]);
  uAddress = oException.auParameters[1];
  sAddressId, sAddressDescription = ftsGetAddressIdAndDescription(uAddress);
  sTypeId = "%s%s:%s" % (oErrorReport.sExceptionTypeId, sViolationTypeId, sAddressId);
  if sTypeId in ddsFunctionName_sSpecialTypeId_sTypeId:
    dsFunctionName_sSpecialTypeId = ddsFunctionName_sSpecialTypeId_sTypeId[sTypeId];
    oTopFrame = len(oException.oStack.aoFrames) > 0 and oException.oStack.aoFrames[0] or None;
    # See if its in a "special" exception and rewrite the exception type id accordingly.
    if oTopFrame and oTopFrame.oFunction:
      sTypeId = dsFunctionName_sSpecialTypeId.get(oTopFrame.sAddress) or \
          dsFunctionName_sSpecialTypeId.get(oTopFrame.sSimplifiedAddress) or \
          sTypeId;
  if sAddressId != "NULL":
    sSecurityImpact = "Not a security issue";
  else:
    sSecurityImpact = "Probably a security issue";
    asPageHeapInformation = oCrashInfo._fasSendCommandAndReadOutput("!heap -p -a 0x%X" % (0xFFFFFFFF & (0x100000004 + uAddress)));
    if asPageHeapInformation is None: return None;
    asPageHeapInformation = oCrashInfo._fasSendCommandAndReadOutput("!heap -p -a 0x%X" % uAddress);
    if asPageHeapInformation is None: return None;
    asPageHeapInformation = oCrashInfo._fasSendCommandAndReadOutput("!heap -p -a 0x%X" % (uAddress + 0x4));
    if asPageHeapInformation is None: return None;
  
  oErrorReport.sExceptionTypeId = sTypeId;
  oErrorReport.sExceptionDescription = "Access violation while %s memory at 0x%X (%s)" % \
      (sViolationTypeDescription, uAddress, sAddressDescription);
  oErrorReport.sSecurityImpact = sSecurityImpact;
  return oException;