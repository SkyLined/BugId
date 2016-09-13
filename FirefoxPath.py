import os;
from fsFirstExistingFile import fsFirstExistingFile;
sProgramFilesPath = os.getenv("ProgramFiles");
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");
sLocalAppData = os.getenv("LocalAppData");

# Firefox Developer Edition
sFirefoxDevPath_x64 = sProgramFilesPath_x64 and fsFirstExistingFile(
  r"%s\Firefox Developer Edition\firefox.exe" % sProgramFilesPath_x64,
);
sFirefoxDevPath_x86 = fsFirstExistingFile(
  r"%s\Firefox Developer Edition\firefox.exe" % sProgramFilesPath_x86,
);
sFirefoxDevPath = sFirefoxDevPath_x64 or sFirefoxDevPath_x86;
# Firefox stable (if installed, otherwise use Firefox Developer Edition if installed).
sFirefoxPath_x64 = sProgramFilesPath_x64 and fsFirstExistingFile(
  r"%s\Mozilla Firefox\firefox.exe" % sProgramFilesPath_x64,
  sFirefoxDevPath_x64,
);
sFirefoxPath_x86 = fsFirstExistingFile(
  r"%s\Mozilla Firefox\firefox.exe" % sProgramFilesPath_x86,
  sFirefoxDevPath_x86,
);
sFirefoxPath = sFirefoxPath_x64 or sFirefoxPath_x86 or sFirefoxDevPath;
