from dsCdbBinaryPath_sISA import dsCdbBinaryPath_sISA;
# Load base config file
from dxConfig import dxConfig;
# Add CrashInfo group if it doesn't exist.
dxCrashInfoConfig = dxConfig.setdefault("CrashInfo", {});
# Add default values where no values have been supplied:
for (sName, xValue) in {
  "bOutputIO": False,           # Output cdb i/o while debugging application
  "bOutputErrIO": True,         # Output anything cdb or the debugged application sends to stderr.
  "bOutputCommands": False,     # Output commands send to cdb while debugging application
  "bOutputFirstChanceExceptions": False, # Are first chance exceptions detected and output?
  "bOutputCommandLine": False,  # Is the cbd.exe command line printed before execution?
  "bOutputProcesses": True,     # Output process details whenever one is created/attached to/terminated.
  "uMaxAddressOffset": 0x1000,  # How far from an address can a pointer be offset and still be considered to point to it?
  "uMaxFunctionOffset": 0xFFF,  # How far from a function symbol can a pointer be offset and still be cosidered to point to it?
  "uMaxStackFramesCount": 50,   # How many stack frames are retreived for analysis?
  "uStackHashFramesCount": 2,   # How many stack frames are hashed for the crash id?
  "asSymbolCachePaths": [],     # Where are symbols cached?
  "bDebugSymbolLoading": False, # Enable noizy symbol reloading before exception analysis. This will detect, delete and
                                # attempt to reload corrupted pdb files. It impacts performance a bit, but improves
                                # results if you frequently have symbol loading issues that you do not want to fix
                                # manually.
  "sCdbBinaryPath_x86": dsCdbBinaryPath_sISA.get("x86"),
  "sCdbBinaryPath_AMD64": dsCdbBinaryPath_sISA.get("AMD64"),
}.items():
  if sName not in dxCrashInfoConfig:
    dxCrashInfoConfig[sName] = xValue;
