import re;
from cStackFrame import cStackFrame;
from dxCrashInfoConfig import dxCrashInfoConfig;

class cStack(object):
  def __init__(oStack, oProcess):
    oStack.oProcess = oProcess;
    oStack.aoFrames = [];
    oStack.bPartialStack = False;
    oStack.uHashFramesCount = dxCrashInfoConfig["uStackHashFramesCount"];
  
  def fHideTopFrames(oStack, asFrameAddresses):
    for oFrame in oStack.aoFrames: # For each frame
      if not oFrame.bIsHidden: # if it's not yet hidden,
        if oFrame.sAddress in asFrameAddresses or oFrame.sSimplifiedAddress in asFrameAddresses: # and it should be,
          oFrame.bIsHidden = True; # hide it.
        else:
          break; # this should not be hidden, stop looking.
  
  def fCreateAndAddStackFrame(oStack, oCrashInfo, uNumber, uAddress, sCdbModuleId, uModuleOffset, sSymbol, uSymbolOffset):
    # frames must be created in order:
    assert uNumber == len(oStack.aoFrames), \
        "Unexpected frame number %d vs %d" % (uNumber, len(oStack.aoFrames));
    uMaxStackFramesCount = dxCrashInfoConfig["uMaxStackFramesCount"];
    assert uNumber < uMaxStackFramesCount, \
        "Unexpected frame number %d (max %d)" % (uNumber, uMaxStackFramesCount);
    if uNumber == uMaxStackFramesCount - 1:
      oStack.bPartialStack = True; # We leave the last one out so we can truely say there are more.
    else:
      if sCdbModuleId == "SharedUserData":
        # "ShareUserData" is a symbol outside of any module that gets used as a module name in cdb.
        # Any value referencing it must be converted to an address:
        sBaseSymbol = "SharedUserData";
        if sSymbol: sBaseSymbol += "!%s" % sSymbol;
        uAddress = oCrashInfo.fuEvaluateExpression(sBaseSymbol);
        if uModuleOffset: uAddress += uModuleOffset;
        if uSymbolOffset: uAddress += uSymbolOffset;
        # Clean up:
        sCdbModuleId = None;
        uModuleOffset = None;
        sSymbol = None;
        uSymbolOffset = None;
      oModule = sCdbModuleId and oStack.oProcess.foGetModule(sCdbModuleId);
      oFunction = oModule and sSymbol and oModule.foGetOrCreateFunction(sSymbol);
      oStack.aoFrames.append(cStackFrame(uNumber, uAddress, oModule, uModuleOffset, oFunction, uSymbolOffset));
    
  @classmethod
  def foCreateFromAddress(cStack, oCrashInfo, oProcess, pAddress, uSize):
    oStack = cStack(oProcess);
    uStackFramesCount = min(dxCrashInfoConfig["uMaxStackFramesCount"], uSize);
    asStack = oCrashInfo._fasSendCommandAndReadOutput("dps 0x%X L0x%X" % (pAddress, uStackFramesCount));
    if not oCrashInfo._bCdbRunning: return None;
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
      oStack.fCreateAndAddStackFrame(oCrashInfo, uFrameNumber, uAddress, sCdbModuleId, uModuleOffset, sSymbol, uSymbolOffset);
      if not oCrashInfo._bCdbRunning: return None;
      uFrameNumber += 1;
    return oStack;
  
  @classmethod
  def foCreate(cStack, oCrashInfo, oProcess):
    oStack = cStack(oProcess);
    uStackFramesCount = dxCrashInfoConfig["uMaxStackFramesCount"];
    asStack = oCrashInfo._fasSendCommandAndReadOutput("kn 0x%X" % uStackFramesCount);
    if not oCrashInfo._bCdbRunning: return None;
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
        oStack.fCreateAndAddStackFrame(oCrashInfo, uFrameNumber, uAddress, sCdbModuleId, uModuleOffset, sSymbol, uSymbolOffset);
        if not oCrashInfo._bCdbRunning: return None;
        uFrameNumber += 1;
    return oStack;
