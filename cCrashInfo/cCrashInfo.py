import os, re, subprocess, threading, time;
from cProcess import cProcess;
from cException import cException;
from cErrorReport import cErrorReport;

from dxCrashInfoConfig import dxCrashInfoConfig;

sISA = os.getenv("PROCESSOR_ARCHITEW6432") or os.getenv("PROCESSOR_ARCHITECTURE"); # AMD64 or x86
sCdbBinaryPath = os.path.join(os.path.dirname(__file__), "Debugging Tools for Windows (%s)" % sISA, "cdb.exe");
sMicrosoftSymbolServerURL = "http://msdl.microsoft.com/download/symbols";

asDetectedExceptions = [
  "*", "asrt", "aph", "av", "bpe", "dm", "dz", "eh", "gp", "ii", "iov", "ip",
  "isc", "lsq", "sbo", "sov", "sse", "ssec", "vcpp", "wkd", "wob", "wos",
];
asIgnoredExceptions = [
  "ch", "hc", "ibp", "ld", "ud", "wos",
  # "cpr" and "epr" are missing because they are special-cased in the code, see below
];

class cCrashInfo(object):
  sISA = sISA;
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
#      0x80000000, # SYMOPT_DEBUG # Makes parsing output near impossible :(
      dxCrashInfoConfig.get("bDebugSymbolLoading", False) and 0x80000000 or 0, # SYMOPT_DEBUG
    ]);
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
    if auApplicationProcessIds is not None and len(auApplicationProcessIds) > 0:
      asCommandLine += ["-p", str(auApplicationProcessIds.pop(0))];
      oSelf._auProcessIds = auApplicationProcessIds;
      oSelf._bResumeThreads = True;
    else:
      oSelf._auProcessIds = [];
      oSelf._bResumeThreads = False;
    # Make a list of all the cdb commands that need to be execute to initialize and start the application.
    asInitialCommands = [];
    # if requested, resume all threads in current process.
    asInitialCommands.append(".childdbg 1");
    if oSelf._bResumeThreads: asInitialCommands.append("~*m");
    # if requested, attach to additional processes and optionally resume all threads in those as well.
    for uAttachProcessId in oSelf._auProcessIds:
      asInitialCommands.append(".attach 0n%d;g" % uAttachProcessId);
      asInitialCommands.append(".childdbg 1");
      if oSelf._bResumeThreads:
        asInitialCommands.append("~*m");
    # request second chance debugger break for certain exceptions that indicate the application has a bug.
    for sException in asDetectedExceptions:
      if dxCrashInfoConfig.get("bOutputFirstChanceExceptions", False):
        asInitialCommands.append("sxe %s" % sException);
      else:
        asInitialCommands.append("sxd %s" % sException);
    # ignore certain other exceptions
    for sException in asIgnoredExceptions:
      asInitialCommands.append("sxi %s" % sException);
    # To be able to track which processes are running at any given time while the application being debugged,
    # cpr and epr must be enabled.
    # Also, if epr is disabled the debugger will silently exit when the application terminates.
    # To distinguish this from other unexpected terminations of the debugger, epr must also be enabled.
    asInitialCommands.append("sxe cpr");
    asInitialCommands.append("sxe epr");
    oSelf._asInitialCommands = asInitialCommands;
    
    asCommandLine = [
      (sArg.find(" ") == -1 or sArg[0] == '"')        and sArg               or '"%s"' % sArg.replace('"', '\\"')
      for sArg in asCommandLine
    ];
    if dxCrashInfoConfig.get("bOutputCommandLine", False):
      print ",-- Cdb command line ".ljust(120, "-");
      print "| %s" % asCommandLine[0];
      for sArgument in asCommandLine[1:]:
        print "|   %s" % sArgument;
      print "`".ljust(120, "-");
    oSelf.asCdbIO = [];
    oSelf._oErrorReport = None;
    oSelf._bExpectTermination = False;
    oSelf._oCdbProcess = subprocess.Popen(args = " ".join(asCommandLine), stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE);
    oSelf._oDuringCdbThread = threading.Thread(target = oSelf._fDuringCdbThread);
    oSelf._oDuringCdbThread.start();
    oSelf._oAfterCdbThread = threading.Thread(target = oSelf._fAfterCdbThread);
    oSelf._oAfterCdbThread.start();
  
  def __del__(oSelf):
    # Check to make sure the debugger process is not running
    oProcess = oSelf._oCdbProcess;
    if oProcess is not None and oProcess.poll() == None:
        print "*** INTERNAL ERROR: CrashInfo was not stopped, the cdb process is still running.";
  
  def fStop(oSelf):
    oSelf._bExpectTermination = True;
    # terminate the cdb process
    while oSelf._oCdbProcess.poll() == None:
      oSelf._oCdbProcess.terminate();
      time.sleep(1);
    oSelf._oDuringCdbThread.join();
    oSelf._oAfterCdbThread.join();
  
  def _fAfterCdbThread(oSelf):
    try:
      # wait for cdb to terminate.
      oSelf._oCdbProcess.wait();
      # wait for any processes the were being debugged to terminate
      if oSelf._auProcessIds:
        sTasklistBinaryPath = os.path.join(os.getenv("WinDir"), "System32", "tasklist.exe");
        for uProcessId in oSelf._auProcessIds:
          while 1:
            sCommand = '%s /FI "PID eq %d" /NH /FO CSV' % (sTasklistBinaryPath, uProcessId);
            oTaskListProcess = subprocess.Popen(args=sCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE);
            sStdOut, sStdErr = oTaskListProcess.communicate(input=None);
            assert not sStdErr, "Error running tasklist.exe: %s" % repr(sStdErr);
            if sStdOut != "INFO: No tasks are running which match the specified criteria.\r\n":
              time.sleep(1);
            else:
              break;
    except Exception, oException:
      oSelf._fInternalExceptionCallback(oException);
      raise;
    # report that we're finished.
    oSelf._fFinishedCallback(oSelf._oErrorReport);
    
  def _fDuringCdbThread(oSelf):
    try:
      if oSelf._bfInitializeDebugger(oSelf._asInitialCommands):
        oSelf._fApplicationStartedCallback();
        oSelf._oErrorReport = oSelf._foRunApplicationAndGetErrorReport();
    except Exception, oException:
      oSelf._fInternalExceptionCallback(oException);
      raise;

  def _bfInitializeDebugger(oSelf, asInitialCommands):
    # Read the initial cdb output
    if oSelf._fasReadOutput() is None:
      return False;
    # Execute all commands in the list and stop if cdb terminates in the mean time.
    for sCommand in asInitialCommands:
      if oSelf._fasSendCommandAndReadOutput(sCommand) is None:
        return False;
    # If the application was started by the debugger, the processes id must be retrieved.
    if not oSelf._auProcessIds:
      uProcessId, sBinaryName = cProcess.ftxGetCurrentProcessIdAndBinaryName(oSelf);
      if uProcessId is None: return False;
      oSelf._auProcessIds.append(uProcessId);
    return True;
  
  def _foRunApplicationAndGetErrorReport(oSelf):
    # The application is now started, read its output until an exception is detected:
    while len(oSelf._auProcessIds) > 0:
      asOutput = oSelf._fasSendCommandAndReadOutput("g");
      if asOutput is None: return None;
      asLastEventOutput = oSelf._fasSendCommandAndReadOutput(".lastevent");
      if asLastEventOutput is None: return None;
      # Sample output:
      # |Last event: 3d8.1348: Create process 3:3d8                
      # |  debugger time: Tue Aug 25 00:06:07.311 2015 (UTC + 2:00)
      # - or -
      # |Last event: c74.10e8: Exit process 4:c74, code 0          
      # |  debugger time: Tue Aug 25 00:06:07.311 2015 (UTC + 2:00)
      bLastEventOutputLooksGood = len(asLastEventOutput) == 2 and re.match(r"^\s*debugger time: .*$", asLastEventOutput[1]);
      oLastEventMatch = bLastEventOutputLooksGood and re.match(r"^Last event: [0-9A-F]+\.[0-9A-F]+: (.+?)\s*$", asLastEventOutput[0], re.I);
      assert oLastEventMatch, "Invalid .lastevent output:\r\n%s" % "\r\n".join(asLastEventOutput);
      sEvent = oLastEventMatch.group(1);
      oCreateExitProcessMatch = re.match(r"^(Create|Exit) process [0-9A-F]+\:([0-9A-F]+)(?:, code [0-9A-F]+)?$", sEvent, re.I);
      if oCreateExitProcessMatch:
        sCreateExit, sProcessIdHex = oCreateExitProcessMatch.groups();
        uProcessId = int(sProcessIdHex, 16);
        if sCreateExit == "Create":
          oSelf._auProcessIds.append(uProcessId);
        else:
          assert uProcessId in oSelf._auProcessIds, \
              "Missing process id: %\r\n%s" % (uProcessId, "\r\n",join(oSelf.asCdbIO));
          oSelf._auProcessIds.remove(uProcessId);
      else:
        oExceptionMatch = re.match(r"^(.*?) \- code ([0-9A-F]+) \(!*\s*(first|second) chance\s*!*\)$", sEvent, re.I);
        assert oExceptionMatch, "The last event was not recognized:\r\n%s" % "\r\n".join(asLastEventOutput);
        sDescription, sCode, sChance = oExceptionMatch.groups();
        if sChance == "second":
          # A fatal exception was detected
          uCode = int(sCode, 16);
          oSelf._fFatalExceptionDetectedCallback(uCode, sDescription);
          # Gather exception information:
          oException = cException.foCreate(oSelf, uCode, sDescription);
          if oException is None: return None;
          # Save the exception report for returning when we're finished.
          oSelf._oErrorReport = cErrorReport.foCreateFromException(oSelf, oException);
          # Stop running the application.
          break;
      # LOOP: continue the application.
    # Terminate cdb.
    oSelf._bExpectTermination = True;
    asDebuggerOutput = oSelf._fasSendCommandAndReadOutput("q");
    assert asDebuggerOutput is None, "Debugger did not terminate";
    return None;
  
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
      if sChar in ["\r", "\n", ""]:
        if dxCrashInfoConfig.get("bOutputIO", False): print "cdb>%s" % repr(sLine)[1:-1];
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
             ]), sCleanedLine);
            if oSymbolLoaderMessageMatch:
              # Sample output:
              # |SYMSRV:  c:\symbols\chakra.pdb\5249D6A2684341B79F239B9E6150169C1\chakra.pdb not found
              # |DBGHELP: \\server\symbols\chakra.pdb\5249D6A2684341B79F239B9E6150169C1\chakra.pdb cached to c:\symbols\chakra.pdb\5249D6A2684341B79F239B9E6150169C1\chakra.pdb
              # |DBGHELP: chakra - public symbols  
              # |        c:\symbols\chakra.pdb\5249D6A2684341B79F239B9E6150169C1\chakra.pdb
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
          if dxCrashInfoConfig.get("bOutputIO", False): print "cdb>%s" % repr(sLine)[1:-1];
          oSelf.asCdbIO.append(sCleanedLine);
          return asCleanedLines;
    # Cdb stdout was closed: the process is terminating.
    assert oSelf._bExpectTermination, \
        "Cdb terminated unexpectedly! Last output:\r\n%s" % "\r\n".join(oSelf.asCdbIO[-20:]);
    return None;
   
  def _fasSendCommandAndReadOutput(oSelf, sCommand):
    if dxCrashInfoConfig.get("bOutputIO", False): print "cdb<%s" % repr(sCommand)[1:-1];
    oSelf.asCdbIO[-1] += sCommand;
    try:
      oSelf._oCdbProcess.stdin.write("%s\r\n" % sCommand);
    except Exception, oException:
      assert oSelf._bExpectTermination, \
          "Cdb terminated unexpectedly! Last output:\r\n%s" % "\r\n".join(oSelf.asCdbIO[-20:]);
      return None;
    asOutput = oSelf._fasReadOutput();
    # Detect obvious errors executing the command. (this will not catch everything, but does help development)
    assert asOutput is None or len(asOutput) != 1 or not re.match(r"^\s*\^ .*$", asOutput[0]), \
        "There was a problem executing the command %s: %s" % (repr(sCommand), repr(asOutput));
    return asOutput;
