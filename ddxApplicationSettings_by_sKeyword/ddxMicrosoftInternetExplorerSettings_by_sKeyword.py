import os;
from dxConfig import dxConfig;
from fsFirstExistingFile import fsFirstExistingFile;
sProgramFilesPath = os.getenv("ProgramFiles");
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");

dxConfigSettings = {
  # Settings used by all browsers (these should eventually be fine-tuned for each browser)
  "bApplicationTerminatesWithMainProcess": True,
  "nExcessiveCPUUsageCheckInitialTimeout": 30.0, # Give browser some time to load repro
  "cBugId.nExcessiveCPUUsageCheckInterval": 30.0, # Browser may be busy for a bit, but no longer than 30 seconds.
  "cBugId.nExcessiveCPUUsagePercent": 95,      # Browser msust be very, very busy.
  "cBugId.nExcessiveCPUUsageWormRunTime": 0.5, # Any well written function should return within half a second IMHO.
  "cBugId.bIgnoreCPPExceptions": True,
  "cBugId.bIgnoreWinRTExceptions": True,
};

# Microsoft Internet Explorer
sApplicationBinaryPath_x64 = sProgramFilesPath_x64 and fsFirstExistingFile(
  r"%s\Internet Explorer\iexplore.exe" % sProgramFilesPath_x64,
);
sApplicationBinaryPath_x86 = fsFirstExistingFile(
  r"%s\Internet Explorer\iexplore.exe" % sProgramFilesPath_x86,
);
sApplicationBinaryPath = sApplicationBinaryPath_x64 or sApplicationBinaryPath_x86;

def fasGetMSIEOptionalArguments(bForHelp = False):
  return bForHelp and ["<dxConfig.sDefaultBrowserTestURL>"] or [dxConfig["sDefaultBrowserTestURL"]];

ddxMicrosoftInternetExplorerSettings_by_sKeyword = {
  "msie": {
    "sBinaryPath": sApplicationBinaryPath,
    "fasGetOptionalArguments": fasGetMSIEOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
  },
  "msie_x86": {
    "sBinaryPath": sApplicationBinaryPath_x86,
    "fasGetOptionalArguments": fasGetMSIEOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x86",
  },
  "msie_x64": {
    "sBinaryPath": sApplicationBinaryPath_x64,
    "fasGetOptionalArguments": fasGetMSIEOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x64",
  },
};