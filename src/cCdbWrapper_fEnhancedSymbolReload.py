import os, re;
from dxBugIdConfig import dxBugIdConfig;

def cCdbWrapper_fEnhancedSymbolReload(oCdbWrapper):
  if dxBugIdConfig["bEnhancedSymbolLoading"]:
    # Try to reload all modules and their PDB files up to 10 times until there are no more corrupt files.
    for x in xrange(10):
      asOutput = oCdbWrapper.fasSendCommandAndReadOutput(".reload /v");
      if not oCdbWrapper.bCdbRunning: return;
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
