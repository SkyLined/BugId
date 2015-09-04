import re;

def cCrashInfo_fsGetModuleISA(oCrashInfo, sCdbModuleId):
  # returns "x86" or "AMD64"
  asModuleOutput = oCrashInfo._fasSendCommandAndReadOutput("lm m %s" % sCdbModuleId);
  if not oCrashInfo._bCdbRunning: return;
  oModuleDetailsMatch = (
    len(asModuleOutput) == 2
    and re.match(r"^start\s+end\s+module name\s*$", asModuleOutput[0])
    and re.match(r"^([0-9`a-f]+)\s+[0-9`a-f]+\s+\w+\s.*$", asModuleOutput[1])
  );
  assert oModuleDetailsMatch, "Unexpected module output:\r\n%s" % "\r\n".join(asModuleOutput);
  sBaseAddressHex = oModuleDetailsMatch.group(1);
  uBaseAddress = long(sBaseAddressHex.replace("`", ""), 16);
  print "* base: 0x%08X" % uBaseAddress;
  uPEHeaderAddress = uBaseAddress + oCrashInfo.fuEvaluateExpression("dwo(0x%X)" % (uBaseAddress + 0x3C));
  print "* pe  : 0x%08X" % uPEHeaderAddress;
  if not oCrashInfo._bCdbRunning: return;
  uMachineType = oCrashInfo.fuEvaluateExpression("wo(0x%X)" % (uPEHeaderAddress + 0x4));
  print "* type: 0x%04X" % uMachineType;
  if not oCrashInfo._bCdbRunning: return;
  if not oCrashInfo._bCdbRunning: return;
  sISA = {0x8664: "AMD64", 0x14c: "x86"}.get(uMachineType);
  assert sISA, "Unknown verifier.dll machine type 0x%X" % uMachineType;
  return sISA;
