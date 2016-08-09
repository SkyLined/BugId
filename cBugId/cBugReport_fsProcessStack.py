from dxBugIdConfig import dxBugIdConfig;
import hashlib;

def cBugReport_fsProcessStack(oBugReport, oCdbWrapper):
  # Get a HTML representation of the stack, find the topmost relevatn stack frame and get stack id.
  uFramesHashed = 0;
  if oCdbWrapper.bGetDetailsHTML:
    asStackHTML = [];
  asStackFrameIds = [];
  oTopmostRelevantFrame = None;
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
      if oTopmostRelevantFrame is None:
        oTopmostRelevantFrame = oStackFrame;
      # Make stack frames without a function symbol italic
      if oCdbWrapper.bGetDetailsHTML and not oStackFrame.oFunction:
        sAddressHTML = '<span class="StackNoSymbol">%s</span>' % sAddressHTML;
      # Hash frame address for id and output frame to html
      if uFramesHashed == oBugReport.oStack.uHashFramesCount:
        # no more hashing is needed: just output as is:
        if oCdbWrapper.bGetDetailsHTML:
          asStackHTML.append('<span class="Stack">%s</span><span class="StackSource">%s</span>' % (sAddressHTML, sSourceHTML));
      else:
        asStackFrameIds.append(oStackFrame.sId or "?");
        # frame adds useful information to the id: add hash and output bold
        uFramesHashed += 1;
        if oCdbWrapper.bGetDetailsHTML:
          asStackHTML.append('<span class="StackHash">%s</span> (%s in id)<span class="StackSource">%s</span>' % (sAddressHTML, oStackFrame.sId, sSourceHTML));
  if len(asStackFrameIds) > dxBugIdConfig["uStackHashFramesCount"]:
    # For certain bugs, such as recursive function calls, ids may have been generated for more functions than the value
    # in uStackHashFramesCount. In this case, the last ids are hashes into one id to reduce the number of hashes:
    oHasher = hashlib.md5();
    while len(asStackFrameIds) >= dxBugIdConfig["uStackHashFramesCount"]:
      oHasher.update(asStackFrameIds.pop());
    asStackFrameIds.append(oHasher.hexdigest()[:dxBugIdConfig["uMaxStackFrameHashChars"]]);
  oBugReport.sStackId = ".".join([s for s in asStackFrameIds]);
  # Get the bug location.
  oBugReport.sBugLocation = "(unknown)";
  if oTopmostRelevantFrame:
    if oTopmostRelevantFrame.sSimplifiedAddress:
      oBugReport.sBugLocation = oTopmostRelevantFrame.sSimplifiedAddress;
    if oTopmostRelevantFrame.sSourceFilePath:
      oBugReport.sBugSourceLocation = "%s @ %d" % (oTopmostRelevantFrame.sSourceFilePath, oTopmostRelevantFrame.uSourceFileLineNumber);
  if (
      oBugReport.sProcessBinaryName and (
        not oTopmostRelevantFrame or
        not oTopmostRelevantFrame.oModule or
        oTopmostRelevantFrame.oModule.sBinaryName != oBugReport.sProcessBinaryName
     )
   ):
    # Exception happened in a module, not the process' binary: add process' binary name:
    oBugReport.sBugLocation = oBugReport.sProcessBinaryName + "!" + oBugReport.sBugLocation;
  oBugReport.oStack.oTopmostRelevantFrame = oTopmostRelevantFrame;
  if not oCdbWrapper.bGetDetailsHTML:
    return None;
  # Construct stack HTML
  sStackHTML = "<ol>%s</ol>\r\n" % "".join(["<li>%s</li>" % s for s in asStackHTML]);
  if oBugReport.oStack.bPartialStack:
    sStackHTML += "There were more stack frames, but these were considered irrelevant and subsequently ignored.";
  return sStackHTML;
