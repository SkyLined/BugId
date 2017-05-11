import codecs, ctypes, ctypes.wintypes, locale, sys, threading;
#oStdOut = codecs.getwriter(locale.getpreferredencoding())(sys.stdout, "replace");

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12
NORMAL_COLOR = 0x7;

class cConsole(object):
  def __init__(oConsole):
    oConsole.oLock = threading.Lock();
    oConsole.uLastLineLength = 0;
    oConsole.uStdOutHandle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE);

  def __fSetColor(oConsole, uColor):
    for x in xrange(10):
      if ctypes.windll.kernel32.SetConsoleTextAttribute(oConsole.uStdOutHandle, uColor) != 0:
        uError = 0;
        break;
      uError = ctypes.windll.kernel32.GetLastError();
      if uError != 6:
        break;
    if uError != 0:
      raise WindowsError("SetConsoleTextAttribute(%d, %d) => Error %08X" % (oConsole.uStdOutHandle, uColor, uError));
  
  def __fWriteOutput(oConsole, sMessage):
    dwCharsWritten = ctypes.wintypes.DWORD(0);
    while sMessage:
      uCharsToWrite = min(len(sMessage), 10000);
      if isinstance(sMessage, unicode):
        fWriteConsole = ctypes.windll.kernel32.WriteConsoleW;
      else:
        fWriteConsole = ctypes.windll.kernel32.WriteConsoleA;
      if fWriteConsole(oConsole.uStdOutHandle, sMessage[:uCharsToWrite], uCharsToWrite, ctypes.byref(dwCharsWritten), None) == 0:
        uError = ctypes.windll.kernel32.GetLastError();
        raise WindowsError("WriteConsoleW(%d, '...', %d, ..., NULL) => Error %08X" % (oConsole.uStdOutHandle, uCharsToWrite, uError));
      sMessage = sMessage[dwCharsWritten.value:];

  def __fOutputHelper(oConsole, axCharsAndColors, bNewLine):
    global goLock, guLastLineLength;
    oConsole.oLock.acquire();
    try:
      # Go to the start of the current line if needed
      if oConsole.uLastLineLength:
        oConsole.__fWriteOutput("\r");
      uNewLineLength = 0;
      try:
        for xCharsOrColor in axCharsAndColors:
          if isinstance(xCharsOrColor, int) or isinstance(xCharsOrColor, long):
            if xCharsOrColor == -1: xCharsOrColor = NORMAL_COLOR;
            oConsole.__fSetColor(xCharsOrColor);
          else:
            uNewLineLength += len(xCharsOrColor);
            oConsole.__fWriteOutput(xCharsOrColor);
      finally:
        oConsole.__fSetColor(NORMAL_COLOR);
      if uNewLineLength < oConsole.uLastLineLength:
        oConsole.__fWriteOutput(" " * (oConsole.uLastLineLength - uNewLineLength));
      if bNewLine:
        oConsole.__fWriteOutput("\r\n");
        oConsole.uLastLineLength = 0;
      else:
        oConsole.__fWriteOutput("\r");
        oConsole.uLastLineLength = uNewLineLength;
    finally:
      oConsole.oLock.release();

  def fPrint(oConsole, *axCharsAndColors):
    oConsole.__fOutputHelper(axCharsAndColors, True);

  def fStatus(oConsole, *axCharsAndColors):
    oConsole.__fOutputHelper(axCharsAndColors, False);

oConsole = cConsole();