import re;
from fbExceptionIsReportedAsOOM import fbExceptionIsReportedAsOOM;
from dxCrashInfoConfig import dxCrashInfoConfig;

dsId_uAddress = {     # Short             Pointer description                                   Security impact
          0x00000000: ('NULL',            "a NULL ptr",                                         "Not a security issue"),
          0XBBADBEEF: ('Assertion',       "an address that indicates an assertion has failed",  "Probably not a security issue"),
          0XBAADF00D: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
  0XBAADF00DBAADF00D: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
          0XCCCCCCCC: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
  0XCCCCCCCCCCCCCCCC: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
          0XC0C0C0C0: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
  0XC0C0C0C0C0C0C0C0: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
          0XCDCDCDCD: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
  0XCDCDCDCDCDCDCDCD: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
          0XD0D0D0D0: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
  0XD0D0D0D0D0D0D0D0: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
          0XDDDDDDDD: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
  0XDDDDDDDDDDDDDDDD: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
          0XF0F0F0F0: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
  0XF0F0F0F0F0F0F0F0: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
          0XFDFDFDFD: ('Canary',          "a pointer read from an out-of-bounds memory canary", "Potentially exploitable security issue"),
  0XF0DE7FFFF0DE7FFF: ('Poison',          "a pointer read from poisoned memory",                "Potentially exploitable security issue"),
          0XF0DE7FFF: ('Poison',          "a pointer read from poisoned memory",                "Potentially exploitable security issue"),
  0XF0090100F0090100: ('Poison',          "a pointer read from poisoned memory",                "Potentially exploitable security issue"),
          0XF0090100: ('Poison',          "a pointer read from poisoned memory",                "Potentially exploitable security issue"),
  0XFEEEFEEEFEEEFEEE: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
          0XFEEEFEEE: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
};

daasOOMExceptionTopStackFrames_sTypeId = {
  "AVW@NULL": [
    ["chrome_child.dll!WTF::partitionOutOfMemory"],
    ["mozalloc.dll!mozalloc_abort"],
    ["xul.dll!js::CrashAtUnhandlableOOM"],
    ["xul.dll!NS_ABORT_OOM"],
    ["xul.dll!StatsCompartmentCallback"],
    ["xul.dll!nsGlobalWindow::ClearDocumentDependentSlots"],
  ],
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
  uMaxAddressOffset = dxCrashInfoConfig.get("uMaxAddressOffset", 0xFFF);
  for (uBaseAddress, (sBaseId, sAddressDescription, sSecurityImpact)) in dsId_uAddress.items():
    iOffset = uAddress - uBaseAddress;
    if iOffset == 0:
      return sId, sDescription;
    if iOffset > uMaxAddressOffset: # Maybe this is wrapping:
      iOffset -= 0x100000000;
    elif iOffset < -uMaxAddressOffset: # Maybe this is wrapping:
      iOffset += 0x100000000;
    uOffset = abs(iOffset);
    if uOffset < uMaxAddressOffset:
      sAddressId = "%s%s0x%X" % (sBaseId, iOffset < 0 and "-" or "+", uOffset);
      break;
  else:
    # This is not a special marker or NULL, so it must be an invalid pointer
    asPageHeapReport = oCrashInfo._fasSendCommandAndReadOutput("!heap -p -a 0x%X" % uAddress);
    if asPageHeapReport is None: return None;
    # Sample output:
    # |    address 0e948ffc found in
    # |    _DPH_HEAP_ROOT @ 48b1000
    # |    in free-ed allocation (  DPH_HEAP_BLOCK:         VirtAddr         VirtSize)
    # |                                    e9f08bc:          e948000             2000
    # |    6d009cd2 verifier!AVrfDebugPageHeapFree+0x000000c2
    # |    77d42e20 ntdll!RtlDebugFreeHeap+0x0000003c
    # |    77cfe0da ntdll!RtlpFreeHeap+0x0006c97a
    # |    77cf5d2c ntdll!RtlpFreeHeapInternal+0x0000027e
    # |    77c90a3c ntdll!RtlFreeHeap+0x0000002c
    # <snip> no 0-day information for you!
    if (
      len(asPageHeapReport) >= 3 and \
      re.match(r"^\s+address [0-9`a-f]+ found in\s*$", asPageHeapReport[0]) and \
      re.match(r"^\s+\w+ @ [0-9`a-f]+\s*$", asPageHeapReport[1]) and \
      re.match(r"^\s+in free\-ed allocation \(\s+\w+:\s+VirtAddr\s+VirtSize\)\s*$", asPageHeapReport[2])
    ):
      # Page heap tells us the memory was freed:
      sAddressId = "Free";
      sAddressDescription = "a pointer to freed memory";
    else:
      sAddressId = "Arbitrary";
      sAddressDescription = "an invalid pointer";
    oErrorReport.dasAdditionalInformation["Page heap report for address 0x%X:" % uAddress] = asPageHeapReport;
    sSecurityImpact = "Potentially exploitable security issue";
  sTypeId = "%s%s:%s" % (oErrorReport.sExceptionTypeId, sViolationTypeId, sAddressId);
  bExceptionIsReportedAsAV = True;
  if sTypeId in daasOOMExceptionTopStackFrames_sTypeId:
    aasOOMExceptionTopStackFrames = daasOOMExceptionTopStackFrames_sTypeId[sTypeId];
    bExceptionIsReportedAsAV = not fbExceptionIsReportedAsOOM( \
        oErrorReport, oCrashInfo, oException, aasOOMExceptionTopStackFrames);
  if bExceptionIsReportedAsAV:
    
    oErrorReport.sExceptionTypeId = sTypeId;
    oErrorReport.sExceptionDescription = "Access violation while %s memory at 0x%X using %s" % \
        (sViolationTypeDescription, uAddress, sAddressDescription);
    oErrorReport.sSecurityImpact = sSecurityImpact;
  return oException;