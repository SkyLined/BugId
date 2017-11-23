import os;
from fsFirstExistingFile import fsFirstExistingFile;
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");

# Firefox stable (if installed, otherwise use Firefox Developer Edition if installed).
sFirefoxPath_x64 = sProgramFilesPath_x64 and fsFirstExistingFile(
  r"%s\Mozilla Firefox\firefox.exe" % sProgramFilesPath_x64,
);
sFirefoxPath_x86 = fsFirstExistingFile(
  r"%s\Mozilla Firefox\firefox.exe" % sProgramFilesPath_x86,
);
sFirefoxPath = sFirefoxPath_x64 or sFirefoxPath_x86;
