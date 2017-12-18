import os;
from dxConfig import dxConfig;
from fsFirstExistingFile import fsFirstExistingFile;
sProgramFilesPath = os.getenv("ProgramFiles");
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");
sLocalAppData = os.getenv("LocalAppData");

dxConfigSettings = {
  # Settings used by all browsers (these should eventually be fine-tuned for each browser)
  "bApplicationTerminatesWithMainProcess": True,
  "nExcessiveCPUUsageCheckInitialTimeout": 30.0, # Give browser some time to load repro
  "cBugId.nExcessiveCPUUsageCheckInterval": 30.0, # Browser may be busy for a bit, but no longer than 30 seconds.
  "cBugId.nExcessiveCPUUsagePercent": 95,      # Browser msust be very, very busy.
  "cBugId.nExcessiveCPUUsageWormRunTime": 0.5, # Any well written function should return within half a second IMHO.
};

# Chrome Canary (if installed)
sChromeSxSPath_x64 = sProgramFilesPath_x64 and fsFirstExistingFile(
  r"%s\Google\Chrome SxS\Application\chrome.exe" % sProgramFilesPath_x64,
  r"%s\Google\Chrome SxS\Application\chrome.exe" % sLocalAppData,
);
sChromeSxSPath_x86 = fsFirstExistingFile(
  r"%s\Google\Chrome SxS\Application\chrome.exe" % sProgramFilesPath_x86,
  r"%s\Google\Chrome SxS\Application\chrome.exe" % sLocalAppData,
);
sChromeSxSPath = sChromeSxSPath_x64 or sChromeSxSPath_x86;
# Chrome stable (if installed)
sChromePath_x64 = sProgramFilesPath_x64 and fsFirstExistingFile(
  r"%s\Google\Chrome\Application\chrome.exe" % sProgramFilesPath_x64,
  r"%s\Google\Chrome\Application\chrome.exe" % sLocalAppData,
);
if os.getenv("ProgramFiles(x86)"):
  # on x64 systems, x64 versions of Chrome can be installed in the x86 Program Files folder...
  sChromePath_x64 = sChromePath_x64 or fsFirstExistingFile(
    r"%s\Google\Chrome\Application\chrome.exe" % sProgramFilesPath_x86,
  );
sChromePath_x86 = fsFirstExistingFile(
  r"%s\Google\Chrome\Application\chrome.exe" % sProgramFilesPath_x86,
  r"%s\Google\Chrome\Application\chrome.exe" % sLocalAppData,
);
sChromePath = sChromePath_x64 or sChromePath_x86 or sChromeSxSPath;


def fasGetChromeStaticArguments(bForHelp = False):
  return [
    "--enable-experimental-accessibility-features",
    "--enable-experimental-canvas-features",
    "--enable-experimental-input-view-features",
    "--enable-experimental-web-platform-features",
    "--enable-logging=stderr",
    "--enable-usermedia-screen-capturing",
    "--enable-viewport",
    "--enable-webgl-draft-extensions",
    "--enable-webvr",
    "--expose-internals-for-testing",
    "--disable-popup-blocking",
    "--disable-prompt-on-repost",
    "--force-renderer-accessibility",
    "--javascript-harmony",
    "--js-flags=\"--expose-gc\"",
    "--no-sandbox",
  ];

def fasGetChromeOptionalArguments(bForHelp = False):
  return bForHelp and ["<dxConfig.sDefaultBrowserTestURL>"] or [dxConfig["sDefaultBrowserTestURL"]];

ddxChromeSettings_by_sKeyword = {
  "chrome": {
    "sBinaryPath": sChromePath,
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
  },
  "chrome_x86": {
    "sBinaryPath": sChromePath_x86,
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x86",
  },
  "chrome_x64": {
    "sBinaryPath": sChromePath_x64,
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x64",
  },
  "chrome-sxs": {
    "sBinaryPath": sChromeSxSPath,
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
  },
  "chrome-sxs_x86": {
    "sBinaryPath": sChromeSxSPath_x86,
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x86",
  },
  "chrome-sxs_x64": {
    "sBinaryPath": sChromeSxSPath_x64,
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x64",
  },
};
