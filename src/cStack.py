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
  
  def fCreateAndAddStackFrame(oStack, uNumber, sCdbSource, uAddress, sUnloadedModuleFileName, oModule, uModuleOffset, oFunction, uFunctionOffset):
    # frames must be created in order:
    assert uNumber == len(oStack.aoFrames), \
        "Unexpected frame number %d vs %d" % (uNumber, len(oStack.aoFrames));
    uMaxStackFramesCount = dxBugIdConfig["uMaxStackFramesCount"];
    assert uNumber < uMaxStackFramesCount, \
        "Unexpected frame number %d (max %d)" % (uNumber, uMaxStackFramesCount);
    if uNumber == uMaxStackFramesCount - 1:
      oStack.bPartialStack = True; # We leave the last one out so we can truely say there are more.
    else:
      oStack.aoFrames.append(cStackFrame(uNumber, sCdbSource, uAddress, sUnloadedModuleFileName, oModule, uModuleOffset, oFunction, uFunctionOffset));
    
  @classmethod
  def foCreateFromAddress(cStack, oCdbWrapper, pAddress, uSize):
    # Create the stack object
    oStack = cStack();
    uStackFramesCount = min(dxBugIdConfig["uMaxStackFramesCount"], uSize);
    asStack = oCdbWrapper.fasGetStack("dps 0x%X L0x%X" % (pAddress, uStackFramesCount));
    if not asStack: return None;
    # Here are some lines you might expect to parse:
    # |TODO put something here...
    uFrameNumber = 0;
    for sLine in asStack:
      assert uFrameNumber < uStackFramesCount, \
          "Got more frames than requested";
      oMatch = re.match(r"^\s*%s\s*$" % (
        r"(?:"                                  # either {
          r"[0-9A-F`]+" r"\s+"                  #   stack_address whitespace
          r"[0-9A-F`]+" r"\s+"                  #   ret_address whitespace
        r"|"                                    # } or {
          r"\(Inline(?: Function)?\)" r"\s+"    #   "(Inline" [" Function"] ")" whitespace
          r"\-{8}(?:`\-{8})?" r"\s+"            #   "--------" [`--------] whitespace
        r")"                                    # }
        "(.+)"                                  # Symbol or address
      ), sLine, re.I);
      assert oMatch, "Unknown stack output: %s" % sLine;
      sSymbolOrAddress = oMatch.group(1);
      (
        uAddress,
        sUnloadedModuleFileName, oModule, uModuleOffset,
        oFunction, uFunctionOffset
      ) = oCdbWrapper.ftxSplitSymbolOrAddress(sSymbolOrAddress, doModules_by_sCdbId);
      oStack.fCreateAndAddStackFrame(uFrameNumber, sSymbolOrAddress, uAddress, sUnloadedModuleFileName, oModule, uModuleOffset, oFunction, uFunctionOffset);
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
    asStack = oCdbWrapper.fasGetStack("kn 0x%X" % uStackFramesCount);
    if not asStack: return None;
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
          r"(.+)"                               # Symbol or address
        ), sLine, re.I);
        assert oMatch, "Unknown stack output: %s\r\n%s" % (repr(sLine), "\r\n".join(asStack));
        (sFrameNumber, sSymbolOrAddress) = oMatch.groups();
        assert uFrameNumber == int(sFrameNumber, 16), "Unexpected frame number: %s vs %d" % (sFrameNumber, uFrameNumber);
        (
          uAddress,
          sUnloadedModuleFileName, oModule, uModuleOffset,
          oFunction, uFunctionOffset
        ) = oCdbWrapper.ftxSplitSymbolOrAddress(sSymbolOrAddress, doModules_by_sCdbId);
        oStack.fCreateAndAddStackFrame(uFrameNumber, sSymbolOrAddress, uAddress, sUnloadedModuleFileName, oModule, uModuleOffset, oFunction, uFunctionOffset);
        if not oCdbWrapper.bCdbRunning: return None;
        uFrameNumber += 1;
    return oStack;
