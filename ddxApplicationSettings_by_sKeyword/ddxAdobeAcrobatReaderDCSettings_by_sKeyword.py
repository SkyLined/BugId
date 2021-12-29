import os;

from .fsFirstExistingFile import fsFirstExistingFile;

sProgramFilesPath = os.getenv("ProgramFiles");
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");

dxConfigSettings = {
  "bApplicationTerminatesWithMainProcess": True,
  "n0ApplicationMaxRunTimeInSeconds": 60.0, # This application can load very slowly, so give it a little more time than others.
};

sApplicationBinaryPath_x86 = fsFirstExistingFile(
  r"%s\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe" % sProgramFilesPath_x86,
  r"%s\Adobe\Acrobat DC\Acrobat\Acrobat.exe" % sProgramFilesPath_x86,
);
sApplicationBinaryPath = sApplicationBinaryPath_x86;

def fasGetStaticArguments(dxConfig, bForHelp = False):
  return ["repro.pdf"]; # Does not matter if it's for help or not: value is the same

ddxAdobeAcrobatReaderDCSettings_by_sKeyword = {
  "acrobatdc": {
    "sBinaryPath": sApplicationBinaryPath,
    "fasGetStaticArguments": fasGetStaticArguments,
    "dxConfigSettings": dxConfigSettings,
    # Adobe Reader has a component that constantly crashes with a NULL pointer when you enable page heap.
    "asBinaryNamesThatAreAllowedToRunWithoutPageHeap": [
      "AcroCEF.exe",
      "rdrcef.exe",
    ],
  },
  "acrobatdc_x86": {
    "sBinaryPath": sApplicationBinaryPath_x86,
    "fasGetStaticArguments": fasGetStaticArguments,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x86",
    # Adobe Reader has a component that constantly crashes with a NULL pointer when you enable page heap.
    "asBinaryNamesThatAreAllowedToRunWithoutPageHeap": [
      "AcroCEF.exe",
      "rdrcef.exe"
    ],
  },
};