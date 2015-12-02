import os, re;
from dxBugIdConfig import dxBugIdConfig;

def cCdbWrapper_fasGetStack(oCdbWrapper, sGetStackCommand):
  if dxBugIdConfig["bEnhancedSymbolLoading"]:
    # Turn noisy symbol loading on
    oCdbWrapper.fasSendCommandAndReadOutput(".symopt+ 0x80000000");
    if not oCdbWrapper.bCdbRunning: return None;
    # Get the stack, which should make sure all relevant symbols are loaded or at least marked as requiring loading.
    # There will be symbol loading debug messages in between the stack output, so the stack cannot easily be parsed.
    # The output is saved in a local variable in case an assertion is thrown.
    asSymbolLoadDebugStack = oCdbWrapper.fasSendCommandAndReadOutput(sGetStackCommand);
    if not oCdbWrapper.bCdbRunning: return None;
    # Try to reload all modules and symbols. The symbol loader will not reload all symbols, but only those symbols that
    # were loaded before or those it attempted to load before, but failed. The symbol loader will output all kinds of
    # cruft, which may contain information about PDB files that cannot be loaded (e.g. corrupt files). If any such
    # issues are detected, these PDB files are deleted and the code loops, so the symbol loader can download them
    # again and any further issues can be detected and fixed. The code loops until there are no more issues that can be
    # fixed, or it has run ten times.
    # This step may also provide some help debugging symbol loading problems that cannot be fixed automatically.
    for x in xrange(10):
      asOutput = oCdbWrapper.fasSendCommandAndReadOutput(".reload /v");
      if not oCdbWrapper.bCdbRunning: return None;
      asCorruptPDBFilePaths = set();
      bErrorsDuringLoading = False;
      for sLine in asOutput:
        # If there are any corrupt PDB files, try to delete them.
        oCorruptPDBFilePathMatch = re.match(r"^DBGHELP: (.*?) (\- E_PDB_CORRUPT|dia error 0x[0-9a-f]+)\s*$", sLine);
        if oCorruptPDBFilePathMatch:
          sPDBFilePath = oCorruptPDBFilePathMatch.group(1);
          asCorruptPDBFilePaths.add(sPDBFilePath);
        # If there were any errors, make sure we try loading again.
        bErrorsDuringLoading |= re.match(r"^\*\*\* ERROR: .+$", sLine) and True or False;
      bCorruptPDBFilesDeleted = False;
      for sCorruptPDBFilePath in asCorruptPDBFilePaths:
        print "* Deleting corrupt pdb file: %s" % sCorruptPDBFilePath;
        try:
          os.remove(sCorruptPDBFilePath);
        except Exception, oException:
          print "- Cannot delete corrupt pdb file: %s" % repr(oException);
        else:
          bCorruptPDBFilesDeleted = True;
      if not (bErrorsDuringLoading or bCorruptPDBFilesDeleted):
        break;
    # Turn noisy symbol loading back off
    asOutput = oCdbWrapper.fasSendCommandAndReadOutput(".symopt- 0x80000000");
    if not oCdbWrapper.bCdbRunning: return None;
  # Get the stack for real.
  asStack = oCdbWrapper.fasSendCommandAndReadOutput(sGetStackCommand);
  # Getting the stack twice does not always work: for unknown reasons the second time the stack may be truncated or
  # incorrect. So, if an error in symbol loading is detected while getting the stack, there is no reliable way to try
  # to reload the symbols and get the stack again: we must throw an exception.
  assert not re.match(r"^\*\*\* ERROR: Module load completed but symbols could not be loaded for .+$", asStack[0]), \
      "CDB failed to load symbols: %s" % asStack[0];
  if not oCdbWrapper.bCdbRunning: return None;
  return asStack;
