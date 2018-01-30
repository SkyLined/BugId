import os;
from dxConfig import dxConfig;
from fsFirstExistingFile import fsFirstExistingFile;
sProgramFilesPath = os.getenv("ProgramFiles");
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");
sLocalAppData = os.getenv("LocalAppData");

dxConfigSettings = {
  "bApplicationTerminatesWithMainProcess": True,
};
dxConfigSettingsAsan = dxConfigSettings.copy().update({
  "bIgnoreAccessViolations": True, # ASan throws a lot of these and should detect bugs before AVs happen, so ignore them.
});

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
sApplicationBinaryPath_x64 = sProgramFilesPath_x64 and fsFirstExistingFile(
  r"%s\Google\Chrome\Application\chrome.exe" % sProgramFilesPath_x64,
  r"%s\Google\Chrome\Application\chrome.exe" % sLocalAppData,
);
if os.getenv("ProgramFiles(x86)"):
  # on x64 systems, x64 versions of Chrome can be installed in the x86 Program Files folder...
  sApplicationBinaryPath_x64 = sApplicationBinaryPath_x64 or fsFirstExistingFile(
    r"%s\Google\Chrome\Application\chrome.exe" % sProgramFilesPath_x86,
  );
sApplicationBinaryPath_x86 = fsFirstExistingFile(
  r"%s\Google\Chrome\Application\chrome.exe" % sProgramFilesPath_x86,
  r"%s\Google\Chrome\Application\chrome.exe" % sLocalAppData,
);
sApplicationBinaryPath = sApplicationBinaryPath_x64 or sApplicationBinaryPath_x86 or sChromeSxSPath;

def fasGetChromeStaticArguments(bForHelp = False):
  return [
    "--enable-experimental-accessibility-features",
    "--enable-experimental-canvas-features",
    "--enable-experimental-input-view-features",
    "--enable-experimental-web-platform-features",
    "--enable-logging=stdout",
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

asBinaryNamesThatAreAllowedToRunWithoutPageHeap = [
  "chrome.exe", # ASan Chrome needs no page heap
  "conhost.exe", # Used to dump debug data through stdout, not part of Chrome
  "llvm-symbolizer.exe", # ASan Chrome uses this to dump info, not part of Chrome.
];

def fasGetChromeOptionalArguments(bForHelp = False):
  return bForHelp and ["<dxConfig.sDefaultBrowserTestURL>"] or [dxConfig["sDefaultBrowserTestURL"]];

# The `--enable-logging=stderr` argument causes Chrome to open a console in which to output log messages. This console
# runs in a "conhost.exe" process, which is part of Windows and not of Chrome. It makes sense that you would not care
# about it when looking for bugs in Chrome, and leave page disabled in this process.
ddxGoogleChromeSettings_by_sKeyword = {
  "chrome": {
    "sBinaryPath": sApplicationBinaryPath,
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "asBinaryNamesThatAreAllowedToRunWithoutPageHeap": ["conhost.exe"],
  },
  "chrome_x86": {
    "sBinaryPath": sApplicationBinaryPath_x86,
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x86",
    "asBinaryNamesThatAreAllowedToRunWithoutPageHeap": ["conhost.exe"],
  },
  "chrome_x64": {
    "sBinaryPath": sApplicationBinaryPath_x64,
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x64",
    "asBinaryNamesThatAreAllowedToRunWithoutPageHeap": asBinaryNamesThatAreAllowedToRunWithoutPageHeap,
  },
  "chrome_asan": {
    "sBinaryPath": None, # We do not know where the user installed it
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettingsAsan,
    "asBinaryNamesThatAreAllowedToRunWithoutPageHeap": asBinaryNamesThatAreAllowedToRunWithoutPageHeap,
  },
  "chrome_asan_x86": {
    "sBinaryPath": None, # We do not know where the user installed it
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettingsAsan,
    "sISA": "x86",
    "asBinaryNamesThatAreAllowedToRunWithoutPageHeap": asBinaryNamesThatAreAllowedToRunWithoutPageHeap,
  },
  "chrome_asan_x64": {
    "sBinaryPath": None, # We do not know where the user installed it
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettingsAsan,
    "sISA": "x64",
    "asBinaryNamesThatAreAllowedToRunWithoutPageHeap": asBinaryNamesThatAreAllowedToRunWithoutPageHeap,
  },
  "chrome-sxs": {
    "sBinaryPath": sChromeSxSPath,
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "asBinaryNamesThatAreAllowedToRunWithoutPageHeap": asBinaryNamesThatAreAllowedToRunWithoutPageHeap,
  },
  "chrome-sxs_x86": {
    "sBinaryPath": sChromeSxSPath_x86,
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x86",
    "asBinaryNamesThatAreAllowedToRunWithoutPageHeap": asBinaryNamesThatAreAllowedToRunWithoutPageHeap,
  },
  "chrome-sxs_x64": {
    "sBinaryPath": sChromeSxSPath_x64,
    "fasGetStaticArguments": fasGetChromeStaticArguments,
    "fasGetOptionalArguments": fasGetChromeOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x64",
    "asBinaryNamesThatAreAllowedToRunWithoutPageHeap": asBinaryNamesThatAreAllowedToRunWithoutPageHeap,
  },
};
