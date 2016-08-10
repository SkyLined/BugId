import re, threading, time;
from cBugReport import cBugReport;
from dxBugIdConfig import dxBugIdConfig;

bDebugOutput = False;
bDebugOutputCalculation = False;
bDebugOutputGetUsageData = False;
bDebugOutputWorm = False;

class cExcessiveCPUUsageDetector(object):
  def __init__(oExcessiveCPUUsageDetector, oCdbWrapper):
    oExcessiveCPUUsageDetector.oCdbWrapper = oCdbWrapper;
    oExcessiveCPUUsageDetector.oLock = threading.Lock();
    oExcessiveCPUUsageDetector.xCleanupTimeout = None;
    oExcessiveCPUUsageDetector.xStartTimeout = None;
    oExcessiveCPUUsageDetector.xCheckUsageTimeout = None;
    oExcessiveCPUUsageDetector.xWormRunTimeout = None;
    oExcessiveCPUUsageDetector.uWormBreakpointId = None;
    oExcessiveCPUUsageDetector.uBugBreakpointId = None;
  
  def fStartTimeout(oExcessiveCPUUsageDetector, nTimeout):
    if bDebugOutput: print "@@@ Starting excessive CPU usage checks in %d seconds..." % nTimeout;
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    oExcessiveCPUUsageDetector.oLock.acquire();
    try:
      # Stop any analysis timeouts in progress...
      if oExcessiveCPUUsageDetector.xStartTimeout is not None:
        oCdbWrapper.fClearTimeout(oExcessiveCPUUsageDetector.xStartTimeout);
        oExcessiveCPUUsageDetector.xStartTimeout = None;
      if oExcessiveCPUUsageDetector.xCheckUsageTimeout is not None:
        oCdbWrapper.fClearTimeout(oExcessiveCPUUsageDetector.xCheckUsageTimeout);
        oExcessiveCPUUsageDetector.xCheckUsageTimeout = None;
      oExcessiveCPUUsageDetector.xPreviousData = None; # Previous data is no longer valid.
      # Request an immediate timeout to remove old breakpoints when the application is paused. This is needed because
      # we cannot execute any command while the application is still running, so these breakpoints cannot be removed
      # here.
      if oExcessiveCPUUsageDetector.xCleanupTimeout is not None:
        oCdbWrapper.fClearTimeout(oExcessiveCPUUsageDetector.xCleanupTimeout);
        oExcessiveCPUUsageDetector.xCleanupTimeout = None;
      oExcessiveCPUUsageDetector.xCleanupTimeout = oCdbWrapper.fxSetTimeout(0, oExcessiveCPUUsageDetector.fCleanup);
      if nTimeout is not None:
        oExcessiveCPUUsageDetector.xStartTimeout = oCdbWrapper.fxSetTimeout(nTimeout, oExcessiveCPUUsageDetector.fStart);
    finally:
      oExcessiveCPUUsageDetector.oLock.release();
  
  def fCleanup(oExcessiveCPUUsageDetector):
    # Remove old breakpoints; this is done in a timeout because we cannot execute any command while the application
    # is still running.
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    oExcessiveCPUUsageDetector.oLock.acquire();
    try:
      if oExcessiveCPUUsageDetector.xCleanupTimeout:
        oCdbWrapper.fClearTimeout(oExcessiveCPUUsageDetector.xCleanupTimeout);
        oExcessiveCPUUsageDetector.xCleanupTimeout = None;
        if bDebugOutput: print "@@@ Cleaning up excessive CPU usage breakpoints...";
        if oExcessiveCPUUsageDetector.uWormBreakpointId is not None:
          oCdbWrapper.fRemoveBreakpoint(oExcessiveCPUUsageDetector.uWormBreakpointId);
          oExcessiveCPUUsageDetector.uWormBreakpointId = None;
          if not oCdbWrapper.bCdbRunning: return;
        if oExcessiveCPUUsageDetector.uBugBreakpointId is not None:
          oCdbWrapper.fRemoveBreakpoint(oExcessiveCPUUsageDetector.uBugBreakpointId);
          oExcessiveCPUUsageDetector.uBugBreakpointId = None;
          if not oCdbWrapper.bCdbRunning: return;
    finally:
      oExcessiveCPUUsageDetector.oLock.release();
  
  def fStart(oExcessiveCPUUsageDetector):
    # A timeout to execute the cleanup function was set, but there is no guarantee the timeout has been fired yet; the
    # timeout to start this function may have been fired first. By calling the cleanup function now, we make sure that
    # cleanup happens if it has not already, and cancel the cleanup timeout if it has not yet fired.
    oExcessiveCPUUsageDetector.fCleanup();
    if bDebugOutput: print "@@@ Start excessive CPU usage checks...";
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    oExcessiveCPUUsageDetector.fGetUsageData();
    oExcessiveCPUUsageDetector.oLock.acquire();
    try:
      nTimeout = dxBugIdConfig["nExcessiveCPUUsageCheckInterval"];
      oExcessiveCPUUsageDetector.xCheckUsageTimeout = oCdbWrapper.fxSetTimeout(nTimeout, oExcessiveCPUUsageDetector.fCheckUsage);
    finally:
      oExcessiveCPUUsageDetector.oLock.release();
  
  def fCheckUsage(oExcessiveCPUUsageDetector):
    if bDebugOutput: print "@@@ Checking for excessive CPU usage...";
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    if oCdbWrapper.fExceptionDetectedCallback:
      oCdbWrapper.fExceptionDetectedCallback(None, "Excessive CPU usage check"); # No exception code
    oExcessiveCPUUsageDetector.oLock.acquire();
    try:
      if oExcessiveCPUUsageDetector.xCheckUsageTimeout is None:
        return; # Analysis was stopped because a new timeout was set.
      oExcessiveCPUUsageDetector.xCheckUsageTimeout = None;
      ddnPreviousCPUTime_by_uThreadId_by_uProcessId = oExcessiveCPUUsageDetector.ddnLastCPUTime_by_uThreadId_by_ProcessId;
      nPreviousRunTime = oExcessiveCPUUsageDetector.nLastRunTime;
      oExcessiveCPUUsageDetector.fGetUsageData();
      ddnCurrentCPUTime_by_uThreadId_by_uProcessId = oExcessiveCPUUsageDetector.ddnLastCPUTime_by_uThreadId_by_ProcessId;
      nCurrentRunTime = oExcessiveCPUUsageDetector.nLastRunTime;
      nRunTime = nCurrentRunTime - nPreviousRunTime;
      # Find out which thread in which process used the most CPU time by comparing previous CPU usage and
      # run time values to current values for all threads in all processes that exist in both data sets.
      nMaxCPUPercent = -1;
      nTotalCPUPercent = 0;
      if bDebugOutputCalculation:
        print ",--- cExcessiveCPUUsageDetector.fGetUsageData ".ljust(120, "-");
        print "| Application run time: %.3f->%.3f=%.3f" % (nPreviousRunTime, nCurrentRunTime, nRunTime);
      for (uProcessId, dnCurrentCPUTime_by_uThreadId) in ddnCurrentCPUTime_by_uThreadId_by_uProcessId.items():
        if bDebugOutputCalculation:
          print ("|--- Process 0x%X" % uProcessId).ljust(120, "-");
          print "| %3s  %21s  %7s" % ("tid", "CPU time", "% Usage");
        dnPreviousCPUTime_by_uThreadId = ddnPreviousCPUTime_by_uThreadId_by_uProcessId.get(uProcessId, {});
        for (uThreadId, nCurrentCPUTime) in dnCurrentCPUTime_by_uThreadId.items():
          # nRunTime can be None due to a bug in cdb. In such cases, usage percentage cannot be calculated
          nPreviousCPUTime = dnPreviousCPUTime_by_uThreadId.get(uThreadId);
          if nPreviousCPUTime is not None and nCurrentCPUTime is not None:
            nCPUTime = nCurrentCPUTime - nPreviousCPUTime;
          else:
            nCPUTime = None;
          if nCPUTime is not None:
            nCPUPercent = nRunTime > 0 and (100.0 * nCPUTime / nRunTime) or 0;
            nTotalCPUPercent += nCPUPercent;
            if nCPUPercent > nMaxCPUPercent:
              nMaxCPUPercent = nCPUPercent;
              uMaxCPUProcessId = uProcessId;
              uMaxCPUThreadId = uThreadId;
          else:
            nCPUPercent = None;
          def fsFormat(nNumber):
            return nNumber is None and " - " or ("%.3f" % nNumber);
          if bDebugOutputCalculation: print "| %4X  %6s->%6s=%6s  %6s%%" % (
            uThreadId,
            fsFormat(nPreviousCPUTime), fsFormat(nCurrentCPUTime), fsFormat(nCPUTime),
            fsFormat(nCPUPercent),
          );
      if bDebugOutputCalculation:
        print "|".ljust(120, "-");
        print "| Total CPU usage: %d%%, max: %d%% for pid 0x%X, tid 0x%X" % \
           (nTotalCPUPercent, nMaxCPUPercent, uMaxCPUProcessId, uMaxCPUThreadId);
        print "'".ljust(120, "-");
      elif bDebugOutput:
        print "*** Total CPU usage: %d%%, max: %d%% for pid %d, tid %d" % \
            (nTotalCPUPercent, nMaxCPUPercent, uMaxCPUProcessId, uMaxCPUThreadId);
      # Rounding errors can give results > 100%. Fix that.
      if nTotalCPUPercent > 100:
        nTotalCPUPercent = 100.0;
      # If all threads in all processes combined have excessive CPU usage
      if nTotalCPUPercent > dxBugIdConfig["nExcessiveCPUUsagePercent"]:
        # Find out which function is using excessive CPU time in the most active thread.
        oExcessiveCPUUsageDetector.fInstallWorm(uMaxCPUProcessId, uMaxCPUThreadId, nTotalCPUPercent);
      else:
        # No thread suspected of excessive CPU usage: measure CPU usage over another interval.
        nTimeout = dxBugIdConfig["nExcessiveCPUUsageCheckInterval"];
        oExcessiveCPUUsageDetector.xCheckUsageTimeout = oCdbWrapper.fxSetTimeout(nTimeout, oExcessiveCPUUsageDetector.fCheckUsage);
    finally:
      oExcessiveCPUUsageDetector.oLock.release();
  
  def fWormDebugOutput(oExcessiveCPUUsageDetector, sMessage, *auArguments):
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    asDebugOutput = oCdbWrapper.fasSendCommandAndReadOutput(
      '.printf "CPUUsage worm: %s\\r\\n"%s;' % \
          (sMessage, "".join([", 0x%X" % uArgument for uArgument in auArguments])),
      bShowOnlyCommandOutput = True,
    );
    if not oCdbWrapper.bCdbRunning: return;
    assert len(asDebugOutput) == 1, "Unexpected output: %s" % repr(asDebugOutput);
    if bDebugOutputWorm: print "@@@ %s" % asDebugOutput[0];
  
  def fInstallWorm(oExcessiveCPUUsageDetector, uProcessId, uThreadId, nTotalCPUPercent):
    if bDebugOutput: print "@@@ Installing excessive CPU usage worm...";
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    # NO LOCK! Called from method that already locked it.
    if oCdbWrapper.fExceptionDetectedCallback:
      oCdbWrapper.fExceptionDetectedCallback(None, "Excessive CPU usage"); # No exception code
    
    # Excessive CPU usage is assumed to be caused by code running in a loop for too long, causing the function that
    # contains the code to never return to its caller. The way a useful BugId is determined, is by finding an address
    # inside the looping code in this function, set a breakpoint there and report a bug when it is hit. The exact
    # instruction in this loop may change between runs, but the functions on the stack should not, and the latter is
    # used in the stack hash, giving you the same id for different tests of the same bug.
    # We already determined which process and thread used the most CPU, so the current instruction pointer for that
    # thread should be inside the loop, but it may in a function that was called by the looping function as part of the
    # loop. If so, this function should return. To find the one function on the stack that does not return, we create
    # a breakpoint "worm": whenever this breakpoint is hit, it moves up the stack by moving the breakpoint from its
    # current location to the current return address on the stack. Should the function in which the breakpoint was hit
    # return, the new breakpoint will be hit and the worm sets another breakpoint for the new return address. If the
    # function does not return, the breakpoint will not be hit and the worm will no longer move up the stack.
    # Every time a breakpoint is hit, its location is saved in a variable. After running some time, the application
    # is interrupted to set a breakpoint at the location of the last breakpoint that was hit. Since this is part of the
    # loop, it should get hit again, at which point a bug is reported. This allows us to get a stack inside the
    # function most likely to be the cause of the excessive CPU usage.
    
    # Select the relevant process and thread
    oCdbWrapper.fSelectProcessAndThread(uProcessId, uThreadId);
    if not oCdbWrapper.bCdbRunning: return;
    oExcessiveCPUUsageDetector.uProcessId = uProcessId;
    oExcessiveCPUUsageDetector.uThreadId = uThreadId;
    oExcessiveCPUUsageDetector.nTotalCPUPercent = nTotalCPUPercent;
    uInstructionPointer = oCdbWrapper.fuGetValue("@$ip");
    if not oCdbWrapper.bCdbRunning: return;
    uStackPointer = oCdbWrapper.fuGetValue("@$csp");
    if not oCdbWrapper.bCdbRunning: return;
