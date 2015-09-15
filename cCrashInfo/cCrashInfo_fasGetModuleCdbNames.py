import re;

def cCrashInfo_fasGetModuleCdbNames(oCrashInfo, sModuleFileName):
  # See also cProcess.py/fdoGetModules_by_sCdbId
  asModuleInformationOutput = oCrashInfo._fasSendCommandAndReadOutput("lm M *%s" % sModuleFileName);
  if not oCrashInfo._bCdbRunning: return [];
  assert len(asModuleInformationOutput) >= 1 and re.match(r"^start\s+end\s+module name\s*$", asModuleInformationOutput[0]), \
      "Unexpected module information output:\r\n%s" % "\r\n".join(asModuleInformationOutput);
  #Sample output:
  # |start    end        module name
  # |00f30000 00f7b000   MicrosoftEdgeCP   (pdb symbols)          c:\symbols\MicrosoftEdgeCP.pdb\26D0017E2A154CA2A692A18BA59225FB1\MicrosoftEdgeCP.pdb
  # |
  # |Unable to enumerate user-mode unloaded modules, Win32 error 0n30
  asModuleCdbNames = [];
  for sLine in asModuleInformationOutput[1:]:
    if re.match("^\s*(%s)\s*$" % "|".join([
      "",
      "Unable to enumerate user\-mode unloaded modules, Win32 error 0n\d+"
    ]), sLine):
      continue;
    # if len == 1, there is no such module and no patch is needed.
    oModuleInformationMatch = re.match(r"^[0-9`a-f]+\s+[0-9`a-f]+\s+(\w+)\s.*$", sLine);
    assert oModuleInformationMatch, \
        "Unexpected module information output:\r\n%s" % "\r\n".join(asModuleInformationOutput);
    asModuleCdbNames.append(oModuleInformationMatch.group(1));
  return asModuleCdbNames;
