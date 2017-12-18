import mFileSystem;
def fsFirstExistingFile(*asPossiblePaths):
  for sPossiblePath in asPossiblePaths:
    if sPossiblePath and mFileSystem.fbIsFile(sPossiblePath):
      return sPossiblePath;
  return None;

