import os;
from fsFirstExistingFile import fsFirstExistingFile;
sProgramFilesPath = os.getenv("ProgramFiles");
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");

dxConfigSettings = {
  "bApplicationTerminatesWithMainProcess": True,
  "nApplicationMaxRunTime": 60.0, # This application can load very slowly, so give it a little more time than others.
};

sApplicationBinaryPath_x86 = fsFirstExistingFile(
  r"%s\Foxit Software\Foxit Reader\FoxitReader.exe" % sProgramFilesPath_x86,
);
sApplicationBinaryPath = sApplicationBinaryPath_x86;

def fasGetOptionalArguments(bForHelp = False):
  return ["repro.pdf"]; # Does not matter if it's for help or not: value is the same

ddxFoxitReaderSettings_by_sKeyword = {
  "foxit": {
    "sBinaryPath": sApplicationBinaryPath,
    "fasGetOptionalArguments": fasGetOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
  },
  "foxit_x86": {
    "sBinaryPath": sApplicationBinaryPath_x86,
    "fasGetOptionalArguments": fasGetOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x86",
  },
};