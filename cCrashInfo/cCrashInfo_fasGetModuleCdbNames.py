import re;

def cCrashInfo_fasGetModuleCdbNames(oCrashInfo, sModuleFileName):
  asModuleInformationOutput = oCrashInfo._fasSendCommandAndReadOutput("lm M *%s" % sModuleFileName);
  if not oCrashInfo._bCdbRunning: return [];
  assert len(asModuleInformationOutput) >= 1 and re.match(r"^start\s+end\s+module name\s*$", asModuleInformationOutput[0]), \
      "Unexpected module information output:\r\n%s" % "\r\n".join(asModuleInformationOutput);
  asModuleCdbNames = [];
  for sModuleInformation in asModuleInformationOutput[1:]:
    # if len == 1, there is no such module and no patch is needed.
    oModuleInformationMatch = re.match(r"^[0-9`a-f]+\s+[0-9`a-f]+\s+(\w+)\s.*$", sModuleInformation);
    assert oModuleInformationMatch, \
        "Unexpected module information output:\r\n%s" % "\r\n".join(oModuleInformationMatch);
    asModuleCdbNames.append(oModuleInformationMatch.group(1));
  return asModuleCdbNames;
