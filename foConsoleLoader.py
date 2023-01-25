import threading;
def fsOutputArgumentsToString(txArguments):
  sOutput = "";
  axArguments = list(txArguments);
  while axArguments:
    xArgument = axArguments.pop(0);
    if isinstance(xArgument, str):
      sOutput += xArgument;
    elif isinstance(xArgument, bytes):
      sOutput += xArgument.decode('ibm437').translate({
        0x01: "\u263A", 0x02: "\u263B", 0x03: "\u2665", 0x04: "\u2666",
        0x05: "\u2663", 0x06: "\u2660", 0x07: "\u2022", 0x08: "\u25D8",
        0x09: "\u25CB", 0x0a: "\u25D9", 0x0b: "\u2642", 0x0c: "\u2640",
        0x0d: "\u266A", 0x0e: "\u266B", 0x0f: "\u263C", 0x10: "\u25BA",
        0x11: "\u25C4", 0x12: "\u2195", 0x13: "\u203C", 0x14: "\u00B6",
        0x15: "\u00A7", 0x16: "\u25AC", 0x17: "\u21A8", 0x18: "\u2191", 
        0x19: "\u2193", 0x1a: "\u2192", 0x1b: "\u2190", 0x1c: "\u221F",
        0x1d: "\u2194", 0x1e: "\u25B2", 0x1f: "\u25BC", 0x7f: "\u2302",
    });
    elif isinstance(xArgument, list):
      axArguments.insert(0, xArgument);
    else:
      assert isinstance(xArgument, int), \
          "Cannot output %s in %s" % (repr(xArgument), repr(txArguments));
  return sOutput;
class oConsoleStandIn(object):
  uCurrentLineLength = 0;
  uCurrentColor = 0xFF07;
  uDefaultColor = 0;
  uDefaultBarColor = 0;
  uDefaultProgressColor = 0;
  uDefaultSubProgressColor = 0;
  uWindowWidth = 80;
  uWidth = 80;
  oLock = threading.Lock();
  @classmethod
  def fOutputCodepage437ToStdOut(cClass):
    pass;
  @classmethod
  def fbCopyOutputToFilePath(cClass, sFilePath, **dxArguments):
    assert not dxArguments.get("bThrowErrors", True), \
        "Not implemented";
    return False;
  @classmethod
  def fLock(cClass):
    cClass.oLock.acquire();
  @classmethod
  def fUnlock(cClass):
    cClass.oLock.release();
  @classmethod
  def fCleanup(cClass):
    print("\r".ljust(cClass.uCurrentLineLength) + "\r", sep="", end="", flush=True);
    cClass.uCurrentLineLength = 0;
  @classmethod
  def fOutput(cClass, *txArguments, **dxArguments):
    sOutput = fsOutputArgumentsToString(txArguments);
    print("\r" + sOutput.ljust(cClass.uCurrentLineLength), sep="", flush=True);
    cClass.uCurrentLineLength = 0;
  @classmethod
  def fStatus(cClass, *txArguments, **dxArguments):
    sOutput = fsOutputArgumentsToString(txArguments);
    print("\r" + sOutput.ljust(cClass.uCurrentLineLength), sep="", end="", flush=True);
    cClass.uCurrentLineLength = len(sOutput);
  @classmethod
  def fProgressBar(cClass, nProgress, sMessage = "", **dxArguments):
    cClass.fStatus(int(100 * nProgress), "%", sMessage);
  @classmethod
  def fSetTitele(cClass, sTitle):
    pass;
  @classmethod
  def fHideWindow(cClass):
    pass;
  @classmethod
  def fShowWindow(cClass, bActivate = False):
    pass;
  @classmethod
  def fMinimizeWindow(cClass):
    pass;
  @classmethod
  def fMaximizeWindow(cClass):
    pass;
  @classmethod
  def fRestoreWindow(cClass):
    pass;

go0Console = None;
def foConsoleLoader():
  global go0Console;
  if go0Console is None:
    try:
      from mConsole import oConsole;
    except Exception as oException:
      print("Using stand-in oConsole (%s)!" % oException);
      goConsole = oConsoleStandIn;
    else:
      goConsole = oConsole;
  return goConsole;