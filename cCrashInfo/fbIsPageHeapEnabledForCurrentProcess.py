import re;

uRequiredFlags = sum([
  0x02000000, #hpa: Put heap allocations at the end of pages.
])

def fbIsPageHeapEnabledForCurrentProcess(oCrashInfo):
  asOutput = oCrashInfo._fasSendCommandAndReadOutput("!gflag");
  if asOutput is None: return None;
  oFlagsMatch = len(asOutput) > 0 and re.match(r"^Current NtGlobalFlag contents: 0x([0-9A-F]+)\s*$", asOutput[0], re.I);
  assert oFlagsMatch, "Unknown !gflag output:\r\n%s" % "\r\n".join(asOutput);
  uFlags = int(oFlagsMatch.group(1), 16);
  return uFlags & uRequiredFlags == uRequiredFlags;