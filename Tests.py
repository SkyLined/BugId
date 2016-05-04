import os, re, sys, threading;
from dxConfig import dxConfig;
sBaseFolderPath = os.path.dirname(__file__);
sys.path.extend([os.path.join(sBaseFolderPath, x) for x in ["src", "modules"]]);
from cBugId import cBugId;
from sOSISA import sOSISA;
from cBugReport_foAnalyzeException_STATUS_ACCESS_VIOLATION import ddtsDetails_uAddress_sISA;
from fsCreateFileName import fsCreateFileName;

bDebugStartFinish = False;
bDebugIO = False;
uSequentialTests = 32; # >32 will probably not work.

dxBugIdConfig = dxConfig["BugId"];
dxBugIdConfig["bOutputStdIn"] = \
    dxBugIdConfig["bOutputStdOut"] = \
    dxBugIdConfig["bOutputStdErr"] = bDebugIO;
dxBugIdConfig["bOutputProcesses"] = False;
dxBugIdConfig["uReserveRAM"] = 1024; # Simply test if reserving RAM works, not actually reserve any useful amount.

asTestISAs = [sOSISA];
if sOSISA == "x64":
  asTestISAs.append("x86");

sBaseFolderPath = os.path.dirname(__file__);
dsBinaries_by_sISA = {
  "x86": os.path.join(sBaseFolderPath, r"Tests\bin\Tests_x86.exe"),
  "x64": os.path.join(sBaseFolderPath, r"Tests\bin\Tests_x64.exe"),
};

