import re;

def cCrashInfo_fsGetCurrentProcessISA(oCrashInfo):
  # return s "x86" or "AMD64"
  asEffmach = oCrashInfo._fasSendCommandAndReadOutput(".effmach");
  if not oCrashInfo._bCdbRunning: return None;
  oEffmachMatch = len(asEffmach) == 1 and re.match(r"^Effective machine: .* \((x86|AMD64)\)\s*$", asEffmach[0]);
  assert oEffmachMatch, "Unexpected .effmach output: %s" % repr(asEffmach);
  return oEffmachMatch.group(1);
