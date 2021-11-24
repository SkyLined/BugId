import os;

from .fsFirstExistingFile import fsFirstExistingFile;

sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");

dxConfigSettings = {
  "bApplicationTerminatesWithMainProcess": True,
  "nApplicationMaxRunTimeInSeconds": 60.0, # This application can load very slowly, so give it a little more time than others.
};

sApplicationBinaryPath_x86 = fsFirstExistingFile(
  r"%s\Microsoft Office\Office14\OUTLOOK.EXE" % sProgramFilesPath_x86,
  r"%s\Microsoft Office\Office15\OUTLOOK.EXE" % sProgramFilesPath_x86,
  r"%s\Microsoft Office\root\Office16\OUTLOOK.EXE" % sProgramFilesPath_x86,
);
sApplicationBinaryPath_x64 = fsFirstExistingFile(
  r"%s\Microsoft Office\Office14\OUTLOOK.EXE" % sProgramFilesPath_x64,
  r"%s\Microsoft Office\Office15\OUTLOOK.EXE" % sProgramFilesPath_x64,
  r"%s\Microsoft Office\root\Office16\OUTLOOK.EXE" % sProgramFilesPath_x64,
);
sApplicationBinaryPath = sProgramFilesPath_x64 or sProgramFilesPath_x86;

ddxMicrosoftOutlookSettings_by_sKeyword = {
  "outlook": {
    "sBinaryPath": sApplicationBinaryPath,
    "dxConfigSettings": dxConfigSettings,
  },
  "outlook_x86": {
    "sBinaryPath": sApplicationBinaryPath_x86,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x86",
  },
  "outlook_x64": {
    "sBinaryPath": sApplicationBinaryPath_x86,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x64",
  },
};