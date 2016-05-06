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
  ### cdb/kill binary settings
  "sCdbBinaryPath_x86": dsCdbBinaryPath_sISA.get("x86"),
  "sCdbBinaryPath_x64": dsCdbBinaryPath_sISA.get("x64"),
  "sKillBinaryPath_x86": dsKillBinaryPath_sISA.get("x86"),
  "sKillBinaryPath_x64": dsKillBinaryPath_sISA.get("x64"),
  ### Exception control
  "bIgnoreFirstChanceBreakpoints": False, # Can be used to ignore first chance debugger breakpoints. This may be useful
                                # if the application has these for debugging purposes, but they are not used to report
                                # fatal bugs. When enabled, only second chance debugger breakpoints are analyzed.
  ### Console output
  "bOutputStdIn": False,        # Output cdb input (commands) send to cdb while debugging application
  "bOutputStdOut": False,       # Output cdb output while debugging application
  "bOutputStdErr": True,        # Output cdb error output, which probably comes from the debugged application.
  "bOutputFirstChanceExceptions": False, # Are first chance exceptions detected and output?
  "bOutputCommandLine": False,  # Is the cbd.exe command line printed before execution?
  "bOutputProcesses": True,     # Output process details whenever one is created/attached to/terminated.
  ### Pointer settings
  "uMaxAddressOffset": 0x1000,  # How far from an address can a pointer be offset and still be considered to point to it?
  "uMaxOffsetMultiplier": 4,    # Show <address + N> - <address + X * N> where X is this number. Use 0 for <address + offset>
  "uMaxFunctionOffset": 0xFFF,  # How far from a function symbol can a pointer be offset and still be cosidered to point to it?
  ### Disassembly settings
  "uDisassemblyInstructionsBefore": 0x20, # How many instructions to disassemble before the instruction that triggered the crash
  "uDisassemblyInstructionsAfter": 0x10, # How many instructions to disassemble after the instruction that triggered the crash
  "uDisassemblyAlignmentBytes": 10, # How many instructions to start disassembling before the first instruction we're interested
                                # in, in order to make sure we don't start diassembling in the middle of that instruction.
  "uDisassemblyAverageInstructionSize": 4, # Use to guess how many bytes to disassemble to get the requested number of instructions
                                # Note: BugId disassembles A * B + C bytes before and after the instruction that triggered the crash,
                                # where A is the number of instructions requested, B is the average instruction size provided, and
                                # C is the number of alignment bytes (only used for the "before" instructions, it's 0 for "after").
                                # If uDisassemblyAlignmentBytes is too small, the first instruction you see may not be an instruction
                                # that will ever get executed, as disassembly happed in the middle of the "real" instruction.
                                # If uDisassemblyAverageInstructionSize is too small, you may see less instructions than
                                # requested when not enough bytes get disassembled to get the requested number of instructions.
                                # If the total number of bytes disassembled is too large, you may get no disassembly at all when
                                # part of the memory it attempts to disassemble is not readable.
  ### Stack settings
  "uMaxStackFramesCount": 100,  # How many stack frames are retreived for analysis?
  "uStackHashFramesCount": 2,   # How many stack frames are hashed for the crash id?
  "uMaxStackFrameHashChars": 3, # How many characters of hash to use in the id for each stack frame.
  ### Symbol loading settings
  "bEnhancedSymbolLoading": False, # Enable additional checks when getting a stack that can detect and fix errors in
                                # symbol loading caused by corrupted pdb files. This turns on "noisy symbol loading"
                                # which may provide useful information to fix symbol loading errors. It has a large
                                # impact on performance, which is why it is disabled by default.
  "asSymbolCachePaths": [],     # Where should symbols be cached?
  ### Source code settings
  "bEnableSourceCodeSupport": True, # Tell cdb to load source line symbols or not.
  "dsURLTemplate_by_srSourceFilePath": {}, # Used to translate source file paths to links to online code repository.
  ### Dump file settings
  "bSaveDump": False,           # Save a dump file.
  "bOverwriteDump": False,      # Overwrite any existing dump file.
  ### OOM mitigations
  "uReserveRAM": 0,             # How many bytes of RAM should be allocate at start of debugging, so they can be
                                # released later to allow analysis under low memory conditions.
}.items():
  if sName not in dxBugIdConfig:
    dxBugIdConfig[sName] = xValue;