bFailed = False;
oOutputLock = threading.Lock();
# If you see weird exceptions, try lowering the number of parallel tests:
oConcurrentTestsSemaphore = threading.Semaphore(uSequentialTests);
class cTest(object):
  def __init__(oTest, sISA, asCommandLineArguments, sExpectedBugTypeId):
    oTest.sISA = sISA;
    oTest.asCommandLineArguments = asCommandLineArguments;
    oTest.sExpectedBugTypeId = sExpectedBugTypeId;
    oTest.bInternalException = False;
    oTest.bHasOutputLock = False;
  
  def __str__(oTest):
    return "%s =%s=> %s" % (" ".join(oTest.asCommandLineArguments), oTest.sISA, oTest.sExpectedBugTypeId);
  
  def fRun(oTest):
    global bFailed, oOutputLock;
    oConcurrentTestsSemaphore.acquire();
    sBinary = dsBinaries_by_sISA[oTest.sISA];
    asApplicationCommandLine = [sBinary] + oTest.asCommandLineArguments;
    if bDebugStartFinish:
      oOutputLock and oOutputLock.acquire();
      oTest.bHasOutputLock = True;
      print "@ Started %s" % oTest;
      oOutputLock and oOutputLock.release();
      oTest.bHasOutputLock = False;
    try:
      oTest.oBugId = cBugId(
        asApplicationCommandLine = asApplicationCommandLine,
        asSymbolServerURLs = ["http://msdl.microsoft.com/download/symbols"],
        bGetDetailsHTML = dxConfig["bSaveTestReports"],
        fFinishedCallback = oTest.fFinishedHandler,
        fInternalExceptionCallback = oTest.fInternalExceptionHandler,
      );
    except Exception, oException:
      if not bFailed:
        bFailed = True;
        oOutputLock and oOutputLock.acquire();
        oTest.bHasOutputLock = True;
        print "- %s" % oTest;
        print "    => Exception: %s" % oException;
        oOutputLock and oOutputLock.release();
        oTest.bHasOutputLock = False;
  
  def fWait(oTest):
    hasattr(oTest, "oBugId") and oTest.oBugId.fWait();
  
  def fFinished(oTest):
    if bDebugStartFinish:
      oOutputLock and oOutputLock.acquire();
      oTest.bHasOutputLock = True;
      print "@ Finished %s" % oTest;
      oOutputLock and oOutputLock.release();
      oTest.bHasOutputLock = False;
    oConcurrentTestsSemaphore.release();
  
  def fFinishedHandler(oTest, oBugReport):
    global bFailed, oOutputLock;
    bThisTestFailed = False;
    if not bFailed:
      oOutputLock and oOutputLock.acquire();
      oTest.bHasOutputLock = True;
      if oTest.sExpectedBugTypeId:
        if not oBugReport:
          print "- %s" % oTest;
          print "    => got no bug report";
          bThisTestFailed = bFailed = True;
        elif not oTest.sExpectedBugTypeId == oBugReport.sBugTypeId:
          print "- %s" % oTest;
          print "    => %s (%s)" % (oBugReport.sId, oBugReport.sBugDescription);
          bThisTestFailed = bFailed = True;
        else:
          print "+ %s" % oTest;
      elif oBugReport:
        print "- %s" % oTest;
        print "    => %s (%s)" % (oBugReport.sId, oBugReport.sBugDescription);
        bThisTestFailed = bFailed = True;
      else:
        print "+ %s" % oTest;
      if bThisTestFailed:
        print "    Command line: %s" % " ".join([dsBinaries_by_sISA[oTest.sISA]] + oTest.asCommandLineArguments);
      oOutputLock and oOutputLock.release();
      oTest.bHasOutputLock = False;
      if dxConfig["bSaveTestReports"]:
        sFileNameBase = fsCreateFileName("%s = %s" % (oTest, oBugReport.sId));
        # File name may be too long, keep trying to save it with a shorter name or output an error if that's not possible.
        while len(sFileNameBase) > 0:
          sFilePath = os.path.join(os.path.dirname(__file__), "Test reports", "%s.html" % sFileNameBase);
          try:
            oFile = open(sFilePath, "wb");
          except IOError:
            sFileNameBase = sFileNameBase[:-1];
            continue;
          try:
            oFile.write(oBugReport.sDetailsHTML);
          finally:
            oFile.close();
          break;
        else:
          oOutputLock and oOutputLock.acquire();
          oTest.bHasOutputLock = True;
          print "  - Bug report cannot be saved";
          bFailed = True;
          oOutputLock and oOutputLock.release();
          oTest.bHasOutputLock = False;
    oTest.fFinished();
    oTest.bHandlingResult = False;
  
  def fInternalExceptionHandler(oTest, oException):
    global bFailed;
    oTest.fFinished();
    if not bFailed:
      # Exception in fFinishedHandler can cause this function to be executed with lock still in place.
      if not oTest.bHasOutputLock:
        oOutputLock and oOutputLock.acquire();
        oTest.bHasOutputLock = True;
      bFailed = True;
      print "@ Exception in %s: %s" % (oTest, oException);
      oOutputLock and oOutputLock.release();
      oTest.bHasOutputLock = False;
      raise;

