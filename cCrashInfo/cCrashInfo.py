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
  "cpr", "ch", "hc", "ibp", "ld", "ud", "wos",
  # "epr" is missing because it is special-cased in the code, see below
];

class cCrashInfo(object):
  sISA = sISA;
  def __init__(oSelf, asApplicationCommandLine, auApplicationProcessIds, sApplicationISA, asSymbolServerURLs, \
      fApplicationStartedCallback, fErrorDetectedCallback, fFinishedCallback, fInternalExceptionCallback):
    oSelf._fApplicationStartedCallback = fApplicationStartedCallback;
    oSelf._fErrorDetectedCallback = fErrorDetectedCallback;
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
      oSelf._auAttachProcessIds = auApplicationProcessIds;
      oSelf._bResumeThreads = True;
    else:
      oSelf._auAttachProcessIds = [];
      oSelf._bResumeThreads = False;
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
    oSelf._oProcess = subprocess.Popen(args = " ".join(asCommandLine), stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE);
    oSelf._oDebugApplicationThread = threading.Thread(target = oSelf._fDebugApplication);
    oSelf._oDebugApplicationThread.start();
  
  def __del__(oSelf):
    # Make sure we always kill the debugger
    while oSelf._oProcess and oSelf._oProcess.poll() == None:
      print "*** INTERNAL ERROR: CrashInfo was terminated before cdb was terminated.";
      oSelf._oProcess.terminate();
      time.sleep(1);
  
  def fStop(oSelf):
    oSelf._bExpectTermination = True;
    # terminate the cdb process
    while oSelf._oProcess.poll() == None:
      oSelf._oProcess.terminate();
      time.sleep(1);
    # wait for the application debugger thread to notice cdb has died and terminate.
    oSelf._oDebugApplicationThread.join();
  
  def _fDebugApplication(oSelf):
    try:
      # Read the initial cdb output
      if oSelf._fasReadOutput() is None:
        return None;
      # Make a list of all the cdb commands that need to be execute to initialize and start the application.
      asInitialCommands = [];
      # if requested, resume all threads in current process.
      asInitialCommands.append(".childdbg 1");
      if oSelf._bResumeThreads: asInitialCommands.append("~*m");
      # if requested, attach to additional processes and optionally resume all threads in those as well.
      for uAttachProcessId in oSelf._auAttachProcessIds:
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
      # if epr is disabled, the debugger will silently exit when the application terminates.
      # To distinguish this from other unexpected terminations of the debugger, epr is enabled and the "g" command is
      # executed whenever a process terminates. This will continue execution of the application until the last process
      # is terminated, at which point cdb outputs an error message. This error message is detected to determine that
      # the application has terminated without crashing.
      asInitialCommands.append("sxe -c \"g\" epr");
      
      # Execute all commands in the list and stop if cdb terminates in the mean time.
      for sCommand in asInitialCommands:
        if oSelf._fasSendCommandAndReadOutput(sCommand) is None:
          return;
      oSelf._fApplicationStartedCallback();
      # The application is now started, read its output until an exception is detected:
      while 1:
        asExceptionDetectedOutput = oSelf._fasSendCommandAndReadOutput("g");
        if asExceptionDetectedOutput is None:
          return;
        # Scan backwards through the output to detect the exception that occured:
        for uIndex in xrange(len(asExceptionDetectedOutput) - 1, -1, -1):
          sLine = asExceptionDetectedOutput[uIndex];
          # Event output looks like this:
          # |(16c0.11c): Access violation - code c0000005 (!!! second chance !!!)
          # |(273c.1f1c): Security check failure or stack buffer overrun - code c0000409 (!!! second chance !!!)
          oEventMatch = re.match(r"^\s*%s\s*$" % (
            r"\([0-9A-F]+\.[0-9A-F]+\): "           # "(" process id "." thread id "): "
            r"(.*?)"                                # (exception description)"
            r" \- code "                            # " - code "
            r"([0-9A-F`]+)"                         # (exception code)
            r" \(!*\s*(first|second) chance\s*!*\)" # " (first chance)" or " (!!! second chance !!!)"
          ), sLine, re.I);
          if oEventMatch:
            sDescription, sCode, sChance = oEventMatch.groups();
            uCode = int(sCode.replace("`", ""), 16);
            break;
          oTerminatedMatch = re.match(r"^\s*\^ No runnable debuggees error in '.*'\s*$", sLine);
          if oTerminatedMatch:
            oSelf._bExpectTermination = True;
            asDebuggerOutput = oSelf._fasSendCommandAndReadOutput("q");
            assert asDebuggerOutput is None, "Debugger did not terminate";
            return;
        else:
          raise AssertionError(
            "Could not find what caused the debugger to break into the application!\r\n%s" %
            "\r\n".join(asExceptionDetectedOutput)
          );
        if sChance == "second":
          break; # we've found something interesting
        # get a stack for this first chance exception (in case it turns out to be interesting later)
        if oSelf._fasSendCommandAndReadOutput("kn 0x%X" % dxCrashInfoConfig.get("uMaxStackFramesCount", 50)) is None:
          return;
        # LOOP: continue the application.
      
      # An exception that should be reported was detected
      oSelf._fErrorDetectedCallback();
      # Gather exception information:
      oException = cException.foCreate(oSelf, uCode, sDescription);
      if oException is None:
        return None;
      # Save the exception report for returning when we're finished.
      oSelf._oErrorReport = cErrorReport.foCreateFromException(oSelf, oException);
      # terminate the debugger.
      oSelf._bExpectTermination = True;
      asDebuggerOutput = oSelf._fasSendCommandAndReadOutput("q");
      assert asDebuggerOutput is None, "Debugger did not terminate";
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
      sChar = oSelf._oProcess.stdout.read(1);
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
    oSelf._oProcess.wait(); # wait for it to terminate completely.
    oSelf._fFinishedCallback(oSelf._oErrorReport);
    return None;
   
  def _fasSendCommandAndReadOutput(oSelf, sCommand):
    if dxCrashInfoConfig.get("bOutputIO", False): print "cdb<%s" % repr(sCommand)[1:-1];
    oSelf.asCdbIO[-1] += sCommand;
    try:
      oSelf._oProcess.stdin.write("%s\r\n" % sCommand);
    except Exception, oException:
      assert oSelf._bExpectTermination, \
          "Cdb terminated unexpectedly! Last output:\r\n%s" % "\r\n".join(oSelf.asCdbIO[-20:]);
      oSelf._oProcess.wait(); # wait for it to terminate completely.
      oSelf._fFinishedCallback(oSelf._oErrorReport);
      return None;
    asOutput = oSelf._fasReadOutput();
    # Detect obvious errors executing the command. (this will not catch everything, but does help development)
    assert asOutput is None or len(asOutput) != 1 or not re.match(r"^\s*\^ .*$", asOutput[0]), \
        "There was a problem executing the command %s: %s" % (repr(sCommand), repr(asOutput));
    return asOutput;
