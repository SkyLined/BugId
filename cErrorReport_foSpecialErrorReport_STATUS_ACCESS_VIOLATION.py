import re;
from dxBugIdConfig import dxBugIdConfig;

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
  "AVE:NULL": {
    "OOM": (
      "The process caused an access violation by calling NULL to indicate it was unable to allocate enough memory",
      None,
      [
        [
          "0x0",
          "chrome_child.dll!v8::base::OS::Abort",
          "chrome_child.dll!v8::Utils::ReportApiFailure",
          "chrome_child.dll!v8::Utils::ApiCheck",
          "chrome_child.dll!v8::internal::V8::FatalProcessOutOfMemory",
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
          "chrome_child.dll!WTF::partitionOutOfMemory",
        ],
        [
          "chrome_child.dll!WTF::partitionsOutOfMemoryUsingLessThan16M",
        ],
        [
          "chrome_child.dll!WTF::partitionsOutOfMemoryUsing16M",
        ],
        [
          "chrome_child.dll!WTF::partitionsOutOfMemoryUsing32M",
        ],
        [
          "chrome_child.dll!WTF::partitionsOutOfMemoryUsing64M",
        ],
        [
          "chrome_child.dll!WTF::partitionsOutOfMemoryUsing128M",
        ],
        [
          "chrome_child.dll!WTF::partitionsOutOfMemoryUsing256M",
        ],
        [
          "chrome_child.dll!WTF::partitionsOutOfMemoryUsing512M",
        ],
      ],
    ),
  },
};
ddtsDetails_uAddress_sISA = {
  "x86": {              # Id                 Description                                           Security impact
            0x00000000: ('NULL',            "a NULL ptr",                                         None),
            0xBBADBEEF: ('Assertion',       "an address that indicates an assertion has failed",  "Probably not a security issue"),
            0xBAADF00D: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
            0xCCCCCCCC: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
            0xC0C0C0C0: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
            0xCDCDCDCD: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
            0xD0D0D0D0: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
            0xDDDDDDDD: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
            0xF0F0F0F0: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
            0xFDFDFDFD: ('Canary',          "a pointer read from an out-of-bounds memory canary", "Potentially exploitable security issue"),
            0xF0DE7FFF: ('Poison',          "a pointer read from poisoned memory",                "Potentially exploitable security issue"),
            0xF0090100: ('Poison',          "a pointer read from poisoned memory",                "Potentially exploitable security issue"),
            0xFEEEFEEE: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
  },
  "AMD64": {            # Id                 Description                                           Security impact
    0x0000000000000000: ('NULL',            "a NULL ptr",                                         None),
    0xBAADF00DBAADF00D: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
    0xCCCCCCCCCCCCCCCC: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
    0xC0C0C0C0C0C0C0C0: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
    0xCDCDCDCDCDCDCDCD: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
    0xD0D0D0D0D0D0D0D0: ('Uninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
    0xDDDDDDDDDDDDDDDD: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
    0xF0F0F0F0F0F0F0F0: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
    0xF0DE7FFFF0DE7FFF: ('Poison',          "a pointer read from poisoned memory",                "Potentially exploitable security issue"),
    0xF0090100F0090100: ('Poison',          "a pointer read from poisoned memory",                "Potentially exploitable security issue"),
    0xFEEEFEEEFEEEFEEE: ('Free',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
  },
};

def fsGetSpecialExceptionTypeId(sTypeId, oFrame):
  dsFunctionName_sSpecialTypeId = ddsFunctionName_sSpecialTypeId_sTypeId.get(sTypeId, {});
  return (
    dsFunctionName_sSpecialTypeId.get(oFrame.sAddress)
    or dsFunctionName_sSpecialTypeId.get(oFrame.sSimplifiedAddress)
  );

def cErrorReport_foSpecialErrorReport_STATUS_ACCESS_VIOLATION(oErrorReport, oCdbWrapper):
  oException = oErrorReport.oException;
  # Parameter[0] = access type (0 = read, 1 = write, 8 = execute)
  # Parameter[1] = address
  assert len(oException.auParameters) == 2, \
      "Unexpected number of access violation exception parameters (%d vs 2)" % len(oException.auParameters);
  # Access violation: add the type of operation and the location to the exception id.
  sViolationTypeId = {0:"R", 1:"W", 8:"E"}.get(oException.auParameters[0], "?");
  sViolationTypeDescription = {0:"reading", 1:"writing", 8:"executing"}.get( \
        oException.auParameters[0], "accessing");
  sViolationTypeNotes = sViolationTypeId == "?" and " (the type-of-accesss code was 0x%X)" % oException.auParameters[0] or "";
  if oCdbWrapper.sCurrentISA == "x86":
    uAddress = oException.auParameters[1];
  else:
    # In AMD64 mode, cdb reports incorrect information in the exception parameters if the address is larger than
    # 0x7FFFFFFFFFFF. A work-around is to get the address from the last instruction output, which can be retreived by
    # setting the current thread.
    asLastInstructionAndAddress = oCdbWrapper.fasSendCommandAndReadOutput("~s");
    if not oCdbWrapper.bCdbRunning: return None;
    # Sample output:
    # |ntdll!LdrpValidateUserCallTarget+0xe:
    # |00007ffd`420b213e 488b14c2        mov     rdx,qword ptr [rdx+rax*8] ds:00007df5`ffb60000=????????????????
    # or
    # |chrome_child!WTF::HashTable<unsigned int,WTF::KeyValuePair<unsigned int,unsigned int>,WTF::KeyValuePairKeyExtractor,WTF::IntHash<unsigned int>,WTF::HashMapValueTraits<WTF::HashTraits<unsigned int>,WTF::HashTraits<unsigned int> >,WTF::HashTraits<unsigned int>,WTF::DefaultAllocator>::lookup+0x9 [inlined in chrome_child!blink::AXObjectCacheImpl::isAriaOwned+0xc]:
    # |60053594 ff7008          push    dword ptr [eax+8]    ds:002b:00000008=????????
    # or
    # |Tests_x64!fJMP+0x4:
    # |00007ff6`e7ab1204 ffe1            jmp     rcx {c0c0c0c0`c0c0c0c0}
    # or
    # |00000000`7fffffff ??              ???
    if len(asLastInstructionAndAddress) == 1:
      oEIPOutsideAllocatedMemoryMatch = re.match("^%s$" % "".join([
        r"([0-9a-f`]+)", r"\s+", r"\?\?", r"\s+", r"\?\?\?" # address   spaces "??" spaces "???"
      ]), asLastInstructionAndAddress[0]);
      assert oEIPOutsideAllocatedMemoryMatch, \
          "Unexpected last instruction output:\r\n%r" % "\r\n".join(asLastInstructionAndAddress);
      sAddress = oEIPOutsideAllocatedMemoryMatch.group(1);
    else:
      assert len(asLastInstructionAndAddress) == 2, \
          "Unexpected last instruction output:\r\n%r" % "\r\n".join(asLastInstructionAndAddress);
      oLastInstructionMatch = re.match("^%s$" % "".join([
        r"[0-9a-f`]+", r"\s+",      # address   spaces
        r"[0-9a-f`]+", r"\s+",      # opcode   spaces
        r"\w+", r"\s+",             # instruction   spaces
        r".*", r"\s+",              # arguments   spaces
        r"(?:",                     # either{
          r"\ws:",                  #   segment register ":"
          r"(?:[0-9a-f`]{4}:)?",    #   segment value ":"
          r"([0-9a-f`]+)",          #   (address)
          r"=\?+",                  #   "=???????"
        r"|",                       # }or{
          r"\{([0-9a-f`]+)\}",      #   "{" (address) "}"
        r")",                       # }
      ]), asLastInstructionAndAddress[1]);
      assert oLastInstructionMatch, \
          "Unexpected last instruction output:\r\n%r" % "\r\n".join(asLastInstructionAndAddress);
      sAddress = oLastInstructionMatch.group(1) or oLastInstructionMatch.group(2);
    uAddress = long(sAddress.replace("`", ""), 16);
    # The correct address can be checked against the one in the exception parameters, if they do not match, the
    # parameters contain invalid information:
    if uAddress != oException.auParameters[1]:
      sViolationTypeId = "?";
      sViolationTypeDescription = "accessing";
      sViolationTypeNotes = " (the type of accesss cannot be determined)";
  uMaxAddressOffset = dxBugIdConfig["uMaxAddressOffset"];
  
  dtsDetails_uAddress = ddtsDetails_uAddress_sISA[oCdbWrapper.sCurrentISA];
  for (uBaseAddress, (sAddressId, sAddressDescription, sSecurityImpact)) in dtsDetails_uAddress.items():
    sErrorDescription = "Access violation while %s memory at 0x%X using %s" % \
        (sViolationTypeDescription, uAddress, sAddressDescription);
    iOffset = uAddress - uBaseAddress;
    if iOffset == 0:
      break;
    uOverflow = {"x86": 1 << 32, "AMD64": 1 << 64}[oCdbWrapper.sCurrentISA];
    if iOffset > uMaxAddressOffset: # Maybe this is wrapping:
      iOffset -= uOverflow;
    elif iOffset < -uMaxAddressOffset: # Maybe this is wrapping:
      iOffset += uOverflow;
    uOffset = abs(iOffset);
    if uOffset <= uMaxAddressOffset:
      # One bug may result in different offsets for 32-bit and 64-bit versions of an application, so the value of the
      # offset cannot be used in the id. However, the fact that there is an offset is unique to the bug, so that can
      # be added:
      sAddressId += (iOffset < 0 and "-" or "+") + (uAddress & 1 and "ODD" or "EVEN");
      break;
  else:
    # This is not a special marker or NULL, so it must be an invalid pointer
    # See if it is a stack overflow:
    iOffsetFromStackBottom = oCdbWrapper.fiEvaluateExpression("@$csp-0x%X" % uAddress);
    if not oCdbWrapper.bCdbRunning: return None;
    if iOffsetFromStackBottom > -0x1000 and iOffsetFromStackBottom < 0:
      # The access violation was in the guard page below the stack, so this should be treated as a stack overflow and
      # not an access violation.
      return cErrorReport_foSpecialErrorReport_STATUS_STACK_OVERFLOW(oErrorReport, oCdbWrapper);
    # See is page heap has more details on the address at which the access violation happened:
    asPageHeapReport = oCdbWrapper.fasSendCommandAndReadOutput("!heap -p -a 0x%X" % uAddress);
    if not oCdbWrapper.bCdbRunning: return None;
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
    # <<<snip>>> no 0-day information for you!
    # |    address 07fd1000 found in
    # |    _DPH_HEAP_ROOT @ 4fd1000
    # |    in busy allocation (  DPH_HEAP_BLOCK:         UserAddr         UserSize -         VirtAddr         VirtSize)
    # |                                 7f51d9c:          7fd0fc0               40 -          7fd0000             2000
    # |    6c469abc verifier!AVrfDebugPageHeapAllocate+0x0000023c
    # <<<snip>>> no 0-day information for you!
    # There may be errors, sample output:
    # |ReadMemory error for address 5b59c3d0
    # |Use `!address 5b59c3d0' to check validity of the address.
    # <<<snip>>>
    # |*************************************************************************
    # |***                                                                   ***
    # |***                                                                   ***
    # |***    Either you specified an unqualified symbol, or your debugger   ***
    # |***    doesn't have full symbol information.  Unqualified symbol      ***
    # |***    resolution is turned off by default. Please either specify a   ***
    # |***    fully qualified symbol module!symbolname, or enable resolution ***
    asPageHeapReport = [
      x for x in asPageHeapReport
      if not re.match(r"^(%s)\s*$" % "|".join([
        "ReadMemory error for address [0-9`a-f]+",
        "Use `!address [0-9`a-f]+' to check validity of the address.",
        "\*\*\*.*\*\*\*",
      ]), x)
    ];
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
        # Page heap says the memory was freed:
        sAddressId = "Free";
        sAddressDescription = "freed memory";
        sErrorDescription = "Access violation while %s %s at 0x%X" % \
            (sViolationTypeDescription, sAddressDescription, uAddress);
      elif sBlockType == "busy":
        # Page heap says the region is allocated,  only logical explanation known is that the read was beyond the
        # end of the heap block, inside a guard page:
        uBlockAddress = long(sBlockAddress.replace("`", ""), 16);
        uBlockSize = long(sBlockSize.replace("`", ""), 16);
        uGuardPageAddress = (uBlockAddress | 0xFFF) + 1; # Follows the page in which the block is located.
        bAccessIsBeyondBlock = uAddress >= uBlockAddress + uBlockSize;
        # The same type of block may have different sizes for 32-bit and 64-bit versions of an application, so the size
        # cannot be used in the id. The same is true for the offset, but the fact that there is an offset is unique to
        # the bug, so that can be added.
        if bAccessIsBeyondBlock:
          # The access was beyond the end of the block (out-of-bounds, OOB) It can be a simple sequential buffer
          # overrun, or use of a bad offset/index. If the AV was at an address beyond the start of the guard page,
          # it cannot be the former, as the previous buffer access would have resulted in an AV as well. In this case
          # the fact that a bad index/offset was used is unique to the bug and can be added to the id:
          bAccessIsBeyondStartOfGuardPage = uAddress > uGuardPageAddress;
          sOffsetOddEven = "+" + (uAddress & 1 and "ODD" or "EVEN");
          sAddressId = "OOB" + (bAccessIsBeyondStartOfGuardPage and sOffsetOddEven or "");
          uOffsetPastEndOfBlock = uAddress - uBlockAddress - uBlockSize;
          sOffsetDescription = "%d/0x%X bytes beyond" % (uOffsetPastEndOfBlock, uOffsetPastEndOfBlock);
        else:
          # The access was inside the block but apparently the kind of access attempted is not allowed (e.g. write to
          # read-only memory). The fact that it was at the start of the block or not is unique to the bug and can be
          # added to the id:
          sOffsetOddEven = "+" + (uOffsetFromStartOfBlock & 1 and "ODD" or "EVEN");
          sAddressId = "AccessDenied" + (uOffsetFromStartOfBlock > 0 and sOffsetOddEven or "");
          sOffsetDescription = "%d/0x%X bytes into" % (uOffsetFromStartOfBlock, uOffsetFromStartOfBlock);
        sErrorDescription = "Access violation while %s memory at 0x%X; " \
            "%s a %d/0x%X byte memory block at 0x%X" % \
            (sViolationTypeDescription, uAddress, sOffsetDescription, uBlockSize, uBlockSize, uBlockAddress);
      else:
        raise NotImplemented("NOT REACHED");
      oErrorReport.atsAdditionalInformation.append(("Page heap report for address 0x%X:" % uAddress, asPageHeapReport));
    else:
      sAddressId = "Arbitrary";
      sErrorDescription = "Access violation while %s memory at 0x%X" % (sViolationTypeDescription, uAddress);
    # No matter what, this is potentially exploitable.
    sSecurityImpact = "Potentially exploitable security issue";
  oErrorReport.sErrorTypeId = "%s%s:%s" % (oErrorReport.sErrorTypeId, sViolationTypeId, sAddressId);
  oErrorReport.sErrorDescription = sErrorDescription + sViolationTypeNotes;
  oErrorReport.sSecurityImpact = sSecurityImpact;
  dtxErrorTranslations = ddtxErrorTranslations.get(oErrorReport.sErrorTypeId, None);
  if dtxErrorTranslations:
    oErrorReport = oErrorReport.foTranslateError(dtxErrorTranslations);
  if oErrorReport:
    oErrorReport.oStack.fHideTopFrames(asHiddenTopFrames);
  return oErrorReport;
