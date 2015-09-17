import os, re, sys, threading;
from cCrashInfo import cCrashInfo;
from dxConfig import dxConfig;
dxConfig.setdefault("CrashInfo", {})["bOutputProcesses"] = False;
bDebug = False;
if bDebug:
  dxConfig.setdefault("CrashInfo", {})["bOutputIO"] = True;

sOSISA = os.getenv("PROCESSOR_ARCHITEW6432") or os.getenv("PROCESSOR_ARCHITECTURE"); # "x86" or "AMD64"
if sOSISA == "AMD64":
  asTestISAs = ["x86", "AMD64"];
else:
  asTestISAs = ["x86"];

sBaseFolderPath = os.path.dirname(__file__);
dsBinaries_by_sISA = {
  "x86": os.path.join(sBaseFolderPath, r"Tests\Tests_x86.exe"),
  "AMD64": os.path.join(sBaseFolderPath, r"Tests\Tests_x64.exe"),
};

bFailed = False;
oOutputLock = threading.Lock();
oConcurrentTestsSemaphore = threading.Semaphore(bDebug and 1 or 32);
class cTest(object):
  def __init__(oTest, sISA, asCommandLineArguments, srBugId):
    oTest.sISA = sISA;
    oTest.asCommandLineArguments = asCommandLineArguments;
    oTest.srBugId = srBugId;
    oTest.bInternalException = False;
  
  def __str__(oTest):
    return "%s =%s=> %s" % (" ".join(oTest.asCommandLineArguments), oTest.sISA, oTest.srBugId);
  
  def fRun(oTest):
    oConcurrentTestsSemaphore.acquire();
    sBinary = dsBinaries_by_sISA[oTest.sISA];
    asApplicationCommandLine = [sBinary] + oTest.asCommandLineArguments;
    oCrashInfo = cCrashInfo(
      asApplicationCommandLine = asApplicationCommandLine,
      auApplicationProcessIds = None,
      asSymbolServerURLs = [],
      fApplicationRunningCallback = oTest.fApplicationRunningHandler,
      fExceptionDetectedCallback = oTest.fExceptionDetectedHandler,
      fFinishedCallback = oTest.fFinishedHandler,
      fInternalExceptionCallback = oTest.fInternalExceptionHandler,
    );
  
  def fFinished(oTest):
    oConcurrentTestsSemaphore.release();
  
  def fApplicationRunningHandler(oTest):
    pass;
  
  def fExceptionDetectedHandler(oTest, uCode, sDescription):
    pass;
  
  def fFinishedHandler(oTest, oErrorReport):
    global bFailed;
    if not bFailed:
      oOutputLock.acquire();
      if oTest.srBugId:
        if not oErrorReport:
          bFailed = True;
          print "- %s" % oTest;
          print "    => got no error";
        elif not re.match("^([0-9A-F_]{2})+ (%s) .+\.exe!.*$" % re.escape(oTest.srBugId), oErrorReport.sId):
          bFailed = True;
          print "- %s" % oTest;
          print "    => %s (%s)" % (oErrorReport.sId, oErrorReport.sErrorDescription);
        elif not bFailed:
          print "+ %s" % oTest;
      elif oErrorReport:
        bFailed = True;
        print "- %s" % oTest;
        print "    => %s (%s)" % (oErrorReport.sId, oErrorReport.sErrorDescription);
      elif not bFailed:
        print "+ %s" % oTest;
      oOutputLock.release();
    if bFailed:
      os._exit(1);
    oTest.fFinished();
  
  def fInternalExceptionHandler(oTest, oException):
    global bFailed;
    bFailed = True;
    oTest.fFinished();

