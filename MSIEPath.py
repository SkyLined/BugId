import os;
from fsFirstExistingFile import fsFirstExistingFile;
sProgramFilesPath = os.getenv("ProgramFiles");
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");
sLocalAppData = os.getenv("LocalAppData");

# Microsoft Internet Explorer
sMSIEPath_x64 = sProgramFilesPath_x64 and fsFirstExistingFile(
  r"%s\Internet Explorer\iexplore.exe" % sProgramFilesPath_x64,
);
sMSIEPath_x86 = fsFirstExistingFile(
  r"%s\Internet Explorer\iexplore.exe" % sProgramFilesPath_x86,
);
sMSIEPath = sMSIEPath_x64 or sMSIEPath_x86;
