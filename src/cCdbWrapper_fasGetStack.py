import os, re;
from dxBugIdConfig import dxBugIdConfig;

def cCdbWrapper_fasGetStack(oCdbWrapper, sGetStackCommand):
  if dxBugIdConfig["bEnhancedSymbolLoading"]:
    # Get the stack, which should make sure all relevant symbols are loaded or at least marked as requiring loading.
    # Not all symbols may have been loaded correctly, so the output is ignored.
    oCdbWrapper.fasSendCommandAndReadOutput(sGetStackCommand);
    if not oCdbWrapper.bCdbRunning: return None;
    # Turn noisy symbol loading on
    oCdbWrapper.fasSendCommandAndReadOutput(".symopt+ 0x80000000");
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
      for sLine in asOutput:
        # If there are any corrupt PDB files, try to delete them.
        oCorruptPDBFilePathMatch = re.match(r"^DBGHELP: (.*?) (\- E_PDB_CORRUPT|dia error 0x[0-9a-f]+)\s*$", sLine);
        if oCorruptPDBFilePathMatch:
          sPDBFilePath = oCorruptPDBFilePathMatch.group(1);
          asCorruptPDBFilePaths.add(sPDBFilePath);
      bCorruptPDBFilesDeleted = False;
      for sCorruptPDBFilePath in asCorruptPDBFilePaths:
        print "* Deleting corrupt pdb file: %s" % sCorruptPDBFilePath;
        try:
          os.remove(sCorruptPDBFilePath);
        except Exception, oException:
          print "- Cannot delete corrupt pdb file: %s" % repr(oException);
        else:
          bCorruptPDBFilesDeleted = True;
      if not bCorruptPDBFilesDeleted:
        # If no corrupt PDB files were deleted, stop reloading modules.
        break;
    # Turn noisy symbol loading back off
    asOutput = oCdbWrapper.fasSendCommandAndReadOutput(".symopt- 0x80000000");
    if not oCdbWrapper.bCdbRunning: return None;
  # Get the stack for real.
  asStack = oCdbWrapper.fasSendCommandAndReadOutput(sGetStackCommand);
  if not oCdbWrapper.bCdbRunning: return None;
  return asStack;
