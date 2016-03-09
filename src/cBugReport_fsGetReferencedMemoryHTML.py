import re;
def cBugReport_fsGetReferencedMemoryHTML(oBugReport, oCdbWrapper):
  # Get data from the memory the last instruction may have been refering.
  asBeforeReferencedMemory = oCdbWrapper.fasSendCommandAndReadOutput("dpp @$ea - 10*$ptrsize L10;");
  if not oCdbWrapper.bCdbRunning: return None;
  if asBeforeReferencedMemory == ["Bad register error at '@$ea - 10*$ptrsize '"]:
    return "";
  asAtAndAfterReferencedMemory = oCdbWrapper.fasSendCommandAndReadOutput("dpp @$ea L10;");
  if not oCdbWrapper.bCdbRunning: return None;
  sAtReferencedMemory = asAtAndAfterReferencedMemory.pop(0);
  asAfterReferencedMemory = asAtAndAfterReferencedMemory;
  uReferencedAddress = long(re.match(r"^\s*([0-9a-fA-F`]+)\s+.+$", sAtReferencedMemory).group(1).replace("`", ""), 16);
  sReferencedMemoryHTML = (
    "<h2 class=\"SubHeader\">Memory around address 0x%X:</h2>" % uReferencedAddress +
    "<br/>".join(
      [oCdbWrapper.fsHTMLEncode(s) for s in asBeforeReferencedMemory] +
      ["<span class=\"Important\">%s</span>" % oCdbWrapper.fsHTMLEncode(sAtReferencedMemory)] +
      [oCdbWrapper.fsHTMLEncode(s) for s in asAfterReferencedMemory]
    )
  );
  # It may have referenced more than one location:
  asReferencedMemory = oCdbWrapper.fasSendCommandAndReadOutput("dpp @$ea2 - 10*$ptrsize L10;");
  if not oCdbWrapper.bCdbRunning: return None;
  if asReferencedMemory != ["Bad register error at '@$ea2 - 10*$ptrsize '"]:
    asAtAndAfterReferencedMemory = oCdbWrapper.fasSendCommandAndReadOutput("dpp @$ea2 L10;");
    if not oCdbWrapper.bCdbRunning: return None;
    sAtReferencedMemory = asAtAndAfterReferencedMemory.pop(0);
    uReferencedAddress = long(re.match(r"^\s*([0-9a-fA-F`]+)\s+.+$", sAtReferencedMemory).group(1), 16);
    asAfterReferencedMemory = asAtAndAfterReferencedMemory;
    sReferencedMemoryHTML += (
      "<br/><br/>" + 
      "<h2 class=\"SubHeader\">Memory around address 0x%X:</h2>" % uReferencedAddress +
      "<br/>".join(
        [oCdbWrapper.fsHTMLEncode(s) for s in asBeforeReferencedMemory] +
        ["<span class=\"Important\">%s</span>" % oCdbWrapper.fsHTMLEncode(sAtReferencedMemory)] +
        [oCdbWrapper.fsHTMLEncode(s) for s in asAfterReferencedMemory]
      )
    );
  return sReferencedMemoryHTML;