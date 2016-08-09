import re;
from cModule import cModule;

def cCdbWrapper_fdoGetModulesByCdbIdForCurrentProcess(oCdbWrapper):
  # This information is cached while the process is suspended, when the process is resumed, this information is
  # discarded in cCdbWrapper_fCdbStdInOutThread.
  if oCdbWrapper.doModules_by_sCdbId is None:
    # Gather start and end address and binary name information for loaded modules.
    # See also cCdbWrapper_fasGetCdbIdsForModuleFileNameInCurrentProcess.py
    asModules = oCdbWrapper.fasSendCommandAndReadOutput("lm on; $$ List loaded modules");
    if not oCdbWrapper.bCdbRunning: return None;
    sHeader = asModules.pop(0);
    assert re.sub(r"\s+", " ", sHeader.strip()) in ["start end module name"], \
        "Unknown modules header: %s" % repr(sHeader);
    doModules_by_sCdbId = {};
    for sLine in asModules:
      if re.match(r"^\s*(%s)\s*$" % r"|".join([
        r"",
        r"Unable to enumerate user\-mode unloaded modules, Win32 error 0n\d+"
      ]), sLine):
        continue;
      oMatch = re.match(r"^\s*%s\s*$" % "\s+".join([
        r"([0-9A-f`]+)",         # (start_address)
        r"([0-9A-f`]+)",         # (end_address)
        r"(\w+)",               # (cdb_module_id)
        r"(.*?)",               # (binary_name)
      ]), sLine);
      assert oMatch, "Unexpected modules output: %s" % sLine;
      sStartAddress, sEndAddress, sModuleCdbId, sBinaryName, = oMatch.groups();
      uStartAddress = long(sStartAddress.replace("`", ""), 16);
      uEndAddress = long(sEndAddress.replace("`", ""), 16);
      doModules_by_sCdbId[sModuleCdbId] = cModule(sModuleCdbId, sBinaryName, uStartAddress, uEndAddress);
    oCdbWrapper.doModules_by_sCdbId = doModules_by_sCdbId;
  return oCdbWrapper.doModules_by_sCdbId;

