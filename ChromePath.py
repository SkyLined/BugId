import os;
from fsFirstExistingFile import fsFirstExistingFile;
sProgramFilesPath = os.getenv("ProgramFiles");
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");
sLocalAppData = os.getenv("LocalAppData");

# Chrome Canary
sChromeSxSPath_x64 = sProgramFilesPath_x64 and fsFirstExistingFile(
  r"%s\Google\Chrome SxS\Application\chrome.exe" % sProgramFilesPath_x64,
  r"%s\Google\Chrome SxS\Application\chrome.exe" % sLocalAppData,
);
sChromeSxSPath_x86 = fsFirstExistingFile(
  r"%s\Google\Chrome SxS\Application\chrome.exe" % sProgramFilesPath_x86,
  r"%s\Google\Chrome SxS\Application\chrome.exe" % sLocalAppData,
);
sChromeSxSPath = sChromeSxSPath_x64 or sChromeSxSPath_x86;
# Chrome stable (if installed, otherwise use Chrome Canary if installed).
sChromePath_x64 = sProgramFilesPath_x64 and fsFirstExistingFile(
  r"%s\Google\Chrome\Application\chrome.exe" % sProgramFilesPath_x64,
  r"%s\Google\Chrome\Application\chrome.exe" % sLocalAppData,
  sChromeSxSPath_x64,
);
sChromePath_x86 = fsFirstExistingFile(
  r"%s\Google\Chrome\Application\chrome.exe" % sProgramFilesPath_x86,
  r"%s\Google\Chrome\Application\chrome.exe" % sLocalAppData,
  sChromeSxSPath_x86,
);
sChromePath = sChromePath_x64 or sChromePath_x86 or sChromeSxSPath;