if __name__ == "__main__":
  if sys.argv[1:2] == ["--save-reports"]:
    dxConfig["bSaveTestReports"] = True;
  
  aoTests = [];
  for sISA in asTestISAs:
    aoTests.append(cTest(sISA, [], None)); # No exceptions, just a clean program exit.
    sMinusOne = {"x86": "FFFFFFFF", "x64": "FFFFFFFFFFFFFFFF"}[sISA];
    sMinusTwo = {"x86": "FFFFFFFE", "x64": "FFFFFFFFFFFFFFFE"}[sISA];
    aoTests.append(cTest(sISA, ["AccessViolation", "READ", "1"], "AVR:NULL+N"));
    aoTests.append(cTest(sISA, ["AccessViolation", "READ", "2"], "AVR:NULL+2*N"));
    aoTests.append(cTest(sISA, ["AccessViolation", "READ", "3"], "AVR:NULL+N"));
    aoTests.append(cTest(sISA, ["AccessViolation", "READ", "4"], "AVR:NULL+4*N"));
    aoTests.append(cTest(sISA, ["AccessViolation", "READ", "5"], "AVR:NULL+N"));
    aoTests.append(cTest(sISA, ["AccessViolation", "READ", sMinusOne], "AVR:NULL-N"));
    aoTests.append(cTest(sISA, ["AccessViolation", "READ", sMinusTwo], "AVR:NULL-2*N"));
    aoTests.append(cTest(sISA, ["Breakpoint"], "Breakpoint"));
    aoTests.append(cTest(sISA, ["C++"], "C++:cException"));
    aoTests.append(cTest(sISA, ["IntegerDivideByZero"], "IntegerDivideByZero"));
    aoTests.append(cTest(sISA, ["Numbered", "41414141", "42424242"], "0x41414141"));
    # Specific test to check for ntdll!RaiseException exception address being off-by-one from the stack address:
    aoTests.append(cTest(sISA, ["Numbered", "80000003", "1"], "Breakpoint"));
    aoTests.append(cTest(sISA, ["IllegalInstruction"], "IllegalInstruction"));
    aoTests.append(cTest(sISA, ["PrivilegedInstruction"], "PrivilegedInstruction"));
    aoTests.append(cTest(sISA, ["StackExhaustion"], "StackExhaustion"));
    aoTests.append(cTest(sISA, ["RecursiveCall"], "RecursiveCall"));
    aoTests.append(cTest(sISA, ["StaticBufferOverrun10", "Write", "20"], "FailFast2:StackCookie"));
    aoTests.append(cTest(sISA, ["OutOfBounds", "Heap", "Write", "c", "-1"], "HeapCorrupt"));  # Write the byte at offset -1 from the start of the buffer.
    aoTests.append(cTest(sISA, ["OutOfBounds", "Heap", "Write", "c", "d"], "HeapCorrupt"));   # Write the byte at offset 0 from the end of the buffer.
    if sISA not in ["x86"]:
      # x86 test results in "0BA2 FailFast2:AppExit Tests_x86.exe!abort (A critical issue was detected (code C0000409, fail fast code 7: FAST_FAIL_FATAL_APP_EXIT))"
      aoTests.append(cTest(sISA, ["PureCall"], "PureCall"));
      # Page heap does not appear to work for x86 tests on x64 platform.
      aoTests.append(cTest(sISA, ["UseAfterFree", "Read", "20", "0"], "AVR:Free"));
      aoTests.append(cTest(sISA, ["UseAfterFree", "Write", "20", "0"], "AVW:Free"));
      aoTests.append(cTest(sISA, ["BufferOverrun", "Heap", "Read", "20", "4"], "AVR:OOB+4*N"));
      aoTests.append(cTest(sISA, ["BufferOverrun", "Heap", "Write", "20", "4"], "AVW:OOB+4*N"));
      aoTests.append(cTest(sISA, ["OutOfBounds", "Heap", "Read", "c", "10"], "AVR:OOB+4*N"));   # Read byte at offset 4 from the end of the memory block
      aoTests.append(cTest(sISA, ["OutOfBounds", "Heap", "Read", "c", "11"], "AVR:OOB+N"));     # Read byte at offset 5 from the end of the memory block
      aoTests.append(cTest(sISA, ["OutOfBounds", "Heap", "Read", "c", "12"], "AVR:OOB+2*N"));   # Read byte at offset 6 from the end of the memory block
      aoTests.append(cTest(sISA, ["OutOfBounds", "Heap", "Read", "c", "13"], "AVR:OOB+N"));     # Read byte at offset 7 from the end of the memory block
      aoTests.append(cTest(sISA, ["OutOfBounds", "Heap", "Write", "c", "10"], "AVW:OOB+4*N"));  # Write byte at offset 4 from the end of the memory block
      aoTests.append(cTest(sISA, ["OutOfBounds", "Heap", "Write", "c", "11"], "AVW:OOB+N"));    # Write byte at offset 5 from the end of the memory block
      aoTests.append(cTest(sISA, ["OutOfBounds", "Heap", "Write", "c", "12"], "AVW:OOB+2*N"));  # Write byte at offset 6 from the end of the memory block
      aoTests.append(cTest(sISA, ["OutOfBounds", "Heap", "Write", "c", "13"], "AVW:OOB+N"));    # Write byte at offset 7 from the end of the memory block
    if False:
      # This does not appear to work at all. TODO: fix this.
      aoTests.append(cTest(sISA, ["BufferOverrun", "Stack", "Write", "20", "1000"], "AVW:OOB"));
    
    for uBaseAddress in [(1 << 31) - 1, (1 << 31), (1 << 32), (1 << 47) - 1, (1 << 47), (1 << 63) - 1, (1 << 63)]:
      if uBaseAddress < (1 << 32) or (sISA == "x64" and uBaseAddress < (1 << 47)):
        aoTests.extend([
          cTest(sISA, ["AccessViolation", "Read", "%X" % uBaseAddress], "AVR:Arbitrary"),
          cTest(sISA, ["AccessViolation", "Write", "%X" % uBaseAddress], "AVW:Arbitrary"),
          cTest(sISA, ["AccessViolation", "Call", "%X" % uBaseAddress], "AVE:Arbitrary"),
          cTest(sISA, ["AccessViolation", "Jump", "%X" % uBaseAddress], "AVE:Arbitrary"),
        ]);
      elif sISA == "x64":
        # Above 0x7FFFFFFFFFFF the exception record no longer contains the correct address.
        aoTests.extend([
          cTest(sISA, ["AccessViolation", "Read", "%X" % uBaseAddress], "AV?:Arbitrary"),
          cTest(sISA, ["AccessViolation", "Write", "%X" % uBaseAddress], "AV?:Arbitrary"),
          cTest(sISA, ["AccessViolation", "Call", "%X" % uBaseAddress], "AV?:Arbitrary"),
          cTest(sISA, ["AccessViolation", "Jump", "%X" % uBaseAddress], "AV?:Arbitrary"),
        ]);
  
  for (sISA, dtsDetails_uAddress) in ddtsDetails_uAddress_sISA.items():
    for (uBaseAddress, (sAddressId, sAddressDescription, sSecurityImpact)) in dtsDetails_uAddress.items():
      if uBaseAddress < (1 << 32) or (sISA == "x64" and uBaseAddress < (1 << 47)):
        aoTests.append(cTest(sISA, ["AccessViolation", "Read", "%X" % uBaseAddress], "AVR:%s" % sAddressId));
        aoTests.append(cTest(sISA, ["AccessViolation", "Write", "%X" % uBaseAddress], "AVW:%s" % sAddressId));
        aoTests.append(cTest(sISA, ["AccessViolation", "Call", "%X" % uBaseAddress], "AVE:%s" % sAddressId));
        aoTests.append(cTest(sISA, ["AccessViolation", "Jump", "%X" % uBaseAddress], "AVE:%s" % sAddressId));
      elif sISA == "x64":
        aoTests.append(cTest(sISA, ["AccessViolation", "Read", "%X" % uBaseAddress], "AV?:%s" % sAddressId));
        aoTests.append(cTest(sISA, ["AccessViolation", "Write", "%X" % uBaseAddress], "AV?:%s" % sAddressId));
        aoTests.append(cTest(sISA, ["AccessViolation", "Call", "%X" % uBaseAddress], "AV?:%s" % sAddressId));
        aoTests.append(cTest(sISA, ["AccessViolation", "Jump", "%X" % uBaseAddress], "AV?:%s" % sAddressId));
  
  print "* Starting tests...";
  for oTest in aoTests:
    if bFailed:
      break;
    oTest.fRun();
  for oTest in aoTests:
    oTest.fWait();
  
  oOutputLock.acquire();
  if bFailed:
    print "* Tests failed."
    sys.exit(1);
  else:
    print "* All tests passed!"
    sys.exit(0);
