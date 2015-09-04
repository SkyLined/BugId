import re;
from dxCrashInfoConfig import dxCrashInfoConfig;

# Hide some functions at the top of the stack that are not relevant to the error:
asHiddenTopFrames = [
  "0x0", # AVE:NULL
  "msvcrt.dll!memcpy",
];
# Some access violations may not be an error:
ddtxErrorTranslations = {
  "AVE:Arbitrary": {
    # corpol.dll can test if DEP is enabled by storing a RET instruction in RW memory and calling it. This causes an
    # access violation if DEP is enabled, which is caught and handled. Therefore this exception should be ignored:
    None: (
      None,
      None,
      [
        [
          "(unknown)", # The location where the RET instruction is stored is not inside a module and has no symbol.
          "corpol.dll!IsNxON",
        ],
      ],
    ),
  },
  "AVW:NULL": {
    "OOM": (
      "The process caused an access violation by writing to NULL to indicate it was unable to allocate enough memory",
      None,
      [
        [
          "chrome_child.dll!WTF::partitionOutOfMemory"
        ],
      ],
    ),
  },
};
dsId_uAddress = {     # Short             Pointer description                                   Security impact
          0x00000000: ('NULL',            "a NULL ptr",                                         None),
          0xBBADBEEF: ('Assertion',       "an address that indicates an assertion has failed",  "Probably not a security issue"),
          0xBAADF00D: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
  0xBAADF00DBAADF00D: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
          0xCCCCCCCC: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
  0xCCCCCCCCCCCCCCCC: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
          0xC0C0C0C0: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
  0xC0C0C0C0C0C0C0C0: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
          0xCDCDCDCD: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
  0xCDCDCDCDCDCDCDCD: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
          0xD0D0D0D0: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
  0xD0D0D0D0D0D0D0D0: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
          0xDDDDDDDD: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
  0xDDDDDDDDDDDDDDDD: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
          0xF0F0F0F0: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
  0xF0F0F0F0F0F0F0F0: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
          0xFDFDFDFD: ('Canary',          "a pointer read from an out-of-bounds memory canary", "Potentially exploitable security issue"),
  0xF0DE7FFFF0DE7FFF: ('Poison',          "a pointer read from poisoned memory",                "Potentially exploitable security issue"),
          0xF0DE7FFF: ('Poison',          "a pointer read from poisoned memory",                "Potentially exploitable security issue"),
  0xF0090100F0090100: ('Poison',          "a pointer read from poisoned memory",                "Potentially exploitable security issue"),
          0xF0090100: ('Poison',          "a pointer read from poisoned memory",                "Potentially exploitable security issue"),
  0xFEEEFEEEFEEEFEEE: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
          0xFEEEFEEE: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
};

def fsGetSpecialExceptionTypeId(sTypeId, oFrame):
  dsFunctionName_sSpecialTypeId = ddsFunctionName_sSpecialTypeId_sTypeId.get(sTypeId, {});
  return (
    dsFunctionName_sSpecialTypeId.get(oFrame.sAddress)
    or dsFunctionName_sSpecialTypeId.get(oFrame.sSimplifiedAddress)
  );

