import re;
from dxBugIdConfig import dxBugIdConfig;
from fsGetNumberDescription import fsGetNumberDescription;
from fsGetOffsetDescription import fsGetOffsetDescription;
from sBlockHTMLTemplate import sBlockHTMLTemplate;

# Hide some functions at the top of the stack that are not relevant to the bug:
asHiddenTopFramesForReadAndWriteAVs = [ # Note: matches are case insensitive
  # A bad pointer can cause an exception in a memcpy. The real problem is not in that function.
  "mshtml.dll!memcpy",
  "msvcrt.dll!memcpy",
  "msvcrt.dll!memcpy_s",
  # A bad function pointer can cause an exception in CFG code that checks it. The real problem is not in that function.
  "ntdll.dll!LdrpValidateUserCallTarget",
  "ntdll.dll!LdrpValidateUserCallTargetBitMapCheck",
];
# Some access violations may not be a bug:
ddtxBugTranslations = {
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
#  "AVW:NULL+EVEN": {
#    # Chrome can trigger this exception but appears to handle it as well. It's not considered a bug at this time.
#    None: (
#      None,
#      None,
#      [
#        [
#          "ntdll.dll!RtlpWaitOnCriticalSection",
#        ]
#      ]
#    )
#  },
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
        [
          "chrome_child.dll!WTF::partitionExcessiveAllocationSize",
        ],
      ],
    ),
  },
};
ddtsDetails_uSpecialAddress_sISA = {
  "x86": {              # Id                 Description                                           Security impact
            0x00000000: ('NULL',                  "a NULL ptr",                                         None),
            0xBBADBEEF: ('Assertion',             "an address that indicates an assertion has failed",  None),
            0xBAADF00D: ('PoisonUninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
            0xCCCCCCCC: ('PoisonUninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
            0xC0C0C0C0: ('PoisonUninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
            0xCDCDCDCD: ('PoisonUninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
            0xD0D0D0D0: ('PoisonUninitialized',   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
            0xDDDDDDDD: ('PoisonFree',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
            0xF0F0F0F0: ('PoisonFree',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
            0xFDFDFDFD: ('PoisonOOB',             "a pointer read from an out-of-bounds memory canary", "Potentially exploitable security issue"),
            0xF0DE7FFF: ('Poison',                "a pointer read from poisoned memory",                "Potentially exploitable security issue"),
            0xF0090100: ('Poison',                "a pointer read from poisoned memory",                "Potentially exploitable security issue"),
            0xFEEEFEEE: ('PoisonFree',            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
            # https://hg.mozilla.org/releases/mozilla-beta/rev/8008235a2429
            0XE4E4E4E4: ("PoisonUninitialized",   "a pointer that was not initialized",                 "Potentially exploitable security issue"),
            0XE5E5E5E5: ("PoisonFree",            "a pointer read from poisoned freed memory",          "Potentially exploitable security issue"),
  },
  "x64": {              # Id                 Description                                           Security impact
    0x0000000000000000: ('NULL',                  "a NULL ptr",                                         None),
    # Note that on x64, addresses with the most significant bit set cannot be allocated in user-land. Since BugId is expected to analyze only user-land
    # applications, accessing such an address is not expected to be an exploitable security issue.
    0xBAADF00DBAADF00D: ('PoisonUninitialized',   "a pointer that was not initialized",                 None),
    0xCCCCCCCCCCCCCCCC: ('PoisonUninitialized',   "a pointer that was not initialized",                 None),
    0xC0C0C0C0C0C0C0C0: ('PoisonUninitialized',   "a pointer that was not initialized",                 None),
    0xCDCDCDCDCDCDCDCD: ('PoisonUninitialized',   "a pointer that was not initialized",                 None),
    0xD0D0D0D0D0D0D0D0: ('PoisonUninitialized',   "a pointer that was not initialized",                 None),
    0xDDDDDDDDDDDDDDDD: ('PoisonFree',            "a pointer read from poisoned freed memory",          None),
    0xF0F0F0F0F0F0F0F0: ('PoisonFree',            "a pointer read from poisoned freed memory",          None),
    0xF0DE7FFFF0DE7FFF: ('Poison',                "a pointer read from poisoned memory",                None),
    0xF0090100F0090100: ('Poison',                "a pointer read from poisoned memory",                None),
    0xFEEEFEEEFEEEFEEE: ('PoisonFree',            "a pointer read from poisoned freed memory",          None),
    # https://hg.mozilla.org/releases/mozilla-beta/rev/8008235a2429
    0xE4E4E4E4E4E4E4E4: ("PoisonUninitialized",   "a pointer that was not initialized",                 None),
    0xE5E5E5E5E5E5E5E5: ("PoisonFree",            "a pointer read from poisoned freed memory",          None),
  },
};

def fsGetSpecialExceptionTypeId(sTypeId, oFrame):
  dsFunctionName_sSpecialTypeId = ddsFunctionName_sSpecialTypeId_sTypeId.get(sTypeId, {});
  return (
    dsFunctionName_sSpecialTypeId.get(oFrame.sAddress)
    or dsFunctionName_sSpecialTypeId.get(oFrame.sSimplifiedAddress)
  );


def cBugReport_foAnalyzeException_STATUS_ACCESS_VIOLATION(oBugReport, oCdbWrapper, oException):
  # Parameter[0] = access type (0 = read, 1 = write, 8 = execute)
  # Parameter[1] = address
  assert len(oException.auParameters) == 2, \
      "Unexpected number of access violation exception parameters (%d vs 2)" % len(oException.auParameters);
  # Access violation: add the type of operation and the location to the exception id.
  sViolationTypeId = {0:"R", 1:"W", 8:"E"}.get(oException.auParameters[0], "?");
  sViolationTypeDescription = {0:"reading", 1:"writing", 8:"executing"}.get(oException.auParameters[0], "accessing");
  sViolationTypeNotes = sViolationTypeId == "?" and " (the type-of-accesss code was 0x%X)" % oException.auParameters[0] or "";
  uAddress = oException.auParameters[1];
  if uAddress == 0xFFFFFFFFFFFFFFFF and sViolationTypeId == "R":
    # In x64 mode, current processors will thrown an exception when you use an address larger than 0x7FFFFFFFFFFF and
    # smaller than 0xFFFF800000000000. In such cases cdb reports incorrect information in the exception parameters,
    # e.g. the address is always reported as 0xFFFFFFFFFFFFFFFF was and the access type is always "read".
    # A partial work-around is to get the address from the last instruction output, which can be retreived by asking
    # cdb to output disassembly and address after each command. This may also tell us if the access type was "execute".
    oCdbWrapper.fasSendCommandAndReadOutput( \
        ".prompt_allow +dis +ea; $$ Enable disassembly and address in cdb prompt");
    # Do this twice in case the first time requires loading symbols, which can output junk that makes parsing ouput difficult.
    if not oCdbWrapper.bCdbRunning: return None;
    oCdbWrapper.fasSendCommandAndReadOutput( \
        "~s; $$ Show disassembly and optional symbol loading stuff");
    if not oCdbWrapper.bCdbRunning: return None;
    asLastInstructionAndAddress = oCdbWrapper.fasSendCommandAndReadOutput(
      "~s; $$ Show disassembly",
      bOutputIsInformative = True,
    );
    if not oCdbWrapper.bCdbRunning: return None;
    # Revert to not showing disassembly and address:
    oCdbWrapper.fasSendCommandAndReadOutput( \
        ".prompt_allow -dis -ea; $$ Revert to clean cdb prompt");
    if not oCdbWrapper.bCdbRunning: return None;
    # Sample output:
    # |00007ffd`420b213e 488b14c2        mov     rdx,qword ptr [rdx+rax*8] ds:00007df5`ffb60000=????????????????
    # or
    # |60053594 ff7008          push    dword ptr [eax+8]    ds:002b:00000008=????????
    # or
    # |00007ff6`e7ab1204 ffe1            jmp     rcx {c0c0c0c0`c0c0c0c0}
    # or
    # |00000000`7fffffff ??              ???
    assert len(asLastInstructionAndAddress) == 1, \
        "Unexpected last instruction output:\r\n%r" % "\r\n".join(asLastInstructionAndAddress);
    oEIPOutsideAllocatedMemoryMatch = re.match("^%s$" % "".join([
      r"([0-9a-f`]+)", r"\s+", r"\?\?", r"\s+", r"\?\?\?" # address   spaces "??" spaces "???"
    ]), asLastInstructionAndAddress[0]);
    if oEIPOutsideAllocatedMemoryMatch:
      sAddress = oEIPOutsideAllocatedMemoryMatch.group(1);
      sViolationTypeId = "E";
      sViolationTypeDescription = "executing";
    else:
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
      ]), asLastInstructionAndAddress[0]);
      assert oLastInstructionMatch, \
          "Unexpected last instruction output:\r\n%r" % "\r\n".join(asLastInstructionAndAddress);
      if oLastInstructionMatch.group(1):
        sAddress = oLastInstructionMatch.group(1);
        sViolationTypeId = "?";
        sViolationTypeDescription = "accessing";
        sViolationTypeNotes = " (the type of accesss must be read or write, but cannot be determined)";
      else:
        sAddress = oLastInstructionMatch.group(2);
        sViolationTypeId = "E";
        sViolationTypeDescription = "executing";
    uAddress = long(sAddress.replace("`", ""), 16);
  
  sMemoryDumpDescription = "Memory near access violation address 0x%X" % uAddress;
  
  if sViolationTypeId == "E":
    # Hide the stack frame for the address at which the execute access violation happened: (e.g. 0x0 for a NULL pointer).
    asHiddenTopFrames = ["0x%X" % uAddress];
  else:
    # Hide common 
    asHiddenTopFrames = asHiddenTopFramesForReadAndWriteAVs;
  
  dtsDetails_uSpecialAddress = ddtsDetails_uSpecialAddress_sISA[oCdbWrapper.sCurrentISA];
  for (uSpecialAddress, (sAddressId, sAddressDescription, sSecurityImpact)) in dtsDetails_uSpecialAddress.items():
    sBugDescription = "Access violation while %s memory at 0x%X using %s." % \
        (sViolationTypeDescription, uAddress, sAddressDescription);
    iOffset = uAddress - uSpecialAddress;
    if iOffset != 0:
      uOverflow = {"x86": 1 << 32, "x64": 1 << 64}[oCdbWrapper.sCurrentISA];
      if iOffset > dxBugIdConfig["uMaxAddressOffset"]: # Maybe this is wrapping:
        iOffset -= uOverflow;
      elif iOffset < -dxBugIdConfig["uMaxAddressOffset"]: # Maybe this is wrapping:
        iOffset += uOverflow;
    uOffset = abs(iOffset);
    if uOffset <= dxBugIdConfig["uMaxAddressOffset"]:
      oBugReport.sBugTypeId = "AV%s:%s%s" % (sViolationTypeId, sAddressId, fsGetOffsetDescription(iOffset));
      break;
  else:
    if uAddress >= 0x800000000000:
      oBugReport.sBugTypeId = "AV%s:Invalid" % sViolationTypeId;
      sBugDescription = "Access violation while %s memory at the invalid address 0x%X." % (sViolationTypeDescription, uAddress);
      sSecurityImpact = "Potentially exploitable security issue.";
    else:
      # This is not a special marker or NULL, so it must be an invalid pointer
      # See is page heap has more details on the address at which the access violation happened:
      asPageHeapReport = oCdbWrapper.fasSendCommandAndReadOutput(
        "!heap -p -a 0x%X; $$ Get page heap information" % uAddress,
        bOutputIsInformative = True,
      );
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
      # TODO: error resolving symbol should be handled by attempting to reload them, similar to cCdbWrapper_fasGetStack
      if len(asPageHeapReport) >= 4 and not asPageHeapReport[0].startswith("unable to resolve ntdll!"):
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
          oBugReport.sBugTypeId = "UAF%s" % sViolationTypeId;
          sAddressDescription = "freed memory";
          sBugDescription = "Access violation while %s %s at 0x%X indicates a use-after-free." % \
              (sViolationTypeDescription, sAddressDescription, uAddress);
          sSecurityImpact = "Potentially exploitable security issue.";
        elif sBlockType == "busy":
          # Page heap says the region is allocated, so the heap block must be inaccessible or the access must have been
          # beyond the end of the heap block, in  the next memory page:
          uBlockAddress = long(sBlockAddress.replace("`", ""), 16);
          uBlockSize = long(sBlockSize.replace("`", ""), 16);
          uGuardPageAddress = (uBlockAddress | 0xFFF) + 1; # Follows the page in which the block is located.
          bAccessIsBeyondBlock = uAddress >= uBlockAddress + uBlockSize;
          # The same type of block may have different sizes for 32-bit and 64-bit versions of an application, so the size
          # cannot be used in the id. The same is true for the offset, but the fact that there is an offset is unique to
          # the bug, so that can be added.
          if bAccessIsBeyondBlock:
            uOffsetPastEndOfBlock = uAddress - uBlockAddress - uBlockSize;
            sOffsetDescription = "%d/0x%X bytes beyond" % (uOffsetPastEndOfBlock, uOffsetPastEndOfBlock);
            sBugDescription = "Out-of-bounds access violation while %s memory at 0x%X; %s a %d/0x%X byte heap block at 0x%X." % \
                (sViolationTypeDescription, uAddress, sOffsetDescription, uBlockSize, uBlockSize, uBlockAddress);
            if uOffsetPastEndOfBlock != 0:
              if sViolationTypeDescription == "writing":
                # Page heap stores the heap as close as possible to the edge of a page, taking into account that the start
                # of the heap block must be properly aligned. Bytes between the heap block and the end of the page are
                # initialized to 0xD0 and may have been modified before the program wrote beyond the end of the page.
                # We can use this to get a better idea of where to OOB write started:
                uCorruptionAddress = uBlockAddress + uBlockSize;
                while uCorruptionAddress < uGuardPageAddress:
                  if oCdbWrapper.fuGetValue("by(0x%X)" % uCorruptionAddress) == 0xD0:
                    uCorruptionAddress += 1;
                  else:
                    # We detected a modified byte; there was an OOB write before the one that caused this access
                    # violation. Use it's offset instead and add this fact to the description.
                    uOffsetPastEndOfBlock = uCorruptionAddress - (uBlockAddress + uBlockSize);
                    sBugDescription += (" An earlier out-of-bounds write was detected at 0x%X, %d/0x%X bytes " \
                        "beyond that block because it modified the page heap suffix pattern.") % \
                        (uCorruptionAddress, uOffsetPastEndOfBlock, uOffsetPastEndOfBlock);
                    sMemoryDumpDescription = "Memory near corruption address 0x%X" % uCorruptionAddress;
                    uAddress = uCorruptionAddress; # Used later on to dump memory
                    break;
              elif uAddress == uGuardPageAddress and uAddress > uBlockAddress + uBlockSize:
                sBugDescription += " An earlier out-of-bounds access before this address may have happened without " \
                    "having triggered an access violation.";
            # The access was beyond the end of the block (out-of-bounds, OOB)
            oBugReport.sBugTypeId = "OOB%s[%s]%s" % (sViolationTypeId, fsGetNumberDescription(uBlockSize), \
                fsGetOffsetDescription(uOffsetPastEndOfBlock));
          else:
            # The access was inside the block but apparently the kind of access attempted is not allowed (e.g. write to
            # read-only memory).
            oBugReport.sBugTypeId = "AV%s[%s]@%s" % (sViolationTypeId, fsGetNumberDescription(uBlockSize), \
                fsGetOffsetDescription(uOffsetFromStartOfBlock));
            sOffsetDescription = "%d/0x%X bytes into" % (uOffsetFromStartOfBlock, uOffsetFromStartOfBlock);
            sBugDescription = "Access violation while %s memory at 0x%X; %s a %d/0x%X byte heap block at 0x%X." % \
                (sViolationTypeDescription, uAddress, sOffsetDescription, uBlockSize, uBlockSize, uBlockAddress);
          sSecurityImpact = "Potentially exploitable security issue.";
        else:
          raise NotImplemented("NOT REACHED");
        sBLockHTML = sBlockHTMLTemplate % {
          "sName": "Page heap report for address 0x%X" % uAddress,
          "sContent": "<br/>".join([oCdbWrapper.fsHTMLEncode(s) for s in asPageHeapReport])
        };
        oBugReport.asExceptionSpecificBlocksHTML.append(sBLockHTML);
      else:
        asMemoryProtectionInformation = oCdbWrapper.fasSendCommandAndReadOutput(
          "!vprot 0x%X; $$ Get memory protection information" % uAddress,
          bOutputIsInformative = True,
        );
        if not oCdbWrapper.bCdbRunning: return None;
        # BaseAddress:       00007df5ff5f0000
        # AllocationBase:    00007df5ff5f0000
        # AllocationProtect: 00000001  PAGE_NOACCESS
        # RegionSize:        0000000001d34000
        # State:             00002000  MEM_RESERVE
        # Type:              00040000  MEM_MAPPED
        
        # BaseAddress:       0000000000000000
        # AllocationBase:    0000000000000000
        # RegionSize:        0000000022f60000
        # State:             00010000  MEM_FREE
        # Protect:           00000001  PAGE_NOACCESS
        
        # BaseAddress:       00007ffffffe0000
        # AllocationBase:    00007ffffffe0000
        # AllocationProtect: 00000002  PAGE_READONLY
        # RegionSize:        0000000000010000
        # State:             00002000  MEM_RESERVE
        # Protect:           00000001  PAGE_NOACCESS
        # Type:              00020000  MEM_PRIVATE
        
        # !vprot: extension exception 0x80004002
        #     "QueryVirtual failed"
        assert len(asMemoryProtectionInformation) > 0, \
            "!vprot did not return any results.";
        if re.match(r"^(%s)$" % "|".join([
          "ERROR: !vprot: extension exception 0x80004002\.",
          "!vprot: No containing memory region found",
          "No export vprot found",
        ]), asMemoryProtectionInformation[0]):
          oBugReport.sBugTypeId = "AV%s:Unallocated" % sViolationTypeId;
          sBugDescription = "Access violation while %s unallocated memory at 0x%X." % (sViolationTypeDescription, uAddress);
          sSecurityImpact = "Potentially exploitable security issue, if the attacker can control the address or the memory at the address.";
        else:
          uAllocationStartAddress = None;
          uAllocationProtectionFlags = None;
          uAllocationSize = None;
          uStateFlags = None;
          uProtectionFlags = None;
          uTypeFlags = None;
          for sLine in asMemoryProtectionInformation:
            oLineMatch = re.match(r"^(\w+):\s+([0-9a-f]+)(?:\s+\w+)?$", sLine);
            assert oLineMatch, \
                "Unrecognized memory protection information line: %s\r\n%s" % (sLine, "\r\n".join(asMemoryProtectionInformation));
            sInfoType, sValue = oLineMatch.groups();
            uValue = long(sValue, 16);
            if sInfoType == "BaseAddress":
              pass; # Appear to be the address rounded down to the nearest start of a page, i.e. not useful information.
            elif sInfoType == "AllocationBase":
              uAllocationStartAddress = uValue;
            elif sInfoType == "AllocationProtect":
              uAllocationProtectionFlags = uValue;
            elif sInfoType == "RegionSize":
              uAllocationStartAddress = uValue;
            elif sInfoType == "State":
              uStateFlags = uValue;
            elif sInfoType == "Protect":
              uProtectionFlags = uValue;
            elif sInfoType == "Type":
              uTypeFlags = uValue;
          if uStateFlags == 0x10000:
            oBugReport.sBugTypeId = "AV%s:Unallocated" % sViolationTypeId;
            sBugDescription = "Access violation while %s unallocated memory at 0x%X." % (sViolationTypeDescription, uAddress);
            sSecurityImpact = "Potentially exploitable security issue, if the attacker can control the address or the memory at the address.";
          elif uStateFlags == 0x2000: # MEM_RESERVE
# These checks were added to make sure I understood exactly what was going on. However, it turns out that I don't
# because these checks fail without me being able to understand why. So, I've decided to disable them and see what
# happens. If you have more information that can help me make sense of this and improve it, let me know!
#            assert uTypeFlags in [0x20000, 0x40000], \
#                "Expected MEM_RESERVE memory to have type MEM_PRIVATE or MEM_MAPPED\r\n%s" % "\r\n".join(asMemoryProtectionInformation);
#            # PAGE_READONLY !? Apparently...
#            assert uProtectionFlags == 0x1 or uAllocationProtectionFlags in [0x1, 02], \
#                "Expected MEM_RESERVE memory to have protection PAGE_NOACCESS or PAGE_READONLY\r\n%s" % "\r\n".join(asMemoryProtectionInformation);
            oBugReport.sBugTypeId = "AV%s:Reserved" % sViolationTypeId;
            sBugDescription = "Access violation while %s reserved but unallocated memory at 0x%X." % (sViolationTypeDescription, uAddress);
            sSecurityImpact = "Potentially exploitable security issue, if the address is attacker controlled.";
          elif uStateFlags == 0x1000: # MEM_COMMIT
            dsMemoryProtectionsDescription_by_uFlags = {
              0x01: "inaccessible",  0x02: "read-only",  0x04: "read- and writable",  0x08: "read- and writable",
              0x10: "executable", 0x20: "read- and executable", 0x40: "full-access", 0x80: "full-access"
            };
            sMemoryProtectionsDescription = dsMemoryProtectionsDescription_by_uFlags.get(uAllocationProtectionFlags);
            assert sMemoryProtectionsDescription, \
                "Unexpected MEM_COMMIT memory to have protection value 0x%X\r\n%s" % (uAllocationProtectionFlags, "\r\n".join(asMemoryProtectionInformation));
            oBugReport.sBugTypeId = "AV%s:Arbitrary" % sViolationTypeId;
            sBugDescription = "Access violation while %s %s memory at 0x%X." % (sViolationTypeDescription, sMemoryProtectionsDescription, uAddress);
            sSecurityImpact = "Potentially exploitable security issue, if the address is attacker controlled.";
          else:
            raise AssertionError("Unexpected memory state 0x%X\r\n%s" % (uStateFlags, "\r\n".join(asMemoryProtectionInformation)));
  oBugReport.sBugDescription = sBugDescription + sViolationTypeNotes;
  oBugReport.sSecurityImpact = sSecurityImpact;
  dtxBugTranslations = ddtxBugTranslations.get(oBugReport.sBugTypeId, None);
  if dtxBugTranslations:
    oBugReport = oBugReport.foTranslate(dtxBugTranslations);
  if oBugReport:
    oBugReport.oStack.fHideTopFrames(asHiddenTopFrames);
  if uAddress is not None:
    oBugReport.duRelevantAddress_by_sDescription[sMemoryDumpDescription] = uAddress;
  return oBugReport;
