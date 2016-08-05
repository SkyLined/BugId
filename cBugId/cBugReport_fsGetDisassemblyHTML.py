import re;
from dxBugIdConfig import dxBugIdConfig;

def fsHTMLEncodeAndColorDisassemblyLine(oCdbWrapper, sLine):
  # If this line starts with an address and opcode, make those semi-transparent.
  oMatch = re.match(r"^([0-9a-fA-F`]+\s+)([0-9a-fA-F]+\s+)(.+)$", sLine);
  if oMatch:
    return '<span class="DisassemblyAddress">%s</span><span class="DisassemblyOpcode">%s</span><span class="DisassemblyInstruction">%s</span>' % \
        tuple([oCdbWrapper.fsHTMLEncode(s) for s in oMatch.groups()]);
  return '<span class="DisassemblyInformation">%s</span>' % oCdbWrapper.fsHTMLEncode(sLine);
  
def cBugReport_fsGetDisassemblyHTML(oBugReport, oCdbWrapper, sAddress, sAddressDescription, sBeforeAddressDescription = None):
  # See dxBugIdConfig for a description of these "magic" values.
  uDisassemblyBytesBefore = dxBugIdConfig["uDisassemblyInstructionsBefore"] * dxBugIdConfig["uDisassemblyAverageInstructionSize"] + \
      dxBugIdConfig["uDisassemblyAlignmentBytes"];
  uDisassemblyBytesAfter = dxBugIdConfig["uDisassemblyInstructionsAfter"] * dxBugIdConfig["uDisassemblyAverageInstructionSize"];
  # Get disassembly around code in which exception happened. This may not be possible if the instruction pointer points to unmapped memory.
  asDisassemblyHTML = [];
  if uDisassemblyBytesBefore > 0:
    # Get disassembly before address
    asBeforeDisassembly = oCdbWrapper.fasSendCommandAndReadOutput(".if ($vvalid(%s - %d, %d)) { u %s - %d %s - 1; };" % \
        (sAddress, uDisassemblyBytesBefore, uDisassemblyBytesBefore, sAddress, uDisassemblyBytesBefore, sAddress));
    if not oCdbWrapper.bCdbRunning: return None;
    # Limit number of instructions
    asBeforeDisassembly = asBeforeDisassembly[-dxBugIdConfig["uDisassemblyInstructionsBefore"]:];
    if asBeforeDisassembly:
      # Optionally highlight and describe instruction before the address:
      if sBeforeAddressDescription:
        sBeforeAddressDisassembly = asBeforeDisassembly.pop(-1);
      asDisassemblyHTML += [fsHTMLEncodeAndColorDisassemblyLine(oCdbWrapper, s) for s in asBeforeDisassembly];
      if sBeforeAddressDescription:
        asDisassemblyHTML.append(
          "<span class=\"Important\">%s &#8656; %s</span>" % \
              (fsHTMLEncodeAndColorDisassemblyLine(oCdbWrapper, sBeforeAddressDisassembly.ljust(80)), sBeforeAddressDescription)
        );
  if uDisassemblyBytesAfter > 0:
    asAtAndAfterDisassembly = oCdbWrapper.fasSendCommandAndReadOutput(".if ($vvalid(%s, %d)) { u %s %s + %d; };" % \
        (sAddress, uDisassemblyBytesAfter, sAddress, sAddress, uDisassemblyBytesAfter - 1));
    if not oCdbWrapper.bCdbRunning: return None;
    # Limit number of instructions
    asAtAndAfterDisassembly = asAtAndAfterDisassembly[-dxBugIdConfig["uDisassemblyInstructionsAfter"]:];
    if asAtAndAfterDisassembly:
      # Optionally highlight and describe instruction at the address:
      if sAddressDescription:
        sAtAddressDisassembly = asAtAndAfterDisassembly.pop(0);
        asDisassemblyHTML.append(
          "<span class=\"Important\">%s &#8656; %s</span>" % \
              (fsHTMLEncodeAndColorDisassemblyLine(oCdbWrapper, sAtAddressDisassembly.ljust(80)), sAddressDescription)
        );
      asDisassemblyHTML += [fsHTMLEncodeAndColorDisassemblyLine(oCdbWrapper, s) for s in asAtAndAfterDisassembly];
  if asDisassemblyHTML:
    return "<br/>".join(asDisassemblyHTML);
  return None;
