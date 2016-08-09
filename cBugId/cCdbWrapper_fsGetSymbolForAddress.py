import re;

def cCdbWrapper_fsGetSymbolForAddress(oCdbWrapper, sAddress):
  oCdbWrapper.fasSendCommandAndReadOutput('.printf "%%y\\n", %s; $$ Get symbol warmup' % sAddress);
  asSymbolResult = oCdbWrapper.fasSendCommandAndReadOutput( \
      '.printf "%%y\\n", %s;lmi a %s; $$ Get symbol' % (sAddress, sAddress));
  if not oCdbWrapper.bCdbRunning: return;
  # Output for a NULL pointer:
  #   >00000000
  #   >start    end        module name
  #   (list of all modules)
  # Output for an invalid address (1):
  #   >00000001
  #   >start    end        module name
  if re.match(r"^[0-9A-F`]+\s*$", asSymbolResult[0]):
    return None; # Invalid address.
  # Output for a module without symbol information (in x64 debugger):
  #   >nmozglue+0xf0c4 (73f1f0c4)
  #   >start             end                 module name
  #   >73f10000 73f2d000   mozglue    (no symbols)           
  # Output for a valid symbol (in x86 debugger, notice different header aligning):
  #   >ntdll!DbgBreakPoint (77ec1250)
  #   >start    end        module name
  #   >77e30000 77fab000   nldll      (pdb symbols)          C:\WINDOWS\SYSTEM32\ntdll.dll
  assert len(asSymbolResult) == 3, \
      "Unexpected symbol result:\r\n%s" % "\r\n".join(asSymbolResult);
  oFirstLine = re.match(r"^%s\s*$" % "".join([
    r"(?:([^!]+)!)?",    # module (optional)
    r"([^\+]+)",         # symbol (or module if not above)
    r"(?:\+0x\w+)? ",    # offset (optional)
    r"\([\w`]+\)",       # address
  ]), asSymbolResult[0]);
  assert oFirstLine, \
      "Unexpected symbol result first line:\r\n%s" % "\r\n".join(asSymbolResult);
  sCdbModuleName1, sSymbolName = oFirstLine.groups();
  if sCdbModuleName1 is None:
    sCdbModuleName1 = sSymbolName;
    sSymbolName = None;
  oSecondLine = re.match(r"^start\s+end\s+module name\s*$", asSymbolResult[1]);
  assert oSecondLine, \
      "Unexpected symbol result second line:\r\n%s" % "\r\n".join(asSymbolResult);
  oThirdLine = re.match(r"^%s\s*$" % "".join([
    r"[\w`]+\s+",         # start " "
    r"[\w`]+\s+",         # end " "
    r"(\S+)\s+",          # module name " "
    r"(?:C)?\s+",         # "C" sometimes appears... no idea what it means.
    r"\(([^\)]+)\)\s+",   # "(" symbol info ")"  " "
    r"(?:.+\\)?",        # file path
    r"([^\\]+?)",         # file name
  ]), asSymbolResult[2]);
  assert oThirdLine, \
      "Unexpected symbol result third line:\r\n%s" % "\r\n".join(asSymbolResult);
  sCdbModuleName2, sSymbolInfo, sModuleFileName = oThirdLine.groups();
  assert sCdbModuleName1 == sCdbModuleName2, \
      "Unexpected symbol module name difference between first and third line:\r\n%s" % "\r\n".join(asSymbolResult);
  if sSymbolName is None:
    assert sSymbolInfo == "no symbols", \
        "Unexpected lack of symbol information:\r\n%s" % "\r\n".join(asSymbolResult);
    # This module has no symbol information, so there are no symbols at this address.
    return None;
  return "%s!%s" % (sModuleFileName, sSymbolName);

