import re;
from cCrashInfo_fsGetCurrentProcessISA import cCrashInfo_fsGetCurrentProcessISA;

# Fix a bug in verifier.dll. For more details see:
# http://berendjanwever.blogspot.nl/2015/07/work-around-for-page-heap-reallocate-in.html
def cCrashInfo_fFixVerifierBugInCurrentProcess(oCrashInfo):
  sISA = cCrashInfo_fsGetCurrentProcessISA(oCrashInfo);
  if not oCrashInfo._bCdbRunning: return;
  if sISA == "x86":
    asVerifierModuleOutput = oCrashInfo._fasSendCommandAndReadOutput("lm M *verifier.dll");
    if not oCrashInfo._bCdbRunning: return;
    assert len(asVerifierModuleOutput) in (1, 2) and re.match(r"^start\s+end\s+module name\s*$", asVerifierModuleOutput[0]), \
        "Unexpected verifier module header output:\r\n%s" % "\r\n".join(asVerifierModuleOutput);
    if len(asVerifierModuleOutput) == 2:
      # if len == 1, there is no such module and no patch is needed.
      oVerifierModuleCdbNameMatch = re.match(r"^[0-9`a-f]+\s+[0-9`a-f]+\s+(\w+)\s.*$", asVerifierModuleOutput[1]);
      assert oVerifierModuleCdbNameMatch, \
          "Unexpected verifier module output:\r\n%s" % "\r\n".join(asVerifierModuleOutput);
      sVerifierModuleCdbName = oVerifierModuleCdbNameMatch.group(1);
      oCrashInfo._fasSendCommandAndReadOutput("bp %s!AVrfpDphCheckPageHeapBlock \"r;ddp @$csp L8;r $t0=poi(@$csp+0xC);ed @$t0-14 (dwo(@$t0-18)+0xfff)&0xFFFFF000;g\"" % sVerifierModuleCdbName);
      if not oCrashInfo._bCdbRunning: return;
  elif sISA == "AMD64":
    pass; # Not implemented yet.
  else:
    raise AssertionError("Unknown instruction set architecture %s" % sISA);