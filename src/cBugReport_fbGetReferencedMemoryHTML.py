from mHTML import fsHTMLEncode;

def cBugReport_fbGetReferencedMemoryHTML(oBugReport, oCdbWrapper):
  # Get data from the memory the last instruction may have been refering.
  asBeforeReferencedMemory = oCdbWrapper.fasSendCommandAndReadOutput("dpp @$ea - 10*$ptrsize L10;");
  if not oCdbWrapper.bCdbRunning: return False;
  if asBeforeReferencedMemory == ["Bad register error at '@$ea - 10*$ptrsize '"]:
    sReferencedMemoryHTML = "";
  else:
    asAtAndAfterReferencedMemory = oCdbWrapper.fasSendCommandAndReadOutput("dpp @$ea L10;");
    if not oCdbWrapper.bCdbRunning: return False;
    sAtReferencedMemory = asAtAndAfterReferencedMemory.pop(0);
    asAfterReferencedMemory = asAtAndAfterReferencedMemory;
    sReferencedMemoryHTML = "<br/>".join(
      [fsHTMLEncode(s) for s in asBeforeReferencedMemory] +
      ["<span class=\"Important\">%s</span>" % fsHTMLEncode(sAtReferencedMemory)] +
      [fsHTMLEncode(s) for s in asAfterReferencedMemory]
    );
    # It may have referenced more than one location:
    asReferencedMemory = oCdbWrapper.fasSendCommandAndReadOutput("dpp @$ea2 - 10*$ptrsize L10;");
    if not oCdbWrapper.bCdbRunning: return False;
    if asReferencedMemory != ["Bad register error at '@$ea2 - 10*$ptrsize '"]:
      asAtAndAfterReferencedMemory = oCdbWrapper.fasSendCommandAndReadOutput("dpp @$ea2 L10;");
      if not oCdbWrapper.bCdbRunning: return False;
      sAtReferencedMemory = asAtAndAfterReferencedMemory.pop(0);
      asAfterReferencedMemory = asAtAndAfterReferencedMemory;
      sReferencedMemoryHTML += "<hr/>" + "<br/>".join(
        [fsHTMLEncode(s) for s in asBeforeReferencedMemory] +
        ["<span class=\"Important\">%s</span>" % fsHTMLEncode(sAtReferencedMemory)] +
        [fsHTMLEncode(s) for s in asAfterReferencedMemory]
      );
  oBugReport.sMemoryHTML = oBugReport.sMemoryHTML + (oBugReport.sMemoryHTML and "<hr/>" or "") + sReferencedMemoryHTML;
  return True;