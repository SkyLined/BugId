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
  "bOutputStdIn": False,        # Output cdb input (commands) send to cdb while debugging application
  "bOutputStdOut": False,       # Output cdb output while debugging application
  "bOutputStdErr": True,        # Output cdb error output, which probably comes from the debugged application.
  "bOutputFirstChanceExceptions": False, # Are first chance exceptions detected and output?
  "bOutputCommandLine": False,  # Is the cbd.exe command line printed before execution?
  "bOutputProcesses": True,     # Output process details whenever one is created/attached to/terminated.
  "uMaxAddressOffset": 0x1000,  # How far from an address can a pointer be offset and still be considered to point to it?
  "uMaxFunctionOffset": 0xFFF,  # How far from a function symbol can a pointer be offset and still be cosidered to point to it?
  "uMaxStackFramesCount": 100,  # How many stack frames are retreived for analysis?
  "uStackHashFramesCount": 2,   # How many stack frames are hashed for the crash id?
  "uReserveRAM": 0,             # How many bytes of RAM should be allocate at start of debugging, so they can be
                                # released later to allow analysis under low memory conditions.
  "bEnhancedSymbolLoading": False, # Enabled additional checks when getting a stack that can detect and fix errors in
                                # symbol loading caused by corrupted pdb files. This turns on "noisy symbol loading"
                                # which may provide useful information to fix symbol loading errors. It has a large
                                # impact on performance, which is why it is disabled by default.
  "asSymbolCachePaths": [],     # Where should symbols be cached?
  "sCdbBinaryPath_x86": dsCdbBinaryPath_sISA.get("x86"),
  "sCdbBinaryPath_x64": dsCdbBinaryPath_sISA.get("x64"),
  "sKillBinaryPath_x86": dsKillBinaryPath_sISA.get("x86"),
  "sKillBinaryPath_x64": dsKillBinaryPath_sISA.get("x64"),
}.items():
  if sName not in dxBugIdConfig:
    dxBugIdConfig[sName] = xValue;
