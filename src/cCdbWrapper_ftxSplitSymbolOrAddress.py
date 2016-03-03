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
      r")"                                #   }
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
  uModuleOffset = (
    sUnloadedModuleOffset and long(sUnloadedModuleOffset.replace("`", ""), 16) or
    sModuleOffset and long(sModuleOffset.replace("`", ""), 16)
  );
  uSymbolOffset = sSymbolOffset and long(sSymbolOffset.replace("`", ""), 16);
  if sModuleCdbId == "SharedUserData":
    # "ShareUserData" is a symbol outside of any module that gets used as a module name in cdb.
    # Any value referencing it must be converted to an address:
    sBaseSymbol = "SharedUserData";
    if sSymbol: sBaseSymbol += "!%s" % sSymbol;
    uAddress = oCdbWrapper.fuEvaluateExpression(sBaseSymbol);
    if uModuleOffset: uAddress += uModuleOffset;
    if uSymbolOffset: uAddress += uSymbolOffset;
    # Clean up:
    oModule = None;
    uModuleOffset = None;
    oFunction = None;
    uFunctionOffset = None;
  else:
    uAddress = sAddress and long(sAddress.replace("`", ""), 16);
    oModule = sModuleCdbId and doModules_by_sCdbId[sModuleCdbId];
    oFunction = oModule and sSymbol and oModule.foGetOrCreateFunction(sSymbol);
    uFunctionOffset = uSymbolOffset;
  return (
    uAddress,
    sUnloadedModuleFileName, oModule, uModuleOffset,
    oFunction, uFunctionOffset
  );