aoTests = [
 cTest("x86", ["AccessViolation", "READ", "1"], "AVR:NULL+X"),
 cTest("AMD64", ["AccessViolation", "READ", "1"], "AVR:NULL+X"),
 cTest("x86", ["AccessViolation", "READ", "FFFFFFFF"], "AVR:NULL-X"),
 cTest("AMD64", ["AccessViolation", "READ", "FFFFFFFFFFFFFFFF"], "AVR:NULL-X"),
 cTest("AMD64", ["PureCall"], "PureCall"), # x86 test not functioning as expected yet
 cTest("AMD64", ["UseAfterFree", "Read", "20", "0"], "AVR:Free"), # x86 test not functioning as expected yet
 cTest("AMD64", ["UseAfterFree", "Write", "20", "0"], "AVW:Free"), # x86 test not functioning as expected yet
 cTest("AMD64", ["OutOfBounds", "Read", "20", "0"], "AVR:OOB"), # x86 test not functioning as expected yet
 cTest("AMD64", ["OutOfBounds", "Write", "20", "0"], "AVW:OOB"), # x86 test not functioning as expected yet
 cTest("AMD64", ["OutOfBounds", "Read", "20", "1"], "AVR:OOB+X"), # x86 test not functioning as expected yet
 cTest("AMD64", ["OutOfBounds", "Write", "20", "1"], "AVW:OOB+X"), # x86 test not functioning as expected yet
];
for sISA in asTestISAs:
  aoTests.append(cTest(sISA, ["Breakpoint"], "Breakpoint"));
  aoTests.append(cTest(sISA, ["C++"], "C++:cException"));
  aoTests.append(cTest(sISA, ["IntegerDivideByZero"], "IntegerDivideByZero"));
  aoTests.append(cTest(sISA, ["Numbered", "41414141", "42424242"], "0x41414141"));
  aoTests.append(cTest(sISA, ["IllegalInstruction"], "IllegalInstruction"));
  aoTests.append(cTest(sISA, ["PrivilegedInstruction"], "PrivilegedInstruction"));
  aoTests.append(cTest(sISA, ["StackExhaustion"], "StackExhaustion"));
  aoTests.append(cTest(sISA, ["RecursiveCall"], "RecursiveCall"));
  
  for uBaseAddress in [(1 << 31) - 1, (1 << 31), (1 << 32), (1 << 47) - 1, (1 << 47), (1 << 63) - 1, (1 << 63)]:
    if uBaseAddress < (1 << 32) or (sISA == "AMD64" and uBaseAddress < (1 << 47)):
      aoTests.extend([
        cTest(sISA, ["AccessViolation", "Read", "%X" % uBaseAddress], "AVR:Arbitrary"),
        cTest(sISA, ["AccessViolation", "Write", "%X" % uBaseAddress], "AVW:Arbitrary"),
        cTest(sISA, ["AccessViolation", "Call", "%X" % uBaseAddress], "AVE:Arbitrary"),
        cTest(sISA, ["AccessViolation", "Jump", "%X" % uBaseAddress], "AVE:Arbitrary"),
      ]);
    elif sISA == "AMD64":
      # Above 0x7FFFFFFFFFFF the exception record no longer contains the correct address.
      aoTests.extend([
        cTest(sISA, ["AccessViolation", "Read", "%X" % uBaseAddress], "AV?:Arbitrary"),
        cTest(sISA, ["AccessViolation", "Write", "%X" % uBaseAddress], "AV?:Arbitrary"),
        cTest(sISA, ["AccessViolation", "Call", "%X" % uBaseAddress], "AV?:Arbitrary"),
        cTest(sISA, ["AccessViolation", "Jump", "%X" % uBaseAddress], "AV?:Arbitrary"),
      ]);

from cCrashInfo.cErrorReport_foSpecialErrorReport_STATUS_ACCESS_VIOLATION import ddtsDetails_uAddress_sISA;
for (sISA, dtsDetails_uAddress) in ddtsDetails_uAddress_sISA.items():
  for (uBaseAddress, (sAddressId, sAddressDescription, sSecurityImpact)) in dtsDetails_uAddress.items():
    if uBaseAddress < (1 << 32) or (sISA == "AMD64" and uBaseAddress < (1 << 47)):
      aoTests.append(cTest(sISA, ["AccessViolation", "Read", "%X" % uBaseAddress], "AVR:%s" % sAddressId));
      aoTests.append(cTest(sISA, ["AccessViolation", "Write", "%X" % uBaseAddress], "AVW:%s" % sAddressId));
      aoTests.append(cTest(sISA, ["AccessViolation", "Call", "%X" % uBaseAddress], "AVE:%s" % sAddressId));
      aoTests.append(cTest(sISA, ["AccessViolation", "Jump", "%X" % uBaseAddress], "AVE:%s" % sAddressId));
    elif sISA == "AMD64":
      aoTests.append(cTest(sISA, ["AccessViolation", "Read", "%X" % uBaseAddress], "AV?:%s" % sAddressId));
      aoTests.append(cTest(sISA, ["AccessViolation", "Write", "%X" % uBaseAddress], "AV?:%s" % sAddressId));
      aoTests.append(cTest(sISA, ["AccessViolation", "Call", "%X" % uBaseAddress], "AV?:%s" % sAddressId));
      aoTests.append(cTest(sISA, ["AccessViolation", "Jump", "%X" % uBaseAddress], "AV?:%s" % sAddressId));

print "* Starting tests...";
for oTest in aoTests:
  if bFailed:
    break;
  oTest.fRun();
