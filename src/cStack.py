import re;
from cStackFrame import cStackFrame;
from dxBugIdConfig import dxBugIdConfig;

class cStack(object):
  def __init__(oStack):
    oStack.aoFrames = [];
    oStack.bPartialStack = False;
    oStack.uHashFramesCount = dxBugIdConfig["uStackHashFramesCount"];
  
  def fHideTopFrames(oStack, asFrameAddresses):
    for oStackFrame in oStack.aoFrames: # For each frame
      if not oStackFrame.bIsHidden: # if it's not yet hidden,
        if not oStackFrame.fbHide(asFrameAddresses): # see if it should be hidden and do so
          break; # or stop looking.
  
  def fCreateAndAddStackFrame(oStack, oCdbWrapper, doModules_by_sCdbId, uNumber, uAddress, sUnloadedModuleFileName, sModuleCdbId, uModuleOffset, sSymbol, uSymbolOffset):
    # frames must be created in order:
    assert uNumber == len(oStack.aoFrames), \
        "Unexpected frame number %d vs %d" % (uNumber, len(oStack.aoFrames));
    uMaxStackFramesCount = dxBugIdConfig["uMaxStackFramesCount"];
    assert uNumber < uMaxStackFramesCount, \
        "Unexpected frame number %d (max %d)" % (uNumber, uMaxStackFramesCount);
    if uNumber == uMaxStackFramesCount - 1:
      oStack.bPartialStack = True; # We leave the last one out so we can truely say there are more.
    else:
      if sModuleCdbId == "SharedUserData":
        # "ShareUserData" is a symbol outside of any module that gets used as a module name in cdb.
        # Any value referencing it must be converted to an address:
        sBaseSymbol = "SharedUserData";
        if sSymbol: sBaseSymbol += "!%s" % sSymbol;
        uAddress = oCdbWrapper.fuEvaluateExpression(sBaseSymbol);
        if uModuleOffset: uAddress += uModuleOffset;
        if uSymbolOffset: uAddress += uSymbolOffset;
        # Clean up:
        sModuleCdbId = None;
        uModuleOffset = None;
        sSymbol = None;
        uSymbolOffset = None;
      oModule = sModuleCdbId and doModules_by_sCdbId[sModuleCdbId];
      if not oCdbWrapper.bCdbRunning: return None;
      oFunction = oModule and sSymbol and oModule.foGetOrCreateFunction(sSymbol);
      oStack.aoFrames.append(cStackFrame(uNumber, uAddress, sUnloadedModuleFileName, oModule, uModuleOffset, oFunction, uSymbolOffset));
    
  @classmethod
  def foCreateFromAddress(cStack, oCdbWrapper, pAddress, uSize):
    # Get information on all modules in the current process
    doModules_by_sCdbId = oCdbWrapper.fdoGetModulesByCdbIdForCurrentProcess();
    if not oCdbWrapper.bCdbRunning: return None;
    # Create the stack object
    oStack = cStack();
    uStackFramesCount = min(dxBugIdConfig["uMaxStackFramesCount"], uSize);
    if dxBugIdConfig["bEnhancedSymbolLoading"]:
      # Turn noisy symbol loading off as it mixes with the stack output and makes it unparsable
      asOutput = oCdbWrapper.fasSendCommandAndReadOutput(".symopt- 0x80000000");
      if not oCdbWrapper.bCdbRunning: return None;
    asStack = oCdbWrapper.fasSendCommandAndReadOutput("dps 0x%X L0x%X" % (pAddress, uStackFramesCount));
    if not oCdbWrapper.bCdbRunning: return None;
    if dxBugIdConfig["bEnhancedSymbolLoading"]:
      # Turn noisy symbol loading back on
      oCdbWrapper.fasSendCommandAndReadOutput(".symopt+ 0x80000000");
      if not oCdbWrapper.bCdbRunning: return None;
    # Here are some lines you might expect to parse:
    # |TODO put something here...
    uFrameNumber = 0;
    for sLine in asStack:
      oMatch = re.match(r"^\s*%s\s*$" % (
        r"(?:"                                  # either {
          r"[0-9A-F`]+" r"\s+"                  #   stack_address whitespace
          r"[0-9A-F`]+" r"\s+"                  #   ret_address whitespace
        r"|"                                    # } or {
          r"\(Inline(?: Function)?\)" r"\s+"    #   "(Inline" [" Function"] ")" whitespace
          r"\-{8}(?:`\-{8})?" r"\s+"            #   "--------" [`--------] whitespace
        r")"                                    # }
        "(?:"                                   # either {
          r"(0x[0-9A-F`]+)"                     #   ("0x" address)
        "|"                                     # } or {
          r"<Unloaded_(.*)>"                    #   "<Unloaded_" module_file_name ">"
        "|"                                     # } or {
          r"(\w+)"                              #   (cdb_module_id)
          "(?:"                                 #   either {
            "(\+0x[0-9A-F`]+)"                  #     ("+0x" offset_in_module)
          "|"                                   #   } or {
            r"!(.+?)([\+\-]0x[0-9A-F]+)?"       #     "!" (function_name) optional{({"+" || "-"} "0x" offset)}
          ")"                                   #   }
        ")"                                     # }
      ), sLine, re.I);
      assert oMatch, "Unknown stack output: %s" % sLine;
      (sAddress, sUnloadedModuleFileName, sModuleCdbId, sModuleOffset, sSymbol, sSymbolOffset) = oMatch.groups();
      uAddress = sAddress and int(sAddress.replace("`", ""), 16);
      uModuleOffset = sModuleOffset and int(sModuleOffset.replace("`", ""), 16);
      uSymbolOffset = sSymbolOffset and int(sSymbolOffset.replace("`", ""), 16);
      assert uFrameNumber < uStackFramesCount, \
          "Got more frames than requested";
      oStack.fCreateAndAddStackFrame(oCdbWrapper, doModules_by_sCdbId, uFrameNumber, uAddress, \
          sUnloadedModuleFileName, sModuleCdbId, uModuleOffset, sSymbol, uSymbolOffset);
      if not oCdbWrapper.bCdbRunning: return None;
      uFrameNumber += 1;
    return oStack;
  
  @classmethod
  def foCreate(cStack, oCdbWrapper):
    # Get information on all modules in the current process
    doModules_by_sCdbId = oCdbWrapper.fdoGetModulesByCdbIdForCurrentProcess();
    if not oCdbWrapper.bCdbRunning: return None;
    # Create the stack object
    oStack = cStack();
    uStackFramesCount = dxBugIdConfig["uMaxStackFramesCount"];
    if dxBugIdConfig["bEnhancedSymbolLoading"]:
      # Turn noisy symbol loading off as it mixes with the stack output and makes it unparsable
      asOutput = oCdbWrapper.fasSendCommandAndReadOutput(".symopt- 0x80000000");
      if not oCdbWrapper.bCdbRunning: return None;
    asStack = oCdbWrapper.fasSendCommandAndReadOutput("kn 0x%X" % uStackFramesCount);
    if not oCdbWrapper.bCdbRunning: return None;
    if dxBugIdConfig["bEnhancedSymbolLoading"]:
      # Turn noisy symbol loading back on
      oCdbWrapper.fasSendCommandAndReadOutput(".symopt+ 0x80000000");
      if not oCdbWrapper.bCdbRunning: return None;
    sHeader = asStack.pop(0);
    assert re.sub(r"\s+", " ", sHeader.strip()) in ["# ChildEBP RetAddr", "# Child-SP RetAddr Call Site", "Could not allocate memory for stack trace"], \
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
        r"\*\*\* ERROR: Module load completed but symbols could not be loaded for .*",
        r"\*\*\* WARNING: Unable to verify checksum for .*",
      ]), sLine):
        oMatch = re.match(r"^\s*%s\s*$" % (
          r"([0-9A-F]+)" r"\s+"                 # (frame_number) whitespace
          r"(?:"                                # either {
            r"[0-9A-F`]+" r"\s+"                #   stack_address whitespace
            r"[0-9A-F`]+" r"\s+"                #   ret_address whitespace
          r"|"                                  # } or {
            r"\(Inline(?: Function)?\)" r"\s+"  #   "(Inline" [" Function"] ")" whitespace
            r"\-{8}(?:`\-{8})?" r"\s+"          #   "--------" [`--------] whitespace
          r")"                                  # }
          r"(?:"                                # either {
            r"(0x[0-9A-F`]+)"                   #   ("0x" address)
          r"|"                                  # } or {
            r"<Unloaded_(.*)>"                  #   "<Unloaded_" module_file_name ">"
            r"(\+0x[0-9A-F]+)?"                 #   optional{ ("+0x" offset_in_unloaded_module) }
          "|"                                   # } or {
            r"(\w+)"                            #   (cdb_module_id)
            r"(?:"                              #   either {
              r"(\+0x[0-9A-F]+)"                #     ("+0x" offset_in_module)
            r"|"                                #   } or {
              r"!(.+?)([\+\-]0x[0-9A-F]+)?"     #     "!" (function_name) optional{ (["+" || "-"] "0x" offset) }
            r")"                                #   }
          r")"                                  # }
        ), sLine, re.I);
        assert oMatch, "Unknown stack output: %s\r\n%s" % (repr(sLine), "\r\n".join(asStack));
        (
          sFrameNumber,
          sAddress,
          sUnloadedModuleFileName,
            sUnloadedModuleOffset,
          sModuleCdbId,
            sModuleOffset,
            sSymbol, sSymbolOffset
        ) = oMatch.groups();
        assert uFrameNumber == int(sFrameNumber, 16), "Unexpected frame number: %s vs %d" % (sFrameNumber, uFrameNumber);
        uAddress = sAddress and long(sAddress.replace("`", ""), 16);
        uModuleOffset = (
          sUnloadedModuleOffset is not None and long(sUnloadedModuleOffset.replace("`", ""), 16) or
          sModuleOffset is not None and long(sModuleOffset.replace("`", ""), 16)
        );
        uSymbolOffset = sSymbolOffset is not None and long(sSymbolOffset.replace("`", ""), 16);
        oStack.fCreateAndAddStackFrame(oCdbWrapper, doModules_by_sCdbId, uFrameNumber, uAddress, \
            sUnloadedModuleFileName, sModuleCdbId, uModuleOffset, sSymbol, uSymbolOffset);
        if not oCdbWrapper.bCdbRunning: return None;
        uFrameNumber += 1;
    return oStack;
