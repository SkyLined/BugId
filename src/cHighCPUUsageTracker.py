import threading;
from cCdbWrapper_fGet_ddtnCPUTime_and_nRunTime_by_uThreadId_by_uProcessId import cCdbWrapper_fGet_ddtnCPUTime_and_nRunTime_by_uThreadId_by_uProcessId;
from dxBugIdConfig import dxBugIdConfig;

class cHighCPUUsageTracker(object):
  def __init__(oHighCPUUsageTracker, oCdbWrapper):
    oHighCPUUsageTracker.oCdbWrapper = oCdbWrapper;
    oHighCPUUsageTracker.oLock = threading.Lock();
    oHighCPUUsageTracker.xStartTimeout = None;
    oHighCPUUsageTracker.xCheckUsageTimeout = None;
    oHighCPUUsageTracker.xCheckWormResultTimeout = None;
    oHighCPUUsageTracker.uBugBreakpointId = None;
  
  def fStartTimeout(oHighCPUUsageTracker, nTimeout):
    oCdbWrapper = oHighCPUUsageTracker.oCdbWrapper;
    oHighCPUUsageTracker.oLock.acquire();
    try:
      # Stop any analysis in progress...
      if oHighCPUUsageTracker.xStartTimeout is not None:
        oCdbWrapper.fClearTimeout(oHighCPUUsageTracker.xStartTimeout);
        oHighCPUUsageTracker.xStartTimeout = None;
      if oHighCPUUsageTracker.xCheckUsageTimeout is not None:
        oCdbWrapper.fClearTimeout(oHighCPUUsageTracker.xCheckUsageTimeout);
        oHighCPUUsageTracker.xCheckUsageTimeout = None;
        oHighCPUUsageTracker.xPreviousData = None; # Previous data is no longer valid.
      if oHighCPUUsageTracker.xCheckWormResultTimeout is not None:
        oCdbWrapper.fClearTimeout(oHighCPUUsageTracker.xCheckWormResultTimeout);
        oHighCPUUsageTracker.xCheckWormResultTimeout = None;
        oHighCPUUsageTracker.fWormCleanup(); # Worm requires a bit of cleanup
        if not oCdbWrapper.bCdbRunning: return;
      if oHighCPUUsageTracker.uBugBreakpointId is not None:
        oCdbWrapper.fReleaseBreakpointId(oHighCPUUsageTracker.uBugBreakpointId);  # This executes a cdb command, so check if cdb is still running later.
        oHighCPUUsageTracker.uBugBreakpointId = None;                                              #
        if not oCdbWrapper.bCdbRunning: return;                                   # <- check here -'
      if nTimeout is not None:
        oHighCPUUsageTracker.xStartTimeout = oCdbWrapper.fxSetTimeout(nTimeout, oHighCPUUsageTracker.fStart);
    finally:
      oHighCPUUsageTracker.oLock.release();
  
  def fStart(oHighCPUUsageTracker):
    print "@@@ Start high CPU usage checks...";
    oCdbWrapper = oHighCPUUsageTracker.oCdbWrapper;
    oHighCPUUsageTracker.xPreviousData = cCdbWrapper_fGet_ddtnCPUTime_and_nRunTime_by_uThreadId_by_uProcessId(oCdbWrapper);
    oHighCPUUsageTracker.oLock.acquire();
    try:
      nTimeout = dxBugIdConfig["nHighCPUsuageCheckInterval"];
      oHighCPUUsageTracker.xCheckUsageTimeout = oCdbWrapper.fxSetTimeout(nTimeout, oHighCPUUsageTracker.fCheckUsage);
    finally:
      oHighCPUUsageTracker.oLock.release();
  
  def fCheckUsage(oHighCPUUsageTracker):
    print "@@@ Checking for high CPU usage...";
    oCdbWrapper = oHighCPUUsageTracker.oCdbWrapper;
    oHighCPUUsageTracker.oLock.acquire();
    try:
      if oHighCPUUsageTracker.xCheckUsageTimeout is None:
        return; # Analysis was stopped because a new timeout was set.
      oHighCPUUsageTracker.xCheckUsageTimeout = None;
      ddtPrevious_nCPUTime_and_nRunTime_by_uThreadId_by_uProcessId = oHighCPUUsageTracker.xPreviousData;
      ddtCurrent_nCPUTime_and_nRunTime_by_uThreadId_by_uProcessId = oHighCPUUsageTracker.xPreviousData = \
          cCdbWrapper_fGet_ddtnCPUTime_and_nRunTime_by_uThreadId_by_uProcessId(oCdbWrapper);
      # Find out which thread in which process used the most CPU by comparing previous CPU usage and run-time values to
      # current values for all threads in all processes that exist in both data sets.
      nMaxCPUPercent = -1;
      for (uProcessId, dtCurrent_nCPUTime_and_nRunTime_by_uThreadId) in ddtCurrent_nCPUTime_and_nRunTime_by_uThreadId_by_uProcessId.items():
        if uProcessId in ddtPrevious_nCPUTime_and_nRunTime_by_uThreadId_by_uProcessId:
          dtPrevious_nCPUTime_and_nRunTime_by_uThreadId = ddtPrevious_nCPUTime_and_nRunTime_by_uThreadId_by_uProcessId[uProcessId];
          for (uThreadId, tCurrent_nCPUTime_and_nRunTime) in dtCurrent_nCPUTime_and_nRunTime_by_uThreadId.items():
            # nRunTime can be None due to a bug in cdb. In such cases, usage percentage cannot be calculated
            if tCurrent_nCPUTime_and_nRunTime[1] is not None and uThreadId in dtPrevious_nCPUTime_and_nRunTime_by_uThreadId:
              tPrevious_nCPUTime_and_nRunTime = dtPrevious_nCPUTime_and_nRunTime_by_uThreadId[uThreadId];
              if tPrevious_nCPUTime_and_nRunTime[1] is not None:
                nCPUTime = tCurrent_nCPUTime_and_nRunTime[0] - tPrevious_nCPUTime_and_nRunTime[0];
                nRunTime = tCurrent_nCPUTime_and_nRunTime[1] - tPrevious_nCPUTime_and_nRunTime[1];
                nCPUPercent = nRunTime > 0 and (100.0 * nCPUTime / nRunTime) or 0;
                if nCPUPercent > nMaxCPUPercent:
                  nMaxCPUPercent = nCPUPercent;
                  uMaxCPUProcessId = uProcessId;
                  uMaxCPUThreadId = uThreadId;
