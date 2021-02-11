from cFileSystemItem import cFileSystemItem;

def fsFirstExistingFile(*asPossiblePaths):
  for sPossiblePath in asPossiblePaths:
    if sPossiblePath and cFileSystemItem(sPossiblePath).fbIsFile():
      return sPossiblePath;
  return None;

