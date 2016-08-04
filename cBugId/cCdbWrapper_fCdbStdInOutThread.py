import datetime, re, time;
from cBugReport import cBugReport;
from daxExceptionHandling import daxExceptionHandling;
from dxBugIdConfig import dxBugIdConfig;
from fsCreateFileName import fsCreateFileName;
from NTSTATUS import *;

def fnGetDebuggerTime(sDebuggerTime):
  # Parse .time and .lastevent timestamps; return a number of seconds since an arbitrary but constant starting point in time.
  sMonths = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec";
  oTimeMatch = re.match("^%s$" % r"\s+".join([
    r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun)",                        # Weekday
    r"(%s)" % sMonths,                                       # Month
    r"(\d+)",                                                # Day in month
    r"(\d+):(\d+):(\d+).(\d+)",                              # Hour:Minute:Second.Milisecond
    r"(\d+)",                                                # Year
    r"\(\w+ \+ \d+:\d+\)",                                   # Timezone (don't care).
  ]), sDebuggerTime);
  assert oTimeMatch, "Cannot parse debugger time: %s" % repr(sDebuggerTime);
  sWeekDay, sMonth, sDay, sHour, sMinute, sSecond, sMilisecond, sYear = oTimeMatch.groups();
  # Convert date and time to a number of seconds since something, and add miliseconds:
  sTime = " ".join([sYear, sMonth, sDay, sHour, sMinute, sSecond]);
  oDateTime = datetime.datetime(
    long(sYear),
    sMonths.find(sMonth) / 4 + 1,
    long(sDay),
    long(sHour),
    long(sMinute),
    long(sSecond),
    long(sMilisecond.ljust(6, "0")),
  );
  return (oDateTime - datetime.datetime(1976,8,28)).total_seconds();

