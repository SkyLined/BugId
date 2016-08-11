import re;
from dxBugIdConfig import dxBugIdConfig;

def fsHTMLEncodeAndColorDisassemblyLine(oCdbWrapper, sLine):
  # If this line starts with an address and opcode, make those semi-transparent.
  oMatch = re.match(r"^([0-9a-fA-F`]+\s+)([0-9a-fA-F]+\s+)(.+)$", sLine);
  if oMatch:
    return '<span class="DisassemblyAddress">%s</span><span class="DisassemblyOpcode">%s</span><span class="DisassemblyInstruction">%s</span>' % \
        tuple([oCdbWrapper.fsHTMLEncode(s) for s in oMatch.groups()]);
  return '<span class="DisassemblyInformation">%s</span>' % oCdbWrapper.fsHTMLEncode(sLine);
  
def cBugReport_fsGetDisassemblyHTML(oBugReport, oCdbWrapper, sAddress, sBeforeAddressInstructionDescription = None, sAtAddressInstructionDescription = None):
  # See dxBugIdConfig for a description of these "magic" values.
  uDisassemblyBytesBefore = dxBugIdConfig["uDisassemblyInstructionsBefore"] * dxBugIdConfig["uDisassemblyAverageInstructionSize"] + \
      dxBugIdConfig["uDisassemblyAlignmentBytes"];
  uDisassemblyBytesAfter = dxBugIdConfig["uDisassemblyInstructionsAfter"] * dxBugIdConfig["uDisassemblyAverageInstructionSize"];
  # Get disassembly around code in which exception happened. This may not be possible if the instruction pointer points to unmapped memory.
  asDisassemblyHTML = [];
  if uDisassemblyBytesBefore > 0:
    # Get disassembly before address
    asBeforeDisassembly = oCdbWrapper.fasSendCommandAndReadOutput(
      ".if ($vvalid(%s - 0x%X, 0x%X)) { u %s - 0x%X %s - 1; }; $$ disassemble before address" %
          (sAddress, uDisassemblyBytesBefore, uDisassemblyBytesBefore, sAddress, uDisassemblyBytesBefore, sAddress),
      bOutputIsInformative = True,
    );
    if not oCdbWrapper.bCdbRunning: return None;
    # Limit number of instructions
    asBeforeDisassembly = asBeforeDisassembly[-dxBugIdConfig["uDisassemblyInstructionsBefore"]:];
    if asBeforeDisassembly:
      # Optionally highlight and describe instruction before the address:
      if sBeforeAddressInstructionDescription:
        sBeforeAddressDisassembly = asBeforeDisassembly.pop(-1);
      asDisassemblyHTML += [fsHTMLEncodeAndColorDisassemblyLine(oCdbWrapper, s) for s in asBeforeDisassembly];
      if sBeforeAddressInstructionDescription:
        asDisassemblyHTML.append(
          "<span class=\"Important\">%s &#8656; %s</span>" % \
              (fsHTMLEncodeAndColorDisassemblyLine(oCdbWrapper, sBeforeAddressDisassembly.ljust(80)), sBeforeAddressInstructionDescription)
        );
  if uDisassemblyBytesAfter > 0:
    asAtAndAfterDisassembly = oCdbWrapper.fasSendCommandAndReadOutput(
      ".if ($vvalid(%s, 0x%X)) { u %s %s + 0x%X; }; $$ Disassemble after address" %
          (sAddress, uDisassemblyBytesAfter, sAddress, sAddress, uDisassemblyBytesAfter - 1),
      bOutputIsInformative = True,
    );
    if not oCdbWrapper.bCdbRunning: return None;
    # The first line contains the address of the instruction
    sAddress = asAtAndAfterDisassembly.pop(0);
    asDisassemblyHTML.append(fsHTMLEncodeAndColorDisassemblyLine(oCdbWrapper, sAddress));
    # Limit number of instructions
    asAtAndAfterDisassembly = asAtAndAfterDisassembly[:dxBugIdConfig["uDisassemblyInstructionsAfter"]];
    if asAtAndAfterDisassembly:
      if not asDisassemblyHTML:
        asDisassemblyHTML.append("(prior disassembly not possible)");
      # Optionally highlight and describe instruction at the address:
      if sAtAddressInstructionDescription:
        sAtAddressDisassembly = asAtAndAfterDisassembly.pop(0);
        asDisassemblyHTML.append(
          "<span class=\"Important\">%s &#8656; %s</span>" % \
              (fsHTMLEncodeAndColorDisassemblyLine(oCdbWrapper, sAtAddressDisassembly.ljust(80)), sAtAddressInstructionDescription)
        );
      asDisassemblyHTML += [fsHTMLEncodeAndColorDisassemblyLine(oCdbWrapper, s) for s in asAtAndAfterDisassembly];
    elif asDisassemblyHTML:
      asDisassemblyHTML.append("(further disassembly not possible)");
  if asDisassemblyHTML:
    return "<br/>".join(asDisassemblyHTML);
  return None;
