import FileSystem;
def fsFirstExistingFile(*asPossiblePaths):
  for sPossiblePath in asPossiblePaths:
    if sPossiblePath and FileSystem.fbIsFile(sPossiblePath):
      return sPossiblePath;
  return None;

