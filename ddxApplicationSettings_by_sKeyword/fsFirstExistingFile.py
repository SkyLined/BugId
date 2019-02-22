import mFileSystem2;
def fsFirstExistingFile(*asPossiblePaths):
  for sPossiblePath in asPossiblePaths:
    if sPossiblePath and mFileSystem2.fo0GetFile(sPossiblePath):
      return sPossiblePath;
  return None;

