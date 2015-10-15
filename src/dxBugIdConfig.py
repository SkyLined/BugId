from dsCdbBinaryPath_sISA import dsCdbBinaryPath_sISA;
from dsKillBinaryPath_sISA import dsKillBinaryPath_sISA;
# Load base config file
try:
  from dxConfig import dxConfig;
except:
  dxConfig = {};
# Add BugId group if it doesn't exist.
dxBugIdConfig = dxConfig.setdefault("BugId", {});
# Add default values where no values have been supplied:
for (sName, xValue) in {
  "bSaveDump": False,           # Save a dump file.
  "bOverwriteDump": False,      # Overwrite any existing dump file.
  "bOutputStdIO": False,        # Output cdb i/o while debugging application
  "bOutputErrIO": True,         # Output anything cdb or the debugged application sends to stderr.
  "bOutputCommands": False,     # Output commands send to cdb while debugging application
  "bOutputFirstChanceExceptions": False, # Are first chance exceptions detected and output?
  "bOutputCommandLine": False,  # Is the cbd.exe command line printed before execution?
  "bOutputProcesses": True,     # Output process details whenever one is created/attached to/terminated.
  "uMaxAddressOffset": 0x1000,  # How far from an address can a pointer be offset and still be considered to point to it?
  "uMaxFunctionOffset": 0xFFF,  # How far from a function symbol can a pointer be offset and still be cosidered to point to it?
  "uMaxStackFramesCount": 100,  # How many stack frames are retreived for analysis?
  "uStackHashFramesCount": 2,   # How many stack frames are hashed for the crash id?
  "asSymbolCachePaths": [],     # Where are symbols cached?
  "bEnhancedSymbolLoading": False, # Enable noizy symbol loading and reload symbols for all modules before exception
                                # analysis. This will also detect and delete corrupted pdb files and try to reload
                                # them. It has a large impact on performance, but improves the accuracy of results if
                                # you frequently have corrupt symbol files in an automated testing environment.
  "sCdbBinaryPath_x86": dsCdbBinaryPath_sISA.get("x86"),
  "sCdbBinaryPath_AMD64": dsCdbBinaryPath_sISA.get("AMD64"),
  "sKillBinaryPath_x86": dsKillBinaryPath_sISA.get("x86"),
  "sKillBinaryPath_AMD64": dsKillBinaryPath_sISA.get("AMD64"),
}.items():
  if sName not in dxBugIdConfig:
    dxBugIdConfig[sName] = xValue;
