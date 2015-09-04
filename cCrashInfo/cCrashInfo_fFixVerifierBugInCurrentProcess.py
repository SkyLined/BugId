import re;

# Fix a bug in verifier.dll. For more details see:
# http://berendjanwever.blogspot.nl/2015/07/work-around-for-page-heap-reallocate-in.html
def cCrashInfo_fFixVerifierBugInCurrentProcess(oCrashInfo):
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
    oCrashInfo._fasSendCommandAndReadOutput("bp %s!AVrfDebugPageHeapFree \"r $t0=poi(@esp+0xC);ed @$t0-14 (dwo(@$t0-18)+0xfff)&0xFFFFF000;g\"" % sVerifierModuleCdbName);
    if not oCrashInfo._bCdbRunning: return;