def cCdbWrapper_fCdbStdInOutThread(oCdbWrapper):
  # cCdbWrapper initialization code already acquire a lock on cdb on behalf of this thread, so the "interrupt on
  # timeout" thread does not attempt to interrupt cdb while this thread is getting started.
  try:
    # Create a list of commands to set up event handling. The default for any exception not explicitly mentioned is to
    # be handled as a second chance exception.
    asExceptionHandlingCommands = ["sxd *"];
    # request second chance debugger break for certain exceptions that indicate the application has a bug.
    for sCommand, axExceptions in daxExceptionHandling.items():
      for xException in axExceptions:
        sException = isinstance(xException, str) and xException or ("0x%08X" % xException);
        asExceptionHandlingCommands.append("%s %s" % (sCommand, sException));
    sExceptionHandlingCommands = ";".join(asExceptionHandlingCommands);
    
    # Read the initial cdb output related to starting/attaching to the first process.
    asIntialCdbOutput = oCdbWrapper.fasReadOutput();
    if not oCdbWrapper.bCdbRunning: return;
    # Turn off prompt information as it is not useful most of the time, but can clutter output.
    oCdbWrapper.fasSendCommandAndReadOutput(".prompt_allow -dis -ea -reg -src -sym", bIsRelevantIO = False);
    if not oCdbWrapper.bCdbRunning: return;
    
    # Exception handlers need to be set up.
    oCdbWrapper.bExceptionHandlersHaveBeenSet = False;
    # Only fire fApplicationRunningCallback if the application was started for the first time or resumed after it was
    # paused to analyze an exception. 
    bInitialApplicationRunningCallbackFired = False;
    bDebuggerNeedsToResumeAttachedProcesses = len(oCdbWrapper.auProcessIdsPendingAttach) > 0;
    bApplicationWasPausedToAnalyzeAnException = False;
    # An bug report will be created when needed; it is returned at the end
    oBugReport = None;
    # Memory can be allocated to be freed later in case the system has run low on memory when an analysis needs to be
    # performed. This is done only if dxBugIdConfig["uReserveRAM"] > 0. The memory is allocated at the start of
    # debugging, freed right before an analysis is performed and reallocated if the exception was not fatal.
    bReserveRAMAllocated = False;
    while asIntialCdbOutput or len(oCdbWrapper.auProcessIdsPendingAttach) + len(oCdbWrapper.auProcessIds) > 0 and oCdbWrapper.bCdbRunning:
      # If requested, reserve some memory in cdb that can be released later to make analysis under low memory conditions
      # more likely to succeed.
      if dxBugIdConfig["uReserveRAM"] and not bReserveRAMAllocated:
        uBitMask = 2 ** 31;
        while uBitMask >= 1:
          sBit = dxBugIdConfig["uReserveRAM"] & uBitMask and "A" or "";
          if bReserveRAMAllocated:
            oCdbWrapper.fasSendCommandAndReadOutput("aS /c RAM .printf \"${RAM}{$RAM}%s\";" % sBit,
                bIsRelevantIO = False);
          elif sBit:
            oCdbWrapper.fasSendCommandAndReadOutput("aS RAM \"%s\";" % sBit, bIsRelevantIO = False);
            bReserveRAMAllocated = True;
          if not oCdbWrapper.bCdbRunning: return;
          uBitMask /= 2;
      # Discard any cached information about modules loaded in the current process, as this may be about to change
      # during execution of the application.
      oCdbWrapper.doModules_by_sCdbId = None;
      if asIntialCdbOutput:
        # First parse the intial output
        asCdbOutput = asIntialCdbOutput;
        asIntialCdbOutput = None;
      else:
        # Then attach to a process, or start or resume the application
        if ( # If we've just started the application or we've attached to all processes and are about to resume them...
          not bInitialApplicationRunningCallbackFired and len(oCdbWrapper.auProcessIdsPendingAttach) == 0
        ) or ( # ... or if we've paused the application and are about to resume it ...
          bApplicationWasPausedToAnalyzeAnException
        ):
          # ...report that the application is about to start running.
          oCdbWrapper.fApplicationRunningCallback and oCdbWrapper.fApplicationRunningCallback();
          bInitialApplicationRunningCallbackFired = True;
        # Mark the time when the application was resumed.
        asCdbOutput = oCdbWrapper.fasSendCommandAndReadOutput(".time", bIsRelevantIO = False);
        if not oCdbWrapper.bCdbRunning: return;
        oTimeMatch = len(asCdbOutput) > 0 and re.match(r"^Debug session time: (.*?)\s*$", asCdbOutput[0]);
        assert oTimeMatch, "Failed to get debugger time!\r\n%s" % "\r\n".join(asCdbOutput);
        oCdbWrapper.oApplicationTimeLock.acquire();
        try:
          oCdbWrapper.nApplicationResumeDebuggerTime = fnGetDebuggerTime(oTimeMatch.group(1));
          oCdbWrapper.nApplicationResumeTime = time.clock();
        finally:
          oCdbWrapper.oApplicationTimeLock.release();
        # Release the lock on cdb so the "interrupt on timeout" thread can attempt to interrupt cdb while the
        # application is running.
        if len(oCdbWrapper.auProcessIdsPendingAttach) == 0:
          oCdbWrapper.oCdbLock.release();
        try:
          asCdbOutput = oCdbWrapper.fasSendCommandAndReadOutput("g", bMayContainApplicationOutput = True);
          if not oCdbWrapper.bCdbRunning: return;
        finally:
          # Get a lock on cdb so the "interrupt on timeout" thread does not attempt to interrupt cdb while we execute
          # commands.
          if len(oCdbWrapper.auProcessIdsPendingAttach) == 0:
            oCdbWrapper.oCdbLock.acquire();
          # Let the interrupt-on-timeout thread know that the application has been interrupted, so that when it detects
          # another timeout should be fired, it will try to interrupt the application again.
          oCdbWrapper.bInterruptPending = False;
      if oCdbWrapper.bGetDetailsHTML:
        # Save the current number of blocks of StdIO; if this exception is not relevant it can be used to remove all
        # blocks added while analyzing it. These blocks are not considered to contain useful information and removing
        # them can  reduce the risk of OOM when irrelevant exceptions happens very often. The last block contains a
        # prompt, which will become the first analysis command's block, so it is not saved.
        uOriginalHTMLCdbStdIOBlocks = len(oCdbWrapper.asCdbStdIOBlocksHTML) - 1;
      # Find out what event caused the debugger break
      asLastEventOutput = oCdbWrapper.fasSendCommandAndReadOutput(".lastevent");
      if not oCdbWrapper.bCdbRunning: return;
      # Sample output:
      # |Last event: 3d8.1348: Create process 3:3d8                
      # |  debugger time: Tue Aug 25 00:06:07.311 2015 (UTC + 2:00)
      # - or -
      # |Last event: c74.10e8: Exit process 4:c74, code 0          
      # |  debugger time: Tue Aug 25 00:06:07.311 2015 (UTC + 2:00)
      assert len(asLastEventOutput) == 2, "Invalid .lastevent output:\r\n%s" % "\r\n".join(asLastEventOutput);
      oEventMatch = re.match(
        "^%s\s*$" % "".join([
          r"Last event: ([0-9a-f]+)\.[0-9a-f]+: ",
          r"(?:",
            r"(Create|Exit) process [0-9a-f]+\:([0-9a-f]+)(?:, code [0-9a-f]+)?",
          r"|",
            r"(.*?) \- code ([0-9a-f]+) \(!*\s*(first|second) chance\s*!*\)",
          r"|",
            r"Hit breakpoint (\d+)",
          r")",
        ]),
        asLastEventOutput[0],
        re.I
      );
      assert oEventMatch, "Invalid .lastevent output on line #1:\r\n%s" % "\r\n".join(asLastEventOutput);
      oEventTimeMatch = re.match(r"^\s*debugger time: (.*?)\s*$", asLastEventOutput[1]);
      assert oEventTimeMatch, "Invalid .lastevent output on line #2:\r\n%s" % "\r\n".join(asLastEventOutput);
      oCdbWrapper.oApplicationTimeLock.acquire();
      try:
        if oCdbWrapper.nApplicationResumeDebuggerTime:
          # Add the time between when the application was resumed and when the event happened to the total application
          # run time.
          oCdbWrapper.nApplicationRunTime += fnGetDebuggerTime(oEventTimeMatch.group(1)) - oCdbWrapper.nApplicationResumeDebuggerTime;
        # Mark the application as suspended by setting nApplicationResumeDebuggerTime to None.
        oCdbWrapper.nApplicationResumeDebuggerTime = None;
        oCdbWrapper.nApplicationResumeTime = None;
      finally:
        oCdbWrapper.oApplicationTimeLock.release();
      (
        sProcessIdHex,
          sCreateExitProcess, sCreateExitProcessIdHex,
          sExceptionDescription, sExceptionCode, sChance,
          sBreakpointId,
      ) = oEventMatch.groups();
      uProcessId = long(sProcessIdHex, 16);
      uExceptionCode = sExceptionCode and long(sExceptionCode, 16);
      uBreakpointId = sBreakpointId and long(sBreakpointId);
      if (
        uExceptionCode in (STATUS_BREAKPOINT, STATUS_WAKE_SYSTEM_DEBUGGER)
        and uProcessId not in oCdbWrapper.auProcessIds
      ):
        # This is assumed to be the initial breakpoint after starting/attaching to the first process or after a new
        # process was created by the application. This assumption may not be correct, in which case the code needs to
        # be modifed to check the stack to determine if this really is the initial breakpoint. But that comes at a
        # performance cost, so until proven otherwise, the code is based on this assumption.
        sCreateExitProcess = "Create";
        sCreateExitProcessIdHex = sProcessIdHex;
      if sCreateExitProcess:
        # Make sure the created/exited process is the current process.
        assert sProcessIdHex == sCreateExitProcessIdHex, "%s vs %s" % (sProcessIdHex, sCreateExitProcessIdHex);
        oCdbWrapper.fHandleCreateExitProcess(sCreateExitProcess, uProcessId);
        # If there are more processes to attach to, do so:
        if len(oCdbWrapper.auProcessIdsPendingAttach) > 0:
          asAttachToProcess = oCdbWrapper.fasSendCommandAndReadOutput(".attach 0n%d" % oCdbWrapper.auProcessIdsPendingAttach[0]);
          if not oCdbWrapper.bCdbRunning: return;
        else:
          # Set up exception handling if this has not been done yet.
          if not oCdbWrapper.bExceptionHandlersHaveBeenSet:
            # Note to self: when rewriting the code, make sure not to set up exception handling before the debugger has
            # attached to all processes. But do so before resuming the threads. Otherwise one or more of the processes
            # can end up having only one thread that has a suspend count of 2 and no amount of resuming will cause the
            # process to run. The reason for this is unknown, but if things are done in the correct order, this problem
            # is avoided.
            oCdbWrapper.bExceptionHandlersHaveBeenSet = True;
            oCdbWrapper.fasSendCommandAndReadOutput(sExceptionHandlingCommands, bIsRelevantIO = False);
            if not oCdbWrapper.bCdbRunning: return;
          # If the debugger attached to processes, mark that as done and resume threads in all processes.
          if bDebuggerNeedsToResumeAttachedProcesses:
            bDebuggerNeedsToResumeAttachedProcesses = False;
            for uProcessId in oCdbWrapper.auProcessIds:
              oCdbWrapper.fSelectProcess(uProcessId);
              if not oCdbWrapper.bCdbRunning: return;
              oCdbWrapper.fasSendCommandAndReadOutput("~*m", bIsRelevantIO = False);
              if not oCdbWrapper.bCdbRunning: return;
        if oCdbWrapper.bGetDetailsHTML:
          # As this is not relevant to the bug, remove the commands and their output from cdb IO and replace with a
          # description of the exception to remove clutter and reduce memory usage. 
          oCdbWrapper.asCdbStdIOBlocksHTML = (
            oCdbWrapper.asCdbStdIOBlocksHTML[0:uOriginalHTMLCdbStdIOBlocks] + # IO before analysis commands
            ["<span class=\"CDBIgnoredException\">%s process %d breakpoint.</span><br/>" % (sCreateExitProcess, uProcessId)] + # Replacement for analysis commands
            oCdbWrapper.asCdbStdIOBlocksHTML[-1:] # Last block contains prompt and must be conserved.
          );
      elif uExceptionCode == DBG_CONTROL_BREAK:
        # Debugging the application was interrupted and the application suspended to fire some timeouts. This exception
        # is not a bug and should be ignored.
        pass;
      elif uExceptionCode == STATUS_SINGLE_STEP:
        # A bug in cdb causes single step exceptions at locations where a breakpoint is set. Since I have never seen a
        # single step exception caused by a bug in an application, I am assuming these are all caused by this bug and
        # ignore them:
        pass;
      elif (
        uExceptionCode in [STATUS_WX86_BREAKPOINT, STATUS_BREAKPOINT]
        and dxBugIdConfig["bIgnoreFirstChanceBreakpoints"]
        and sChance == "first"
      ):
        pass;
      else:
        # And potentially report that the application is resumed later...
        bApplicationWasPausedToAnalyzeAnException = True;
        # If available, free previously allocated memory to allow analysis in low memory conditions.
        if bReserveRAMAllocated:
          # This command is not relevant to the bug, so it is hidden in the cdb IO to prevent OOM.
          oCdbWrapper.fasSendCommandAndReadOutput("ad RAM;", bIsRelevantIO = False);
          bReserveRAMAllocated = False;
        if uBreakpointId is not None:
          if oCdbWrapper.bGetDetailsHTML:
            # Remove the breakpoint event from the cdb IO to remove clutter and reduce memory usage.
            oCdbWrapper.asCdbStdIOBlocksHTML = (
              oCdbWrapper.asCdbStdIOBlocksHTML[0:uOriginalHTMLCdbStdIOBlocks] + # IO before analysis commands
              oCdbWrapper.asCdbStdIOBlocksHTML[-1:] # Last block contains prompt and must be conserved.
            );
          fBreakpointCallback = oCdbWrapper.dfCallback_by_uBreakpointId[uBreakpointId];
          fBreakpointCallback();
        else:
          # Report that the application is paused for analysis...
          if oCdbWrapper.fExceptionDetectedCallback:
            if sBreakpointId:
              oCdbWrapper.fExceptionDetectedCallback(STATUS_BREAKPOINT, "A BugId breakpoint");
            else:
              oCdbWrapper.fExceptionDetectedCallback(uExceptionCode, sExceptionDescription);
          # Create a bug report, if the exception is fatal.
          oCdbWrapper.oBugReport = cBugReport.foCreateForException(oCdbWrapper, uExceptionCode, sExceptionDescription);
          if not oCdbWrapper.bCdbRunning: return;
          if oCdbWrapper.oBugReport is None and oCdbWrapper.bGetDetailsHTML:
            # Otherwise remove the analysis commands from the cdb IO and replace with a description of the exception to
            # remove clutter and reduce memory usage.
            oCdbWrapper.asCdbStdIOBlocksHTML = (
              oCdbWrapper.asCdbStdIOBlocksHTML[0:uOriginalHTMLCdbStdIOBlocks] + # IO before analysis commands
              ["<span class=\"CDBIgnoredException\">Exception 0x%08X in process %d ignored.</span><br/>" % (uExceptionCode, uProcessId)] +
              oCdbWrapper.asCdbStdIOBlocksHTML[-1:] # Last block contains prompt and must be conserved.
            );
        # See if a bug needs to be reported
        if oCdbWrapper.oBugReport is not None:
          # See if a dump should be saved
          if dxBugIdConfig["bSaveDump"]:
            sDumpFileName = fsCreateFileName(oCdbWrapper.oBugReport.sId);
            sOverwrite = dxBugIdConfig["bOverwriteDump"] and "/o" or "";
            oCdbWrapper.fasSendCommandAndReadOutput(".dump %s /ma \"%s.dmp\"" % (sOverwrite, sDumpFileName));
            if not oCdbWrapper.bCdbRunning: return;
          # Stop to report the bug.
          break;
      # Execute any pending timeout callbacks
      oCdbWrapper.oTimeoutsLock.acquire();
      try:
        axTimeoutsToFire = [];
        for xTimeout in oCdbWrapper.axTimeouts:
          (nTimeoutTime, fTimeoutCallback, axTimeoutCallbackArguments) = xTimeout;
          if nTimeoutTime <= oCdbWrapper.nApplicationRunTime: # This timeout should be fired.
            oCdbWrapper.axTimeouts.remove(xTimeout);
            axTimeoutsToFire.append((fTimeoutCallback, axTimeoutCallbackArguments));
#           print "@@@ firing timeout %.1f seconds late: %s" % (oCdbWrapper.nApplicationRunTime - nTimeoutTime, repr(fTimeoutCallback));
      finally:
        oCdbWrapper.oTimeoutsLock.release();
      for (fTimeoutCallback, axTimeoutCallbackArguments) in axTimeoutsToFire:
        fTimeoutCallback(*axTimeoutCallbackArguments);
    # Terminate cdb.
    oCdbWrapper.bCdbWasTerminatedOnPurpose = True;
    oCdbWrapper.fasSendCommandAndReadOutput("q");
  finally:
    oCdbWrapper.bCdbStdInOutThreadRunning = False;
    # Release the lock on cdb so the "interrupt on timeout" thread can notice cdb has terminated
    oCdbWrapper.oCdbLock.release();
  assert not oCdbWrapper.bCdbRunning, "Debugger did not terminate when requested";

