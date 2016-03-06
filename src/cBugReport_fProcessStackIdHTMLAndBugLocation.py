from mHTML import fsHTMLEncode;

def cBugReport_fProcessStackIdHTMLAndBugLocation(oBugReport):
  # Find out which frame should be the "main" frame and get stack id.
  oTopmostRelevantFrame = None;          # topmost relevant frame
  oTopmostRelevantFunctionFrame = None;  # topmost relevant frame that has a function symbol
  oTopmostRelevantModuleFrame = None;    # topmost relevant frame that has no function symbol but a module
  uFramesHashed = 0;
  bStackShowsNoSignOfCorruption = True;
  asStackHTML = [];
  asStackFrameIds = [];
  for oStackFrame in oBugReport.oStack.aoFrames:
    if oStackFrame.bIsHidden:
      # This frame is hidden (because it is irrelevant to the crash)
      asStackHTML.append('<span class="StackIgnored">%s</span>' % fsHTMLEncode(oStackFrame.sAddress));
    else:
      # Once a stack frame is encountered with no id, (i.e. no module or function) the stack can no longer be trusted to be correct.
      bStackShowsNoSignOfCorruption = bStackShowsNoSignOfCorruption and (oStackFrame.sId and True or False);
      oTopmostRelevantFrame = oTopmostRelevantFrame or oStackFrame;
      sAddressHTML = fsHTMLEncode(oStackFrame.sAddress);
      # Make stack frames without a function symbol italic
      if not oStackFrame.oFunction:
        sAddressHTML = '<span class="StackNoSymbol">%s</span>' % sAddressHTML;
      # Hash frame address for id and output frame to html
      if not bStackShowsNoSignOfCorruption or uFramesHashed == oBugReport.oStack.uHashFramesCount:
        # no more hashing is needed: just output as is:
        asStackHTML.append('<span class="Stack">%s</span>' % sAddressHTML);
      else:
        asStackFrameIds.append(oStackFrame.sId);
        # frame adds useful information to the id: add hash and output bold
        uFramesHashed += 1;
        asStackHTML.append('<span class="StackHash">%s</span> (%s in id)' % (sAddressHTML, oStackFrame.sId));
        # Determine the top frame for the id:
        if oStackFrame.oFunction:
          oTopmostRelevantFunctionFrame = oTopmostRelevantFunctionFrame or oStackFrame;
        elif oStackFrame.oModule:
          oTopmostRelevantModuleFrame = oTopmostRelevantModuleFrame or oStackFrame;
  oBugReport.sStackId = ".".join([s for s in asStackFrameIds if s]) or "?";
  if oBugReport.oStack.bPartialStack:
    asStackHTML.append("... (the remainder of the stack was ignored)");
  oBugReport.sStackHTML = "<br/>".join(asStackHTML);
  # Get the topmost relevant code frame; prefer one with a function symbol, otherwise one with a module or just the first non-hidden.
  oTopmostRelevantCodeFrame = oTopmostRelevantFunctionFrame or oTopmostRelevantModuleFrame or oTopmostRelevantFrame;
  oBugReport.oTopmostRelevantCodeFrame = oTopmostRelevantCodeFrame;
  # Get the bug location.
  sBugLocation = oTopmostRelevantCodeFrame and oTopmostRelevantCodeFrame.sSimplifiedAddress or "(unknown)";
  if (
      oBugReport.sProcessBinaryName and (
        not oTopmostRelevantCodeFrame or
        not oTopmostRelevantCodeFrame.oModule or
        oTopmostRelevantCodeFrame.oModule.sBinaryName != oBugReport.sProcessBinaryName
     )
   ):
    # Exception happened in a module, not the process' binary: add process' binary name:
    sBugLocation = "%s!%s" % (oBugReport.sProcessBinaryName, sBugLocation);
  oBugReport.sBugLocation = sBugLocation;