# Ideally, we'de use the return address here but for some unknown reason cdb may not give a valid value at this point.
# However, we can use the instruction pointer to set our first breakpoint and when it is hit, the return addres will be
# correct... sigh.
#    uReturnAddress = oCdbWrapper.fuGetValue("@$ra");
#    if not oCdbWrapper.bCdbRunning: return;
    uBreakpointAddress = uInstructionPointer; # uReturnAddress would be preferred.
    oExcessiveCPUUsageDetector.fWormDebugOutput(
      "Starting at IP=%ly, SP=%p: setting breakpoint at IP=%ly ...",
      uInstructionPointer, uBreakpointAddress, uStackPointer
    );
    if not oCdbWrapper.bCdbRunning: return;
    oExcessiveCPUUsageDetector.uLastInstructionPointer = uInstructionPointer;
    oExcessiveCPUUsageDetector.uLastStackPointer = uStackPointer;
    oExcessiveCPUUsageDetector.uNextBreakpointAddress = uBreakpointAddress;
    oExcessiveCPUUsageDetector.uWormBreakpointId = oCdbWrapper.fuAddBreakpoint(
      uAddress = uBreakpointAddress,
      fCallback = oExcessiveCPUUsageDetector.fMoveWormBreakpointUpTheStack,
      uProcessId = oExcessiveCPUUsageDetector.uProcessId,
      uThreadId = oExcessiveCPUUsageDetector.uThreadId,
    );
    if not oCdbWrapper.bCdbRunning: return;
    assert oExcessiveCPUUsageDetector.uWormBreakpointId is not None, \
        "Could not set breakpoint at 0x%X" % oExcessiveCPUUsageDetector.uLastInstructionPointer;
    nTimeout = dxBugIdConfig["nExcessiveCPUUsageWormRunTime"];
    oExcessiveCPUUsageDetector.xWormRunTimeout = oCdbWrapper.fxSetTimeout(nTimeout, oExcessiveCPUUsageDetector.fSetBugBreakpointAfterTimeout);
  
  def fMoveWormBreakpointUpTheStack(oExcessiveCPUUsageDetector):
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    oExcessiveCPUUsageDetector.oLock.acquire();
    try:
      uStackPointer = oCdbWrapper.fuGetValue("@$csp");
      if not oCdbWrapper.bCdbRunning: return;
      uInstructionPointer = oCdbWrapper.fuGetValue("@$ip");
      if not oCdbWrapper.bCdbRunning: return;
      # This is a sanity check: the instruction pointer should be equal to the address at which we set the breakpoint.
      assert uInstructionPointer == oExcessiveCPUUsageDetector.uNextBreakpointAddress, \
          "Expected to hit breakpoint at 0x%X, but got 0x%X instead !?" % (oExcessiveCPUUsageDetector.uNextBreakpointAddress, uInstructionPointer);
      # The code we're expecting to return to may actually be *called* in recursive code. We can detect this by checking
      # if the stackpointer has increased or not. If not, we have not yet returned and will ignore this breakpoint.
      if uStackPointer <= oExcessiveCPUUsageDetector.uLastStackPointer:
        oExcessiveCPUUsageDetector.fWormDebugOutput(
          "Ignored breakpoint at IP=%ly, SP=%p: SP but must be >%p",
          uInstructionPointer, uStackPointer, oExcessiveCPUUsageDetector.uLastStackPointer
        );
        if not oCdbWrapper.bCdbRunning: return;
        return;
      uReturnAddress = oCdbWrapper.fuGetValue("@$ra");
      if not oCdbWrapper.bCdbRunning: return;
      oExcessiveCPUUsageDetector.fWormDebugOutput(
        "Moving from IP=%ly, SP=%p by setting breakpoint at IP=%ly...",
        uInstructionPointer, uStackPointer, uReturnAddress
      );
      if not oCdbWrapper.bCdbRunning: return;
      # Try to move the breakpoint to the return addess:
      uNewWormBreakpointId = oCdbWrapper.fuAddBreakpoint(
        uAddress = uReturnAddress,
        fCallback = oExcessiveCPUUsageDetector.fMoveWormBreakpointUpTheStack,
        uProcessId = oExcessiveCPUUsageDetector.uProcessId,
        uThreadId = oExcessiveCPUUsageDetector.uThreadId,
      );
      if not oCdbWrapper.bCdbRunning: return;
      if uNewWormBreakpointId is None:
        # Could not move breakpoint: the return address may be invalid.
        # Ignore this and continue to run; the unchanged breakpoint may get hit again and we get another try, or
        # the timeout fires and we get a stack.
        oExcessiveCPUUsageDetector.fWormDebugOutput(
          "Unable to set breakpoint at IP=%ly: worm breakpoint remains at IP=%ly...\\r\\n",
          uReturnAddress, uInstructionPointer
        );
        if not oCdbWrapper.bCdbRunning: return;
      else:
        # Remove the old breakpoint.
        oCdbWrapper.fRemoveBreakpoint(oExcessiveCPUUsageDetector.uWormBreakpointId);
        if not oCdbWrapper.bCdbRunning: return;
        oExcessiveCPUUsageDetector.uWormBreakpointId = uNewWormBreakpointId;
        oExcessiveCPUUsageDetector.uLastInstructionPointer = uInstructionPointer;
        oExcessiveCPUUsageDetector.uLastStackPointer = uStackPointer;
        oExcessiveCPUUsageDetector.uNextBreakpointAddress = uReturnAddress;
        # Clear the current timeout and start a new one.
        oCdbWrapper.fClearTimeout(oExcessiveCPUUsageDetector.xWormRunTimeout);
        nTimeout = dxBugIdConfig["nExcessiveCPUUsageWormRunTime"];
        oExcessiveCPUUsageDetector.xWormRunTimeout = oCdbWrapper.fxSetTimeout(nTimeout, oExcessiveCPUUsageDetector.fSetBugBreakpointAfterTimeout);
    finally:
      oExcessiveCPUUsageDetector.oLock.release();

  def fSetBugBreakpointAfterTimeout(oExcessiveCPUUsageDetector):
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    if bDebugOutput: print "@@@ Worm run timeout: setting excessive CPU usage bug breakpoint...";
    oExcessiveCPUUsageDetector.oLock.acquire();
    try:
      if oExcessiveCPUUsageDetector.xWormRunTimeout is None:
        return; # Analysis was stopped because a new timeout was set.
      oExcessiveCPUUsageDetector.xWormRunTimeout = None;
      oExcessiveCPUUsageDetector.fWormDebugOutput(
        "Run timeout; putting bug breakpoint at IP=%ly, SP=%p...",
        oExcessiveCPUUsageDetector.uLastInstructionPointer, oExcessiveCPUUsageDetector.uLastStackPointer
      );
      if not oCdbWrapper.bCdbRunning: return;
      # Remove worm breakpoint
      oCdbWrapper.fRemoveBreakpoint(oExcessiveCPUUsageDetector.uWormBreakpointId);
      oExcessiveCPUUsageDetector.uWormBreakpointId = None;
      if not oCdbWrapper.bCdbRunning: return;
      # Set bug breakpoint
      oExcessiveCPUUsageDetector.uBugBreakpointId = oCdbWrapper.fuAddBreakpoint(
        uAddress = oExcessiveCPUUsageDetector.uLastInstructionPointer,
        fCallback = oExcessiveCPUUsageDetector.fReportCPUUsageBug,
        uProcessId = oExcessiveCPUUsageDetector.uProcessId,
        uThreadId = oExcessiveCPUUsageDetector.uThreadId,
      );
      oExcessiveCPUUsageDetector.uNextBreakpointAddress = oExcessiveCPUUsageDetector.uLastInstructionPointer;
      if not oCdbWrapper.bCdbRunning: return;
      assert oExcessiveCPUUsageDetector.uBugBreakpointId is not None, \
         "Could not set breakpoint at 0x%X" % oExcessiveCPUUsageDetector.uLastInstructionPointer;
    finally:
      oExcessiveCPUUsageDetector.oLock.release();
  
  def fReportCPUUsageBug(oExcessiveCPUUsageDetector):
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    oExcessiveCPUUsageDetector.oLock.acquire();
    try:
      uStackPointer = oCdbWrapper.fuGetValue("@$csp");
      if not oCdbWrapper.bCdbRunning: return;
      uInstructionPointer = oCdbWrapper.fuGetValue("@$ip");
      if not oCdbWrapper.bCdbRunning: return;
      # This is a sanity check: the instruction pointer should be equal to the address at which we set the breakpoint.
      assert uInstructionPointer == oExcessiveCPUUsageDetector.uNextBreakpointAddress, \
          "Expected to hit breakpoint at 0x%X, but got 0x%X instead !?" % (oExcessiveCPUUsageDetector.uNextBreakpointAddress, uInstructionPointer);
      # The code we're expecting to return to may actually be *called* in recursive code. We can detect this by checking
      # if the stackpointer has increased or not. If not, we have not yet returned and will ignore this breakpoint.
      if uStackPointer < oExcessiveCPUUsageDetector.uLastStackPointer:
        oExcessiveCPUUsageDetector.fWormDebugOutput(
          "Ignored bug breakpoint at IP=%ly, SP=%p: SP but must be >=%p",
          uInstructionPointer, uStackPointer, oExcessiveCPUUsageDetector.uLastStackPointer
        );
        if not oCdbWrapper.bCdbRunning: return;
        return;
      if bDebugOutput: print "@@@ Reporting excessive CPU usage bug...";
      # Remove the breakpoint
      oCdbWrapper.fRemoveBreakpoint(oExcessiveCPUUsageDetector.uBugBreakpointId);
      if not oCdbWrapper.bCdbRunning: return;
      oExcessiveCPUUsageDetector.uBugBreakpointId = None;
      # Report a bug
      sBugTypeId = "CPUUsage";
      sBugDescription = "The application was using %d%% CPU for %d seconds, which is considered excessive." % \
          (oExcessiveCPUUsageDetector.nTotalCPUPercent, dxBugIdConfig["nExcessiveCPUUsageCheckInterval"]);
      sSecurityImpact = None;
      if not oCdbWrapper.bCdbRunning: return;
      oCdbWrapper.oBugReport = cBugReport.foCreate(oCdbWrapper, sBugTypeId, sBugDescription, sSecurityImpact);
      if not oCdbWrapper.bCdbRunning: return;
      oCdbWrapper.oBugReport.bRegistersRelevant = False;
    finally:
      oExcessiveCPUUsageDetector.oLock.release();
  
  def fGetUsageData(oExcessiveCPUUsageDetector):
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    # Get the amount of CPU time each thread in each process has consumed
    ddnCPUTime_by_uThreadId_by_uProcessId = {};
    sTimeType = None;
    if bDebugOutputGetUsageData:
      print ",--- cExcessiveCPUUsageDetector.fGetUsageData ".ljust(120, "-");
    for uProcessId in oCdbWrapper.auProcessIds:
      if bDebugOutputGetUsageData:
        print ("|--- Process 0x%X" % uProcessId).ljust(120, "-");
        print "| %4s  %6s  %s" % ("tid", "time", "source line");
      oCdbWrapper.fSelectProcess(uProcessId);
      if not oCdbWrapper.bCdbRunning: return;
      asThreadTimes = oCdbWrapper.fasSendCommandAndReadOutput(
        "!runaway 7; $$ Get CPU usage information",
      );
      if not oCdbWrapper.bCdbRunning: return;
      dnCPUTime_by_uThreadId = {};
      dnCPUTime_by_uThreadId = ddnCPUTime_by_uThreadId_by_uProcessId[uProcessId] = {};
      for sLine in asThreadTimes:
        if re.match(r"^\s*(Thread\s+Time)\s*$", sLine):
          pass; # Header, ignored.
        elif re.match(r"^\s*(User Mode Time|Kernel Mode Time|Elapsed Time)\s*$", sLine):
          sTimeType = sLine.strip(); # Keep track of what type of type of times are being reported.
        else:
          assert sTimeType is not None, \
              "Expected a header before values in %s.\r\n%s" % (sLine, "\r\n".join(asThreadTimes));
          oThreadTime = re.match(r"^\s*\d+:(\w+)\s+ (\d+) days (\d\d?):(\d\d):(\d\d).(\d\d\d)\s*$", sLine);
          assert oThreadTime, \
              "Unrecognized \"!runaway3\" output: %s\r\n%s" % (sLine, "\r\n".join(asThreadCPUTime));
          sThreadId, sDays, sHours, sMinutes, sSeconds, sMilliseconds = oThreadTime.groups();
          uThreadId = int(sThreadId, 16);
          nTime = ((long(sDays) * 24 + long(sHours)) * 60 + long(sMinutes)) * 60 + long(sSeconds) + long(sMilliseconds) / 1000.0;
          if nTime >= 2000000000:
            # Due to a bug in !runaway, elapsed time sometimes gets reported as a very, very large number.
            assert sTimeType == "Elapsed Time", \
                "Unexpected large value for %s: %s\r\n%s" % (sTimeType, nTime, "\r\n".join(asThreadCPUTime));
            # In such cases, do not return a value for elapsed time.
            nTime = None;
  # Use for debugging
          if sTimeType == "User Mode Time":
            dnCPUTime_by_uThreadId[uThreadId] = nTime;
            if bDebugOutputGetUsageData: print "| %4X  %6s %s" % (uThreadId, nTime is None and "?" or ("%.3f" % nTime), repr(sLine));
          elif sTimeType == "Kernel Mode Time":
            dnCPUTime_by_uThreadId[uThreadId] += nTime;
            if bDebugOutputGetUsageData: print "| %4X  %6s %s" % (uThreadId, nTime is None and "?" or ("+%.3f" % nTime), repr(sLine));
    if bDebugOutputGetUsageData: print "'".ljust(120, "-");
    oExcessiveCPUUsageDetector.ddnLastCPUTime_by_uThreadId_by_ProcessId = ddnCPUTime_by_uThreadId_by_uProcessId;
    oExcessiveCPUUsageDetector.nLastRunTime = oCdbWrapper.fnApplicationRunTime();
