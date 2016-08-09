import re;

def cCdbWrapper_ftxSplitSymbolOrAddress(oCdbWrapper, sSymbolOrAddress, doModules_by_sCdbId):
  oMatch = re.match(r"^\s*%s\s*$" % (
    r"(?:"                                # either {
      r"(0x[0-9A-F`]+)"                   #   ("0x" address)
    r"|"                                  # } or {
      r"<Unloaded_(.*)>"                  #   "<Unloaded_" module_file_name ">"
      r"(\+0x[0-9A-F]+)?"                 #   optional{ ("+0x" offset_in_unloaded_module) }
    "|"                                   # } or {
      r"(\w+)"                            #   (cdb_module_id)
      r"(?:"                              #   either {
        r"(\+0x[0-9A-F]+)"                #     ("+0x" offset_in_module)
      r"|"                                #   } or {
        r"!(.+?)([\+\-]0x[0-9A-F]+)?"     #     "!" (function_name) optional{ (["+" || "-"] "0x" offset) }
      r")?"                                #  } or { nothing }
    r")"                                  # }
  ), sSymbolOrAddress, re.I);
  assert oMatch, "Unknown symbol or address format: %s" % repr(sSymbolOrAddress);
  (
    sAddress,
    sUnloadedModuleFileName,
      sUnloadedModuleOffset,
    sModuleCdbId,
      sModuleOffset,
      sSymbol, sSymbolOffset
  ) = oMatch.groups();
  uAddress = None;
  oModule = None;
  uModuleOffset = None;
  oFunction = None;
  uFunctionOffset = None;
  if sAddress:
    uAddress = long(sAddress.replace("`", ""), 16);
  elif sUnloadedModuleFileName:
    # sUnloadedModuleFileName is returned without modification
    uModuleOffset = sUnloadedModuleOffset and long(sUnloadedModuleOffset.replace("`", ""), 16) or 0;
  elif sModuleCdbId == "SharedUserData":
    # "ShareUserData" is a symbol outside of any module that gets used as a module name in cdb.
    # Any value referencing it will be converted to an address:
    sAddress = "SharedUserData";
    if sSymbol: sAddress += "!%s" % sSymbol;
    uAddress = oCdbWrapper.fuGetValue(sAddress);
    if uModuleOffset: uAddress += uModuleOffset;
    if uSymbolOffset: uAddress += uSymbolOffset;
  else:
    oModule = doModules_by_sCdbId[sModuleCdbId];
    if sSymbol:
      oFunction = oModule.foGetOrCreateFunction(sSymbol);
      uFunctionOffset = sSymbolOffset and long(sSymbolOffset.replace("`", ""), 16) or 0;
    elif sModuleOffset:
      uModuleOffset = long(sModuleOffset.replace("`", ""), 16);
    else:
      uModuleOffset = 0;
  return (
    uAddress,
    sUnloadedModuleFileName, oModule, uModuleOffset,
    oFunction, uFunctionOffset
  );