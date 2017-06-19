import codecs, ctypes, ctypes.wintypes, locale, sys, threading;
#oStdOut = codecs.getwriter(locale.getpreferredencoding())(sys.stdout, "replace");

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12
NORMAL_COLOR = 0x7;

# Non-unicode strings are assumed to be CP437. We have an indexed table to
# convert CP437 to unicode (index range 0-255 => unicode char) and a dict to
# convert Unicode to CP437 (unicode char => CP437 char). These are used by the
# fsuCP437_to_Unicode and fsUnicode_to_CP437 functions respectively.
asuCP437_to_Unicode = [isinstance(x, str) and unicode(x) or unichr(x) for x in [
  0,      9786,   9787,   9829,   9830,   9827,   9824,   8226,
  9688,   9675,   9689,   9794,   9792,   9834,   9835,   9788,
  9658,   9668,   8597,   8252,   182,    167,    9644,   8616,
  8593,   8595,   8594,   8592,   8735,   8596,   9650,   9660,
  " ",    "!",    '"',    "#",    "$",    "%",    "&",    "'",
  "(",    ")",    "*",    "+",    ",",    "-",    ".",    "/",
  "0",    "1",    "2",    "3",    "4",    "5",    "6",    "7",
  "8",    "9",    ":",    ";",    "<",    "=",    ">",    "?",
  "@",    "A",    "B",    "C",    "D",    "E",    "F",    "G",
  "H",    "I",    "J",    "K",    "L",    "M",    "N",    "O",
  "P",    "Q",    "R",    "S",    "T",    "U",    "V",    "W",
  "X",    "Y",    "Z",    "[",    "\\",   "]",    "^",    "_",
  "`",    "a",    "b",    "c",    "d",    "e",    "f",    "g",
  "h",    "i",    "j",    "k",    "l",    "m",    "n",    "o",
  "p",    "q",    "r",    "s",    "t",    "u",    "v",    "w",
  "x",    "y",    "z",    "{",    "|",    "}",    "~",    8962,
  199,    252,    233,    226,    228,    224,    229,    231,
  234,    235,    232,    239,    238,    236,    196,    197,
  201,    230,    198,    244,    246,    242,    251,    249,
  255,    214,    220,    162,    163,    165,    8359,   402,
  225,    237,    243,    250,    241,    209,    170,    186,
  191,    8976,   172,    189,    188,    161,    171,    187,
  9617,   9618,   9619,   9474,   9508,   9569,   9570,   9558,
  9557,   9571,   9553,   9559,   9565,   9564,   9563,   9488,
  9492,   9524,   9516,   9500,   9472,   9532,   9566,   9567,
  9562,   9556,   9577,   9574,   9568,   9552,   9580,   9575,
  9576,   9572,   9573,   9561,   9560,   9554,   9555,   9579,
  9578,   9496,   9484,   9608,   9604,   9612,   9616,   9600,
  945,    946,    915,    960,    931,    963,    956,    964,
  934,    920,    937,    948,    8734,   966,    949,    8745,
  8801,   177,    8805,   8804,   8992,   8993,   247,    8776,
  176,    8729,   183,    8730,   8319,   178,    9632,   160,
]];
dsUnicode_to_CP437 = {};
for uCP437 in xrange(0x100):
  suUnicode = asuCP437_to_Unicode[uCP437];
  dsUnicode_to_CP437[suUnicode] = chr(uCP437);

def fsuCP437_to_Unicode(sCP437):
  return u"".join([asuCP437_to_Unicode[ord(sChar)] for sChar in sCP437]);

def fsUnicode_to_CP437(suUnicode):
  return "".join([dsUnicode_to_CP437.get(suChar, "?") for suChar in suUnicode]);