def cErrorReport_foSpecialErrorReport_STATUS_ACCESS_VIOLATION(oErrorReport, oCrashInfo):
  oException = oErrorReport.oException;
  # Parameter[0] = access type (0 = read, 1 = write, 8 = execute)
  # Parameter[1] = address
  assert len(oException.auParameters) == 2, \
      "Unexpected number of access violation exception parameters (%d vs 2)" % len(oException.auParameters);
  # Access violation: add the type of operation and the location to the exception id.
  sViolationTypeId = {0:"R", 1:"W", 8:"E"}.get(oException.auParameters[0], "?");
  sViolationTypeDescription = {0:"reading", 1:"writing", 8:"executing"}.get( \
        oException.auParameters[0], "0x%X-ing" % oException.auParameters[0]);
  uAddress = oException.auParameters[1];
  uMaxAddressOffset = dxCrashInfoConfig["uMaxAddressOffset"];
  for (uBaseAddress, (sAddressId, sAddressDescription, sSecurityImpact)) in dsId_uAddress.items():
    sErrorDescription = "Access violation while %s memory at 0x%X using %s" % \
        (sViolationTypeDescription, uAddress, sAddressDescription);
    iOffset = uAddress - uBaseAddress;
    if iOffset == 0:
      break;
    if iOffset > uMaxAddressOffset: # Maybe this is wrapping:
      iOffset -= 0x100000000;
    elif iOffset < -uMaxAddressOffset: # Maybe this is wrapping:
      iOffset += 0x100000000;
    uOffset = abs(iOffset);
    if uOffset <= uMaxAddressOffset:
      sAddressId += "%s0x%X" % (iOffset < 0 and "-" or "+", uOffset);
      break;
  else:
    # This is not a special marker or NULL, so it must be an invalid pointer
    asPageHeapReport = oCrashInfo._fasSendCommandAndReadOutput("!heap -p -a 0x%X" % uAddress);
    if not oCrashInfo._bCdbRunning: return None;
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
    # |    address 07fd1000 found in
    # |    _DPH_HEAP_ROOT @ 4fd1000
    # |    in busy allocation (  DPH_HEAP_BLOCK:         UserAddr         UserSize -         VirtAddr         VirtSize)
    # |                                 7f51d9c:          7fd0fc0               40 -          7fd0000             2000
    # |    6c469abc verifier!AVrfDebugPageHeapAllocate+0x0000023c
    # <snip> no 0-day information for you!
    if len(asPageHeapReport) >= 4:
      assert re.match(r"^\s+address [0-9`a-f]+ found in\s*$", asPageHeapReport[0]), \
          "Unrecognized page heap report first line:\r\n%s" % "\r\n".join(asPageHeapReport);
      assert re.match(r"^\s+\w+ @ [0-9`a-f]+\s*$", asPageHeapReport[1]), \
          "Unrecognized page heap report second line:\r\n%s" % "\r\n".join(asPageHeapReport);
      oBlockTypeMatch = re.match(                       # line #3
          r"^\s+in (free-ed|busy) allocation \("        # space "in" space ("free-ed" | "busy") space  "allocation ("
          r"\s*\w+:"                                    #   [space] DPH_HEAP_BLOCK ":"
          r"(?:\s+UserAddr\s+UserSize\s+\-)?"           #   optional{ space "UserAddr" space "UserSize" space "-" }
          r"\s+VirtAddr\s+VirtSize"                     #   space "VirtAddr" space "VirtSize"
          r"\)\s*$",                                    # ")" [space]
          asPageHeapReport[2]);
      assert oBlockTypeMatch, \
          "Unrecognized page heap report third line:\r\n%s" % "\r\n".join(asPageHeapReport);
      oBlockAdressAndSizeMatch = re.match(              # line #4
          r"^\s+[0-9`a-f]+:"                            # space heap_header_address ":"
          r"(?:\s+([0-9`a-f]+)\s+([0-9`a-f]+)\s+\-)?"   # optional{ space (heap_block_address) space (heap_block_size) space "-" }
          r"\s+[0-9`a-f]+\s+[0-9`a-f]+"                 # space heap_pages_address space heap_pages_size
          r"\s*$",                                      # [space]
          asPageHeapReport[3]);
      assert oBlockAdressAndSizeMatch, \
          "Unrecognized page heap report fourth line:\r\n%s" % "\r\n".join(asPageHeapReport);
      sBlockType = oBlockTypeMatch.group(1);
      sBlockAddress, sBlockSize = oBlockAdressAndSizeMatch.groups();
      if sBlockType == "free-ed":
        # Page heap tells us the memory was freed:
        sAddressId = "Free";
        sErrorDescription = "Access violation while %s freed memory at 0x%X" % \
            (sViolationTypeDescription, uAddress);
      elif sBlockType == "busy":
        # This can only happen if the read was beyond the end of the heap block:
        uBlockAddress = int(sBlockAddress.replace("`", ""), 16);
        uBlockSize = int(sBlockSize.replace("`", ""), 16);
        uOffsetPastEndOfBlock = uAddress - uBlockAddress - uBlockSize;
        sAddressId = "OOB";
        bBlockAlignsWithEndOfPage = (uBlockAddress + uBlockSize) & 0xFFF == 0;
        bReadAlignsWithEndOfPage = uAddress & 0xFFF == 0;
        if not bReadAlignsWithEndOfPage and bBlockAlignsWithEndOfPage:
          # The block ends at a page boundary, but the read was not at offset 0 in the next page. It is assumed that
          # this means this is not a simple sequential buffer read/write overflowing, but that a bad index/offset into
          # an object is used. It is therefore assumed the object has the same size each time this issue is reproduced
          # and that the offset will not change, so this information is added to the address id.
          sAddressId += "[0x%X]+0x%X" % (uBlockSize, uOffsetPastEndOfBlock);
        sOffset = "%d/0x%X bytes beyond" % (uOffsetPastEndOfBlock, uOffsetPastEndOfBlock);
        sErrorDescription = "Access violation while %s memory at 0x%X; " \
            "%s a %d/0x%X byte memory block at 0x%X" % \
            (sViolationTypeDescription, uAddress, sOffset, uBlockSize, uBlockSize, uBlockAddress);
      oErrorReport.atsAdditionalInformation.append(("Page heap report for address 0x%X:" % uAddress, asPageHeapReport));
    else:
      sAddressId = "Arbitrary";
      sErrorDescription = "Access violation while %s memory at 0x%X" % (sViolationTypeDescription, uAddress);
    # No matter what, this is potentially exploitable.
    sSecurityImpact = "Potentially exploitable security issue";
  oErrorReport.sErrorTypeId = "%s%s:%s" % (oErrorReport.sErrorTypeId, sViolationTypeId, sAddressId);
  oErrorReport.sErrorDescription = sErrorDescription;
  oErrorReport.sSecurityImpact = sSecurityImpact;
  oErrorReport.oStack.fHideTopFrames(asHiddenTopFrames);
  dtxErrorTranslations = ddtxErrorTranslations[oErrorReport.sErrorTypeId];
  if dtxErrorTranslations:
    oErrorReport = oErrorReport.foTranslateError(dtxErrorTranslations);
  return oErrorReport;
