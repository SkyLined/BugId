import os, re;
from cModule import cModule;

class cProcess(object):
  def __init__(oSelf, uProcessId, sBinaryName, sISA):
    oSelf.uProcessId = uProcessId;
    oSelf.sBinaryName = sBinaryName;
    oSelf.sISA = sISA;
    oSelf._doModules_sCdbId = {};
  
  def __str__(oSelf):
    return 'Process(%s #%d %s)' % (oSelf.sBinaryName, oSelf.uProcessId, oSelf.sISA);
  
  def foGetModule(oSelf, sCdbModuleId):
    return oSelf._doModules_sCdbId[sCdbModuleId];
  
  @classmethod
  def ftxGetCurrentProcessIdAndBinaryName(cSelf, oCrashInfo):
    # Gather process id and binary name for the current process.
    asProcessesOutput = oCrashInfo._fasSendCommandAndReadOutput("|.");
    if not oCrashInfo._bCdbRunning: return None, None;
    #Output:
    # |.  2 id:  e44 child   name: chrome.exe
    # |.  1 id:  28c child   name: iexplore.exe
    # |.  4 id:  c74 exited  name: chrome.exe
    oMatch = len(asProcessesOutput) == 1 and re.match(r"^\s*%s\s*$" % (
      r"\.\s+"                # "." whitespace
      r"\d+"                  # cdb_process_number
      r"\s+id:\s+"            # whitespace "id:" whitespace
      r"([0-9A-F]+)"          # (pid)
      r"\s+\w+\s+name:\s+"    # whitespace {"create" || "child"} whitespace "name:" whitespace
      r"(.*?)"                # (binary_name)
    ), asProcessesOutput[0], re.I);
    assert oMatch, "Unexpected current process output:\r\n%s" % "\r\n".join(asProcessesOutput);
    sProcessId, sBinaryNameOrPath = oMatch.groups();
    uProcessId = int(sProcessId, 16);
    sBinaryName = os.path.basename(sBinaryNameOrPath);
    return (uProcessId, sBinaryName);
  
  @classmethod
  def foCreate(cSelf, oCrashInfo):
    (uProcessId, sBinaryName) = cSelf.ftxGetCurrentProcessIdAndBinaryName(oCrashInfo);
    # Gather instruction set architecture for current process.
    asEffmach = oCrashInfo._fasSendCommandAndReadOutput(".effmach");
    if not oCrashInfo._bCdbRunning: return None;
    oEffmachMatch = len(asEffmach) == 1 and re.match(r"^Effective machine: (x\d{2}) .*$", asEffmach[0]);
    assert oEffmachMatch, "Unexpected .effmach output: %s" % repr(asEffmach);
    sISA = oEffmachMatch.group(1);
    # Create a cProcess instance
    oSelf = cSelf(uProcessId, sBinaryName, sISA);
    # Gather start and end address and binary name information for loaded modules.
    asModules = oCrashInfo._fasSendCommandAndReadOutput("lm on");
    if not oCrashInfo._bCdbRunning: return None;
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