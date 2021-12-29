from mConsole import oConsole;

from mColorsAndChars import *;

# Helper function to format messages that are specific to a process.
def fOutputMessageForProcess(uHeaderColor, s0HeaderChar, oProcess, bIsMainProcess, *txMessage):
  # oProcess is a mWindowsAPI.cProcess or derivative.
  sIntegrityLevel = "?" if oProcess.uIntegrityLevel is None else (
    str(oProcess.uIntegrityLevel >> 12) +
    ("+" if oProcess.uIntegrityLevel & 0x100 else "")
  );
  axHeader = [
    uHeaderColor, s0HeaderChar or " ",
    COLOR_NORMAL, " ", bIsMainProcess and "Main" or "Sub", " process ",
    COLOR_INFO, str(oProcess.uId), COLOR_NORMAL, "/", COLOR_INFO , "0x%X" % oProcess.uId, 
    COLOR_NORMAL, " (",
      COLOR_INFO, oProcess.sBinaryName,
      COLOR_NORMAL, ", ", COLOR_INFO, oProcess.sISA,
      COLOR_NORMAL, ", IL:", COLOR_INFO, sIntegrityLevel,
    COLOR_NORMAL, "): ",
  ];
  if s0HeaderChar is None:
    # Just blanks for the header (used for multi-line output to reduce redundant output).
    oConsole.fOutput(
      " " * len("".join(s for s in axHeader if isinstance(s, str))),
      *txMessage,
      uConvertTabsToSpaces = 8
    );
  else:
    oConsole.fOutput(
      axHeader,
      *txMessage,
      uConvertTabsToSpaces = 8
    );
