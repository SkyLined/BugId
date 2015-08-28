import os, re, subprocess, threading, time;

from cCrashInfo_fbInitialize import cCrashInfo_fbInitialize;
from cCrashInfo_foDebugAndGetErrorReport import cCrashInfo_foDebugAndGetErrorReport;
from dxCrashInfoConfig import dxCrashInfoConfig;

sOSISA = os.getenv("PROCESSOR_ARCHITEW6432") or os.getenv("PROCESSOR_ARCHITECTURE"); # AMD64 or x86
sMicrosoftSymbolServerURL = "http://msdl.microsoft.com/download/symbols";

class cCrashInfo(object):
  def __init__(oSelf, asApplicationCommandLine, auApplicationProcessIds, sApplicationISA, asSymbolServerURLs, \
      fApplicationStartedCallback, fFatalExceptionDetectedCallback, fFinishedCallback, fInternalExceptionCallback):
    oSelf._fApplicationStartedCallback = fApplicationStartedCallback;
    oSelf._fFatalExceptionDetectedCallback = fFatalExceptionDetectedCallback;
    oSelf._fFinishedCallback = fFinishedCallback;
    oSelf._fInternalExceptionCallback = fInternalExceptionCallback;
    oSelf._sApplicationISA = sApplicationISA;
    uSymbolOptions = sum([
      0x00000001, # SYMOPT_CASE_INSENSITIVE
      0x00000002, # SYMOPT_UNDNAME
      0x00000004, # SYMOPT_DEFERRED_LOAD
#      0x00000020, # SYMOPT_OMAP_FIND_NEAREST
#      0x00000040, # SYMOPT_LOAD_ANYTHING
      0x00000100, # SYMOPT_NO_UNQUALIFIED_LOADS
      0x00000200, # SYMOPT_FAIL_CRITICAL_ERRORS
      0x00000400, # SYMOPT_EXACT_SYMBOLS
      0x00000800, # SYMOPT_ALLOW_ABSOLUTE_SYMBOLS
      0x00010000, # SYMOPT_AUTO_PUBLICS
#      0x00020000, # SYMOPT_NO_IMAGE_SEARCH
      0x00080000, # SYMOPT_NO_PROMPTS
      dxCrashInfoConfig.get("bDebugSymbolLoading", False) and 0x80000000 or 0, # SYMOPT_DEBUG
    ]);
    # For historic reasons, the ISA of the OS is used to determine which ISA version of cdb to use. It is not known if
    # this was originally done to avoid problems with x86 cdb debugging x86 applications of AMD64 windows, or if it
    # doesn't really matter which cdb ISA version is used in this case.
    sCdbBinaryPath = dxCrashInfoConfig.get("sCdbBinaryPath_%s" % sOSISA);
    asCommandLine = [sCdbBinaryPath, "-o", "-sflags", "0x%08X" % uSymbolOptions];
    # -o => debug child processes, -sflags 0xXXXXXXXX => symbol options:
    set_asSymbolServerURLs = set(asSymbolServerURLs + [sMicrosoftSymbolServerURL]);
    sSymbolsPath = ";".join(
      ["cache*%s" % sSymbolCachePath for sSymbolCachePath in dxCrashInfoConfig.get("asSymbolCachePaths", [])] +
      ["srv*%s" % sSymbolServerURL for sSymbolServerURL in set_asSymbolServerURLs]
    );
    asCommandLine.extend(["-y", sSymbolsPath]);
    if asApplicationCommandLine is not None:
      asCommandLine += asApplicationCommandLine;
    oSelf._auProcessIds = [];
    oSelf._auProcessIdsPendingAttach = [];
    if auApplicationProcessIds is not None and len(auApplicationProcessIds) > 0:
      asCommandLine += ["-p", str(auApplicationProcessIds[0])];
      oSelf._auProcessIdsPendingAttach = auApplicationProcessIds;
    
    asCommandLine = [
      (sArg.find(" ") == -1 or sArg[0] == '"')        and sArg               or '"%s"' % sArg.replace('"', '\\"')
      for sArg in asCommandLine
    ];
    if dxCrashInfoConfig.get("bOutputCommandLine", False):
      print "* Starting %s" % " ".join(asCommandLine);
    oSelf.asCdbIO = [];
    oSelf._oErrorReport = None;
    oSelf._bDebuggerTerminated = False;
    oSelf._uLastProcessId = None;
    oSelf._oCdbProcess = subprocess.Popen(args = " ".join(asCommandLine), stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE);
    # Create a thread that interacts with the debugger to debug the application
    oSelf._oCdbDebuggerThread = threading.Thread(target = oSelf._fCdbDebuggerThread);
    oSelf._oCdbDebuggerThread.start();
    # Create a thread that waits for the debugger to terminate and cleans up after it.
    oSelf._oCdbCleanupThread = threading.Thread(target = oSelf._fCdbCleanupThread);
    oSelf._oCdbCleanupThread.start();
    # NB. The above two are separated to make handling exceptions in the code run in the first thread possible without
    # the code running in the second thread interfering. If both were in the same thread, the cleanup code would have
    # to intercept exceptions from the debug code to make sure the cleanup code is always run. It would need to do the
    # cleanup before throwing the original exception again to make sure the exception is visible to the user. This is
    # complex and any exception thrown in the cleanup code would prevent the original exception from the debug code
    # from getting thrown, potentially hiding the root cause of all these exceptions. This has happened before, hence
    # the two threads solution.
  
  def __del__(oSelf):
    # Check to make sure the debugger process is not running
    oProcess = oSelf._oCdbProcess;
    if oProcess is not None and oProcess.poll() == None:
        print "*** INTERNAL ERROR: CrashInfo was not stopped, the cdb process is still running.";
  
  def fStop(oSelf):
    oSelf._bDebuggerTerminated = True;
    oSelf._oCdbProcess.terminate();
    oSelf._oCdbDebuggerThread.join();
    oSelf._oCdbCleanupThread.join();
  
  def _fCdbDebuggerThread(oSelf):
    try:
      if cCrashInfo_fbInitialize(oSelf):
        oSelf._fApplicationStartedCallback();
        oSelf._oErrorReport = cCrashInfo_foDebugAndGetErrorReport(oSelf);
    except Exception, oException:
      oSelf._fInternalExceptionCallback(oException);
      oSelf._bDebuggerTerminated = True;
      oSelf._oCdbProcess.terminate();
      raise;
  
  def _fCdbCleanupThread(oSelf):
    try:
      # wait for debugger thread to terminate.
      oSelf._oCdbDebuggerThread.join();
      # wait for debugger to terminate.
      oSelf._oCdbProcess.wait();
      # wait for any processes that were being debugged to terminate
      sTasklistBinaryPath = os.path.join(os.getenv("WinDir"), "System32", "tasklist.exe");
      oSelf.asTest = [];
      # The last process that terminated was open when cdb reported it and may not have been closed by the OS yet.
      # It needs to be added to the list of processes that need to terminate before debugging is truely finished.
      if oSelf._uLastProcessId is not None:
        oSelf._auProcessIds.append(oSelf._uLastProcessId);
      while oSelf._auProcessIds:
        uProcessId = oSelf._auProcessIds.pop();
        while 1:
          sCommand = '%s /FI "PID eq %d" /NH /FO CSV' % (sTasklistBinaryPath, uProcessId);
          oTaskListProcess = subprocess.Popen(args=sCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE);
          sStdOut, sStdErr = oTaskListProcess.communicate(input=None);
          oTaskListProcess.stdout.close();
          oTaskListProcess.stderr.close();
          oTaskListProcess.terminate();
          assert not sStdErr, "Error running tasklist.exe: %s" % repr(sStdErr);
          if sStdOut != "INFO: No tasks are running which match the specified criteria.\r\n":
            time.sleep(0.1);
          else:
            break;
      # report that we're finished.
      oSelf._fFinishedCallback(oSelf._oErrorReport);
    except Exception, oException:
      oSelf._fInternalExceptionCallback(oException);
      raise;
  
  def _fasReadOutput(oSelf):
    # Read cdb output until an input prompt is detected, or cdb terminates.
    # This is a bit more complex than one might expect because I attempted to make it work with noizy symbol loading.
    # This may interject messages at any point during command execution, which are not part of the commands output and
    # have to be remove to make parsing of the output possible. Unfortuntely, it appears to be too complex to be
    # worth the effort. I've left what i did in here in case I want to try to finish it at some point.
    sLine = "";
    sCleanedLine = "";
    asCleanedLines = [];
    bNextLineIsSymbolLoaderMessage = False;
    while 1:
      sChar = oSelf._oCdbProcess.stdout.read(1);
      if sChar == "\r":
        pass; # ignored.
      elif sChar in ["\n", ""]:
        if dxCrashInfoConfig.get("bOutputIO", False) and sChar in ["\n", ""]:
          print "cdb>%s" % repr(sLine)[1:-1];
        oSelf.asCdbIO.append(sLine);
        sLine = "";
        if sCleanedLine:
          oLineEndsWithWarning = re.match(r"^(.*)\*\*\* WARNING: Unable to verify checksum for .*$", sCleanedLine);
          if oLineEndsWithWarning:
            # Sample output:
            # 
            # |00000073`ce10fda0  00007ff7`cf312200*** WARNING: Unable to verify checksum for CppException_x64.exe
            # | CppException_x64!cException::`vftable'
            # The warning and a "\r\n" appear in the middle of a line od output and need to be removed. The interrupted
            # output continues on the next line.
            sCleanedLine = oLineEndsWithWarning.group(1);
          else:
            oSymbolLoaderMessageMatch = re.match(r"^(?:%s)$" % "|".join([
              r"SYMSRV: .+",
              r"\s*\x08+\s+(?:copied\s*|\d+ percentSYMSRV: .+)",
              r"DBGHELP: .+?( \- (?:private|public) symbols(?: & lines)?)?\s*",
              r"\*\*\* ERROR: Module load completed but symbols could not be loaded for .*$",
             ]), sCleanedLine);
            if oSymbolLoaderMessageMatch:
              # Sample output:
              # |SYMSRV:  c:\symbols\chakra.pdb\5249D6A2684341B79F239B9E6150169C1\chakra.pdb not found
              # |DBGHELP: \\server\symbols\chakra.pdb\5249D6A2684341B79F239B9E6150169C1\chakra.pdb cached to c:\symbols\chakra.pdb\5249D6A2684341B79F239B9E6150169C1\chakra.pdb
              # |DBGHELP: chakra - public symbols  
              # |        c:\symbols\chakra.pdb\5249D6A2684341B79F239B9E6150169C1\chakra.pdb
              # |*** ERROR: Module load completed but symbols could not be loaded for C:\Windows\System32\Macromed\Flash\Flash.ocx
              bNextLineIsSymbolLoaderMessage = oSymbolLoaderMessageMatch.group(1) is not None;
            elif bNextLineIsSymbolLoaderMessage:
              bNextLineIsSymbolLoaderMessage = False;
            else:
              asCleanedLines.append(sCleanedLine);
            sCleanedLine = "";
        if sChar == "":
          break;
      else:
        sLine += sChar;
        sCleanedLine += sChar;
        # Detect the prompt.
        oPromptMatch = re.match("^\d+:\d+(:x86)?> $", sCleanedLine);
        if oPromptMatch:
          if dxCrashInfoConfig.get("bOutputIO", False):
            print "cdb>%s" % repr(sLine)[1:-1];
          oSelf.asCdbIO.append(sCleanedLine);
          return asCleanedLines;
    # Cdb stdout was closed: the process is terminating.
    assert oSelf._bDebuggerTerminated or len(oSelf._auProcessIds) == 0, \
        "Cdb terminated unexpectedly! Last output:\r\n%s" % "\r\n".join(oSelf.asCdbIO[-20:]);
    return None;
   
  def _fasSendCommandAndReadOutput(oSelf, sCommand):
    if dxCrashInfoConfig.get("bOutputIO", False) or dxCrashInfoConfig.get("bOutputCommands", False):
      print "cdb<%s" % repr(sCommand)[1:-1];
    oSelf.asCdbIO[-1] += sCommand;
    try:
      oSelf._oCdbProcess.stdin.write("%s\r\n" % sCommand);
    except Exception, oException:
      assert oSelf._bDebuggerTerminated or len(oSelf._auProcessIds) == 0, \
          "Cdb terminated unexpectedly! Last output:\r\n%s" % "\r\n".join(oSelf.asCdbIO[-20:]);
      return None;
    asOutput = oSelf._fasReadOutput();
    # Detect obvious errors executing the command. (this will not catch everything, but does help development)
    assert asOutput is None or len(asOutput) != 1 or not re.match(r"^\s*\^ .*$", asOutput[0]), \
        "There was a problem executing the command %s: %s" % (repr(sCommand), repr(asOutput));
    return asOutput;