class cConsole(object):
  def __init__(oConsole):
    oConsole.oLock = threading.Lock();
    oConsole.uLastLineLength = 0;
    oConsole.hStdOut = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE);
    dwMode = ctypes.wintypes.DWORD(0);
    oConsole.bStdOutIsConsole = ctypes.windll.kernel32.GetConsoleMode(oConsole.hStdOut, ctypes.byref(dwMode));
    oConsole.bByteOrderMarkWritten = False;

  def __fSetColor(oConsole, uColor):
    assert oConsole.bStdOutIsConsole, \
        "Cannot set colors when output is redirected";
    assert uColor in xrange(0, 0x100), \
        "You cannot use color 0x%X; maybe you are trying to print a number without converting it to a string?" % uColor;
    assert ctypes.windll.kernel32.SetConsoleTextAttribute(oConsole.hStdOut, uColor), \
        "SetConsoleTextAttribute(%d, %d) => Error %08X" % \
        (oConsole.hStdOut, uColor, ctypes.windll.kernel32.GetLastError());
  
  def __fWriteOutput(oConsole, sMessage):
    dwCharsWritten = ctypes.wintypes.DWORD(0);
    if oConsole.bStdOutIsConsole:
      sWriteFunctionName = "WriteConsoleW";
      if isinstance(sMessage, str):
        sMessage = fsuCP437_to_Unicode(sMessage); # Convert CP437 to Unicode
    else:
      sWriteFunctionName = "WriteFile";
      if isinstance(sMessage, unicode):
        sMessage = fsUnicode_to_CP437(sMessage); # Convert Unicode to CP437
    fbWriteFunction = getattr(ctypes.windll.kernel32, sWriteFunctionName);
    while sMessage:
      uCharsToWrite = min(len(sMessage), 10000);
      assert fbWriteFunction(oConsole.hStdOut, sMessage[:uCharsToWrite], uCharsToWrite, ctypes.byref(dwCharsWritten), None), \
          "%s(%d, '...', %d, ..., NULL) => Error %08X" % \
          (sWriteFunctionName, oConsole.hStdOut, uCharsToWrite, ctypes.windll.kernel32.GetLastError());
      sMessage = sMessage[dwCharsWritten.value:];

  def __fOutputHelper(oConsole, axCharsAndColors, bNewLine):
    global goLock, guLastLineLength;
    oConsole.oLock.acquire();
    try:
      # Go to the start of the current line if needed
      if oConsole.uLastLineLength:
        oConsole.__fWriteOutput(oConsole.bStdOutIsConsole and u"\r" or "\r");
      bColorWasSet = False;
      uNewLineLength = 0;
      try:
        for xCharsOrColor in axCharsAndColors:
          if isinstance(xCharsOrColor, int) or isinstance(xCharsOrColor, long):
            if oConsole.bStdOutIsConsole: # If output is redirected, colors will not be set, so don't try
              if xCharsOrColor == -1: xCharsOrColor = NORMAL_COLOR;
              oConsole.__fSetColor(xCharsOrColor);
              bColorWasSet = True;
          else:
            assert isinstance(xCharsOrColor, str) or isinstance(xCharsOrColor, unicode), \
                "You cannot print %s (type = %s) directly; it must be converted to a string" % (repr(xCharsOrColor), xCharsOrColor.__class__.__name__);
            uNewLineLength += len(xCharsOrColor);
            oConsole.__fWriteOutput(xCharsOrColor);
      finally:
        if bColorWasSet:
          oConsole.__fSetColor(NORMAL_COLOR);
      if uNewLineLength < oConsole.uLastLineLength:
        oConsole.__fWriteOutput(u" " * (oConsole.uLastLineLength - uNewLineLength));
      if bNewLine:
        oConsole.__fWriteOutput(oConsole.bStdOutIsConsole and u"\r\n" or "\r\n");
        oConsole.uLastLineLength = 0;
      else:
        oConsole.__fWriteOutput(oConsole.bStdOutIsConsole and u"\r" or "\r");
        oConsole.uLastLineLength = uNewLineLength;
    finally:
      oConsole.oLock.release();

  def fPrint(oConsole, *axCharsAndColors):
    oConsole.__fOutputHelper(axCharsAndColors, True);

  def fStatus(oConsole, *axCharsAndColors):
    # If output is redirected, do not output status messages
    if oConsole.bStdOutIsConsole:
      oConsole.__fOutputHelper(axCharsAndColors, False);

oConsole = cConsole();