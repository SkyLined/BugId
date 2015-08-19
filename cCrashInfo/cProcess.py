import os, re;
from cModule import cModule;

class cProcess(object):
  def __init__(oSelf, uPid, sBinaryName):
    oSelf.uPid = uPid;
    oSelf.sBinaryName = sBinaryName;
    oSelf._doModules_sCdbId = {};
  
  def __str__(oSelf):
    return 'Process(%s #%d)' % (oSelf.sBinaryName, oSelf.uPid);
  
  def foGetModule(oSelf, sCdbModuleId):
    return oSelf._doModules_sCdbId[sCdbModuleId];
  
  @classmethod
  def foCreate(cSelf, oCrashInfo):
    # Gather process id and binary name for the current process.
    asProcesses = oCrashInfo._fasSendCommandAndReadOutput("|.");
    if asProcesses is None: return None;
    #we're only interested in the current process, and output should only include that. However, here's a list of some
    # of the output you might encounter:
    #    0    id: e80 create  name: chrome.exe
    #    1    id: 14bc        child   name: chrome.exe
    # .  2    id: e44 child   name: chrome.exe
    # .  1	id: 28c	child	name: iexplore.exe
    for sLine in asProcesses:
      oMatch = re.match(r"^\s*%s\s*$" % (
        r"\.\s+"                # "." whitespace
        r"\d+"                  # cdb_process_number
        r"\s+id:\s+"            # whitespace "id:" whitespace
        r"([0-9A-F]+)"          # (pid)
        r"\s+\w+\s+name:\s+"    # whitespace {"create" || "child"} whitespace "name:" whitespace
        r"(.*?)"                # (binary_name)
      ), sLine, re.I);
      if oMatch:
        sPid, sBinaryNameOrPath = oMatch.groups();
        break;
    else:
      raise AssertionError("Unexpected processes output: %s" % repr(asLines));
    oSelf = cSelf(int(sPid, 16), os.path.basename(sBinaryNameOrPath));
    # Gather start and end address and binary name information for loaded modules.
    asModules = oCrashInfo._fasSendCommandAndReadOutput("lm on");
    if asModules is None: return None;
    sHeader = asModules.pop(0);
    assert re.sub(r"\s+", " ", sHeader.strip()) in ["start end module name"], \
        "Unknown modules header: %s" % repr(sHeader);
    for sLine in asModules:
      oMatch = re.match(r"^\s*%s\s*$" % "\s+".join([
        r"([0-9A-F`]+)",         # (start_address)
        r"([0-9A-F`]+)",         # (end_address)
        r"(\w+)",               # (cdb_module_id)
        r"(.*?)",               # (binary_name)
      ]), sLine, re.I);
      assert oMatch, "Unexpected modules output: %s" % sLine;
      sStartAddress, sEndAddress, sCdbModuleId, sBinaryName, = oMatch.groups();
      uStartAddress = int(sStartAddress.replace("`", ""), 16);
      uEndAddress = int(sEndAddress.replace("`", ""), 16);
      oSelf._doModules_sCdbId[sCdbModuleId] = cModule(oSelf, sBinaryName, uStartAddress, uEndAddress);
    return oSelf;