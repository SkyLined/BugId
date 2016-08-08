import re;
from dxBugIdConfig import dxBugIdConfig;

def cBugReport_fsGetRelevantMemoryHTML(oBugReport, oCdbWrapper, uAddress):
  uPointerSize = oCdbWrapper.fuGetValue("@$ptrsize");
  if not oCdbWrapper.bCdbRunning: return None;
  uAlignedAddress = uAddress - (uAddress % uPointerSize);
  # Get data from the memory the last instruction may have been refering.
  asBeforeReferencedMemory = oCdbWrapper.fasSendCommandAndReadOutput("dpp 0x%X L0x%X;" % \
      (uAlignedAddress - uPointerSize * dxBugIdConfig["uRelevantMemoryPointersBefore"], dxBugIdConfig["uRelevantMemoryPointersBefore"]));
  if not oCdbWrapper.bCdbRunning: return None;
  asAtAndAfterReferencedMemory = oCdbWrapper.fasSendCommandAndReadOutput("dpp 0x%X L0x%X;" % \
      (uAlignedAddress, dxBugIdConfig["uRelevantMemoryPointersAfter"] + 1));
  if not oCdbWrapper.bCdbRunning: return None;
  sAtReferencedMemory = asAtAndAfterReferencedMemory.pop(0);
  asAfterReferencedMemory = asAtAndAfterReferencedMemory;
  if uAlignedAddress == uAddress:
    sNote = "right here";
  else:
    sNote = "at offset 0x%X" % (uAddress - uAlignedAddress);
  return (
    "<br/>".join(
      ['<span class="Memory">%s</span>' % oCdbWrapper.fsHTMLEncode(re.sub(r"(\?{8}`)?\?{8}\s*$", "<inaccessible>", s)) for s in asBeforeReferencedMemory] +
      ['<span class="Memory Important">%s &#8656; %s</span>' % (oCdbWrapper.fsHTMLEncode(sAtReferencedMemory.ljust(80)), sNote)] +
      ['<span class="Memory">%s</span>' % oCdbWrapper.fsHTMLEncode(re.sub(r"(\?{8}`)?\?{8}\s*$", "<inaccessible>", s)) for s in asAfterReferencedMemory]
    )
  );