# Use for debugging
#                print "   pid %4d tid %4d CPU: %6.3f=>%6.3f (%4.3f) RUN: %6.3f=>%6.3f (%4.3f) USE: %3.0f%%" % (
#                  uProcessId, uThreadId,
#                  tPrevious_nCPUTime_and_nRunTime[0], tCurrent_nCPUTime_and_nRunTime[0], nCPUTime,
#                  tPrevious_nCPUTime_and_nRunTime[1], tCurrent_nCPUTime_and_nRunTime[1], nRunTime,
#                  nCPUPercent
#                );
      print "@@@ Max CPU usage is %d%% by process %d/0x%X, thread %d/0x%X..." % \
          (nMaxCPUPercent, uMaxCPUProcessId, uMaxCPUProcessId, uMaxCPUThreadId, uMaxCPUThreadId);
      # If any thread used too much CPU time
      if nMaxCPUPercent > dxBugIdConfig["nHighCPUsuagePercent"]:
        # Find out which function is using too much CPU.
# Use for debugging
#        print "*** Max CPU: %d%% for pid %d, tid %d" % (nMaxCPUPercent, uMaxCPUProcessId, uMaxCPUThreadId);
        oHighCPUUsageTracker.fInstallWorm(uMaxCPUProcessId, uMaxCPUThreadId);
      else:
        # No thread suspected of high CPU usage: measure CPU usage over anopther interval.
        nTimeout = dxBugIdConfig["nHighCPUsuageCheckInterval"];
        oHighCPUUsageTracker.xCheckUsageTimeout = oCdbWrapper.fxSetTimeout(nTimeout, oHighCPUUsageTracker.fCheckUsage);
    finally:
      oHighCPUUsageTracker.oLock.release();
    
  def fInstallWorm(oHighCPUUsageTracker, uProcessId, uThreadId):
    print "@@@ Installing high CPU usage worm...";
    oCdbWrapper = oHighCPUUsageTracker.oCdbWrapper;
    # High CPU usage is caused by some code running in a loop. Because this loop is never broken, the function
    # containing the looping code will not return to its caller. The easiest way to get a useful BugId is to
    # determine an address of an instruction inside the looping code in this function, set a breakpoint and get
    # a stack as with other issues. The exact instruction may change between runs, but the name of the function on
    # the stack should not, and the latter is used in the stack hash.
    # To do this, we create a breakpoint "worm" inside the looping code. Whenever this breakpoint is hit, it moves up
    # the stack by removing the breakpoint from its current location and setting a new breakpoint at the current
    # return address. Should the code in which the breakpoint used to be return, the new breakpoint will be hit and
    # the worm moves up the stack again. If the code does not return, the breakpoint will no longer move up.
    # Every time a breakpoint is hit, its location is saved in a variable. After running some time, the application
    # is interrupted and the value of this variable is read to determine the location of an instruction inside the
    # function that does not return. At this point a breakpoint is set there, which will trigger a bug report.
    # Select the relevant process and thread
    oCdbWrapper.fSelectProcessAndThread(uProcessId, uThreadId);
    if not oCdbWrapper.bCdbRunning: return;
    oHighCPUUsageTracker.uWormProcessId = uProcessId;
    oHighCPUUsageTracker.uWormThreadId = uThreadId;
    oHighCPUUsageTracker.uWormBreakpointId = oCdbWrapper.fuGetBreakpointId();
    oHighCPUUsageTracker.uWormVariableId = oCdbWrapper.fuGetVariableId();
    sSetBreakpointCommand = r'r $t%d=@$ip;~. bp%d @$ra "HighCPUUsageWorm;g;";.printf "High CPU usage worm at %%p, next breakpoint at %%p.\r\n", @$ip, @$ra;' % \
        (oHighCPUUsageTracker.uWormVariableId, oHighCPUUsageTracker.uWormBreakpointId);
    # Create the worm and start it.
    sSetAliasCommand = 'aS HighCPUUsageWorm "%s";' % sSetBreakpointCommand.replace("\\", "\\\\").replace('"', '\\"');
    asNothing = oCdbWrapper.fasSendCommandAndReadOutput(sSetAliasCommand, bIsRelevantIO = False);
    if not oCdbWrapper.bCdbRunning: return;
    assert len(asNothing) == 0, "Unexpected set high CPU usage worm alias output:\r\n%s" % "\r\n".join(asNothing);
    asNothing = oCdbWrapper.fasSendCommandAndReadOutput("HighCPUUsageWorm", bIsRelevantIO = False);
    if not oCdbWrapper.bCdbRunning: return;
    assert len(asNothing) == 1, "Unexpected run high CPU usage worm output:\r\n%s" % "\r\n".join(asNothing);
    # Set a timeout after which we check what the worm found.
    nTimeout = dxBugIdConfig["nHighCPUsuageCheckInterval"];
    oHighCPUUsageTracker.xCheckWormResultTimeout = oCdbWrapper.fxSetTimeout(nTimeout, oHighCPUUsageTracker.fCheckWormResult);
  
  def fCheckWormResult(oHighCPUUsageTracker):
    print "@@@ Checking high CPU usage worm results...";
    oCdbWrapper = oHighCPUUsageTracker.oCdbWrapper;
    oHighCPUUsageTracker.oLock.acquire();
    try:
      if oHighCPUUsageTracker.xCheckWormResultTimeout is None:
        return; # Analysis was stopped because a new timeout was set.
      oHighCPUUsageTracker.xCheckWormResultTimeout = None;
      # Select the relevant process and thread
      oCdbWrapper.fSelectProcessAndThread(oHighCPUUsageTracker.uWormProcessId, oHighCPUUsageTracker.uWormThreadId);
      if not oCdbWrapper.bCdbRunning: return;
      # Read the last instruction pointer at which a worm breakpoint was hit.
      asHighCPUUsageLastIP = oCdbWrapper.fasSendCommandAndReadOutput('.printf "%%p\\n", @$t%d' % oHighCPUUsageTracker.uWormVariableId, bIsRelevantIO = False);
      if not oCdbWrapper.bCdbRunning: return;
      assert len(asHighCPUUsageLastIP) == 1, "Unexpected get high CPU usage worm last instruction pointer output:\r\n%s" % "\r\n".join(asHighCPUUsageLastIP);
      uHighCPUUsageLastIP = long(asHighCPUUsageLastIP[0], 16);
      # Set a breakpoint when the loop next hits the iunstruction we want to report a bug at.
      print "@@@ Adding high CPU usage bug breakpoint at address 0x%X..." % uHighCPUUsageLastIP;
      oHighCPUUsageTracker.uBugBreakpointId = oCdbWrapper.fuAddBugBreakpoint(
          sAddress = "0x%X" % uHighCPUUsageLastIP,
          sBugTypeId = "CPUUsage",
          sBugDescription = "The application is using excessive CPU, most likely caused by a code loop that does not end.",
          sSecurityImpact = None,
#          uProcessId = oHighCPUUsageTracker.uWormProcessId, # Already selected
#          uThreadId = oHighCPUUsageTracker.uWormThreadId,
      );
      if not oCdbWrapper.bCdbRunning: return;
      oHighCPUUsageTracker.fWormCleanup();
      if not oCdbWrapper.bCdbRunning: return;
    finally:
      oHighCPUUsageTracker.oLock.release();
  
  def fWormCleanup(oHighCPUUsageTracker):
    oCdbWrapper = oHighCPUUsageTracker.oCdbWrapper;
    oHighCPUUsageTracker.uWormProcessId = None;
    oHighCPUUsageTracker.uWormThreadId = None;
    oCdbWrapper.fReleaseBreakpointId(oHighCPUUsageTracker.uWormBreakpointId); # This executes a cdb command, so check if cdb is still running later.
    oHighCPUUsageTracker.uWormBreakpointId = None;
    oCdbWrapper.fReleaseVariableId(oHighCPUUsageTracker.uWormVariableId);
    oHighCPUUsageTracker.uWormVariableId = None;
