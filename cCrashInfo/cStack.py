import re;
from cStackFrame import cStackFrame;

from dxCrashInfoConfig import dxCrashInfoConfig;

class cStack(object):
  def __init__(oSelf, oProcess):
    oSelf.oProcess = oProcess;
    oSelf.aoFrames = [];
    oSelf.bPartialStack = False;
  
  def _fAddStackFrame(oSelf, uNumber, uAddress, sCdbModuleId, uModuleOffset, sSymbol, uSymbolOffset):
    # frames must be created in order:
    assert uNumber == len(oSelf.aoFrames), \
        "Unexpected frame number %d vs %d" % (uNumber, len(oSelf.aoFrames));
    uMaxStackFramesCount = dxCrashInfoConfig.get("uMaxStackFramesCount", 50);
    assert uNumber < uMaxStackFramesCount, \
        "Unexpected frame number %d (max %d)" % (uNumber, uMaxStackFramesCount);
    if uNumber == uMaxStackFramesCount - 1:
      oSelf.bPartialStack = True; # We leave the last one out so we can truely say there are more.
    else:
      oModule = sCdbModuleId and oSelf.oProcess.foGetModule(sCdbModuleId);
      oFunction = oModule and sSymbol and oModule.foGetOrCreateFunction(sSymbol);
      oSelf.aoFrames.append(cStackFrame(uNumber, uAddress, oModule, uModuleOffset, oFunction, uSymbolOffset));
  
  @classmethod
  def foCreateFromAddress(cSelf, oCrashInfo, oProcess, pAddress, uSize):
    oSelf = cSelf(oProcess);
    uStackFramesCount = min(dxCrashInfoConfig.get("uMaxStackFramesCount", 50), uSize);
    asStack = oCrashInfo._fasSendCommandAndReadOutput("dps 0x%X L0x%X" % (pAddress, uStackFramesCount));
    if asStack is None: return None;
    # Here are some lines you might expect to parse:
    # |TODO put something here...
    uFrameNumber = 0;
    for sLine in asStack:
      oMatch = re.match(r"^\s*%s\s*$" % (
        r"(?:[0-9A-F`]+|\(Inline\))" r"\s+" # {stack_address || "(Inline)"} whitespace
        r"(?:[0-9A-F`]+|\-{8})"      r"\s+" # {ret_address || "--------"} whitespace
        "(?:"                               # either {
          r"(0x[0-9A-F`]+)"                 #   ("0x" address)
        "|"                                 # } or {
          r"(\w+)"                          #   (cdb_module_id)
          "(?:"                             #   either {
            "(\+0x[0-9A-F`]+)"              #     ("+0x" offset_in_module)
          "|"                               #   } or {
            r"!(.+?)([\+\-]0x[0-9A-F]+)?"   #     "!" (function_name) optional{({"+" || "-"} "0x" offset)}
          ")"                               #   }
        ")"                                 # }
      ), sLine, re.I);
      assert oMatch, "Unknown stack output: %s" % sLine;
      (sAddress, sCdbModuleId, sModuleOffset, sSymbol, sSymbolOffset) = oMatch.groups();
      uAddress = sAddress and int(sAddress.replace("`", ""), 16);
      uModuleOffset = sModuleOffset and int(sModuleOffset.replace("`", ""), 16);
      uSymbolOffset = sSymbolOffset and int(sSymbolOffset.replace("`", ""), 16);
      assert uFrameNumber < uStackFramesCount, \
          "Got more frames than requested";
      oSelf._fAddStackFrame(uFrameNumber, uAddress, sCdbModuleId, uModuleOffset, sSymbol, uSymbolOffset);
      uFrameNumber += 1;
    return oSelf;
  
  @classmethod
  def foCreate(cSelf, oCrashInfo, oProcess):
    oSelf = cSelf(oProcess);
    uStackFramesCount = dxCrashInfoConfig.get("uMaxStackFramesCount", 50);
    asStack = oCrashInfo._fasSendCommandAndReadOutput("kn 0x%X" % uStackFramesCount);
    if asStack is None: return None;
    sHeader = asStack.pop(0);
    assert re.sub(r"\s+", " ", sHeader.strip()) in ["# ChildEBP RetAddr", "# Child-SP RetAddr Call Site"], \
        "Unknown stack header: %s" % repr(sHeader);
    # Here are some lines you might expect to parse:
    # |00 (Inline) -------- chrome_child!WTF::RawPtr<blink::Document>::operator*+0x11
    # |03 0082ec08 603e2568 chrome_child!blink::XMLDocumentParser::startElementNs+0x105
    # |33 0082fb50 0030d4ba chrome!wWinMain+0xaa
    # |23 0a8cc578 66629c9b 0x66cf592a
    # |13 0a8c9cc8 63ea124e IEFRAME!Ordinal231+0xb3c83
    # |36 0a19c854 77548e71 MSHTML+0x8d45e
    # |1b 0000008c`53b2c650 00007ffa`4631cfba ntdll!KiUserCallbackDispatcherContinue
    # |22 00000040`0597b770 00007ffa`36ddc0e3 0x40`90140fc3
    # |WARNING: Frame IP not in any known module. Following frames may be wrong.
    # |WARNING: Stack unwind information not available. Following frames may be wrong.
    # |Could not allocate memory for stack trace
    uFrameNumber = 0;
    for sLine in asStack:
      if not re.match(r"^(?:%s)$" % "|".join([
        r"WARNING: Frame IP not in any known module\. Following frames may be wrong\.",
        r"WARNING: Stack unwind information not available\. Following frames may be wrong\.",
        r"Could not allocate memory for stack trace",
      ]), sLine):
        oMatch = re.match(r"^\s*%s\s*$" % (
          r"([0-9A-F]+)"               r"\s+" # frame_number whitespace
          r"(?:[0-9A-F`]+|\(Inline\))" r"\s+" # {stack_address || "(Inline)"} whitespace
          r"(?:[0-9A-F`]+|\-{8})"      r"\s+" # {ret_address || "--------"} whitespace
          "(?:"                               # either {
            r"(0x[0-9A-F`]+)"                 #   ("0x" address)
          "|"                                 # } or {
            r"(\w+)"                          #   (cdb_module_id)
            "(?:"                             #   either {
              "(\+0x[0-9A-F]+)"               #     ("+0x" offset_in_module)
            "|"                               #   } or {
              r"!(.+?)([\+\-]0x[0-9A-F]+)?"   #     "!" (function_name) optional{(["+" || "-"] "0x" offset)}
            ")"                               #   }
          ")"                                 # }
        ), sLine, re.I);
        assert oMatch, "Unknown stack output: %s" % repr(sLine);
        (sFrameNumber, sAddress, sCdbModuleId, sModuleOffset, sSymbol, sSymbolOffset) = oMatch.groups();
        assert uFrameNumber == int(sFrameNumber, 16), "Unexpected frame number: %s vs %d" % (sFrameNumber, uFrameNumber);
        uAddress = sAddress and int(sAddress.replace("`", ""), 16);
        uModuleOffset = sModuleOffset is not None and int(sModuleOffset.replace("`", ""), 16);
        uSymbolOffset = sSymbolOffset is not None and int(sSymbolOffset.replace("`", ""), 16);
        oSelf._fAddStackFrame(uFrameNumber, uAddress, sCdbModuleId, uModuleOffset, sSymbol, uSymbolOffset);
        uFrameNumber += 1;
    return oSelf;
