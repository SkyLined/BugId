def cBugReport_fsProcessStack(oBugReport, oCdbWrapper):
  # Find out which frame should be the "main" frame and get stack id.
  oTopmostRelevantFrame = None;          # topmost relevant frame
  oTopmostRelevantFunctionFrame = None;  # topmost relevant frame that has a function symbol
  oTopmostRelevantModuleFrame = None;    # topmost relevant frame that has no function symbol but a module
  uFramesHashed = 0;
  bStackShowsNoSignOfCorruption = True;
  if oCdbWrapper.bGetDetailsHTML:
    asStackHTML = [];
  asStackFrameIds = [];
  for oStackFrame in oBugReport.oStack.aoFrames:
    if oCdbWrapper.bGetDetailsHTML:
      sAddressHTML = oCdbWrapper.fsHTMLEncode(oStackFrame.sAddress);
      sSourceHTML = "";
      if oStackFrame.sSourceFilePath:
        sSourceFilePathAndLineNumber = "%s @ %d" % (oStackFrame.sSourceFilePath, oStackFrame.uSourceFileLineNumber);
        sSourceHTML = " [%s]" % oCdbWrapper.fsHTMLEncode(sSourceFilePathAndLineNumber);
    if oStackFrame.bIsHidden:
      # This frame is hidden (because it is irrelevant to the crash)
      if oCdbWrapper.bGetDetailsHTML:
        asStackHTML.append('<span class="StackIgnored">%s</span><span class="StackSource">%s</span>' % (sAddressHTML, sSourceHTML));
    else:
      # Once a stack frame is encountered with no id, (i.e. no module or function) the stack can no longer be trusted to be correct.
      bStackShowsNoSignOfCorruption = bStackShowsNoSignOfCorruption and (oStackFrame.sId and True or False);
      oTopmostRelevantFrame = oTopmostRelevantFrame or oStackFrame;
      # Make stack frames without a function symbol italic
      if oCdbWrapper.bGetDetailsHTML and not oStackFrame.oFunction:
        sAddressHTML = '<span class="StackNoSymbol">%s</span>' % sAddressHTML;
      # Hash frame address for id and output frame to html
      if not bStackShowsNoSignOfCorruption or uFramesHashed == oBugReport.oStack.uHashFramesCount:
        # no more hashing is needed: just output as is:
        if oCdbWrapper.bGetDetailsHTML:
          asStackHTML.append('<span class="Stack">%s</span><span class="StackSource">%s</span>' % (sAddressHTML, sSourceHTML));
      else:
        asStackFrameIds.append(oStackFrame.sId);
        # frame adds useful information to the id: add hash and output bold
        uFramesHashed += 1;
        if oCdbWrapper.bGetDetailsHTML:
          asStackHTML.append('<span class="StackHash">%s</span> (%s in id)<span class="StackSource">%s</span>' % (sAddressHTML, oStackFrame.sId, sSourceHTML));
        # Determine the top frame for the id:
        if oStackFrame.oFunction:
          oTopmostRelevantFunctionFrame = oTopmostRelevantFunctionFrame or oStackFrame;
        elif oStackFrame.oModule:
          oTopmostRelevantModuleFrame = oTopmostRelevantModuleFrame or oStackFrame;
  oBugReport.sStackId = ".".join([s for s in asStackFrameIds if s]) or "?";
  if oCdbWrapper.bGetDetailsHTML and oBugReport.oStack.bPartialStack:
    asStackHTML.append("... (the remainder of the stack was ignored)");
  # Get the topmost relevant code frame; prefer one with a function symbol, otherwise one with a module or just the first non-hidden.
  oTopmostRelevantCodeFrame = oTopmostRelevantFunctionFrame or oTopmostRelevantModuleFrame or oTopmostRelevantFrame;
  oBugReport.oTopmostRelevantCodeFrame = oTopmostRelevantCodeFrame;
  # Get the bug location.
  oBugReport.sBugLocation = "(unknown)";
  if oTopmostRelevantCodeFrame:
    if oTopmostRelevantCodeFrame.sSimplifiedAddress:
      oBugReport.sBugLocation = oTopmostRelevantCodeFrame.sSimplifiedAddress;
    if oTopmostRelevantCodeFrame.sSourceFilePath:
      oBugReport.sBugSourceLocation = "%s @ %d" % (oTopmostRelevantCodeFrame.sSourceFilePath, oTopmostRelevantCodeFrame.uSourceFileLineNumber);
  if (
      oBugReport.sProcessBinaryName and (
        not oTopmostRelevantCodeFrame or
        not oTopmostRelevantCodeFrame.oModule or
        oTopmostRelevantCodeFrame.oModule.sBinaryName != oBugReport.sProcessBinaryName
     )
   ):
    # Exception happened in a module, not the process' binary: add process' binary name:
    oBugReport.sBugLocation = oBugReport.sProcessBinaryName + "!" + oBugReport.sBugLocation;
  return oCdbWrapper.bGetDetailsHTML and "<ul>%s</ul>" % "".join(["<li>%s</li>" % s for s in asStackHTML]) or None;