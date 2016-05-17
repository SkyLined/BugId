import re, threading;
from dxBugIdConfig import dxBugIdConfig;

class cExcessiveCPUUsageDetector(object):
  def __init__(oExcessiveCPUUsageDetector, oCdbWrapper):
    oExcessiveCPUUsageDetector.oCdbWrapper = oCdbWrapper;
    oExcessiveCPUUsageDetector.oLock = threading.Lock();
    oExcessiveCPUUsageDetector.xStartTimeout = None;
    oExcessiveCPUUsageDetector.xCheckUsageTimeout = None;
    oExcessiveCPUUsageDetector.xCheckWormResultTimeout = None;
    oExcessiveCPUUsageDetector.uBugBreakpointId = None;
  
  def fStartTimeout(oExcessiveCPUUsageDetector, nTimeout):
#    print "@@@ Starting excessive CPU usage checks in %d seconds..." % nTimeout;
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    oExcessiveCPUUsageDetector.oLock.acquire();
    try:
      # Stop any analysis in progress...
      if oExcessiveCPUUsageDetector.xStartTimeout is not None:
        oCdbWrapper.fClearTimeout(oExcessiveCPUUsageDetector.xStartTimeout);
        oExcessiveCPUUsageDetector.xStartTimeout = None;
      if oExcessiveCPUUsageDetector.xCheckUsageTimeout is not None:
        oCdbWrapper.fClearTimeout(oExcessiveCPUUsageDetector.xCheckUsageTimeout);
        oExcessiveCPUUsageDetector.xCheckUsageTimeout = None;
      if oExcessiveCPUUsageDetector.xCheckWormResultTimeout is not None:
        oCdbWrapper.fClearTimeout(oExcessiveCPUUsageDetector.xCheckWormResultTimeout);
        oExcessiveCPUUsageDetector.xCheckWormResultTimeout = None;
        oExcessiveCPUUsageDetector.fWormCleanup(); # Worm requires a bit of cleanup
        if not oCdbWrapper.bCdbRunning: return;
      if oExcessiveCPUUsageDetector.uBugBreakpointId is not None:
        oCdbWrapper.fReleaseBreakpointId(oExcessiveCPUUsageDetector.uBugBreakpointId);  # This executes a cdb command, so check if cdb is still running later.
        oExcessiveCPUUsageDetector.uBugBreakpointId = None;                                              #
        if not oCdbWrapper.bCdbRunning: return;                                   # <- check here -'
      oExcessiveCPUUsageDetector.xPreviousData = None; # Previous data is no longer valid.
      if nTimeout is not None:
        oExcessiveCPUUsageDetector.xStartTimeout = oCdbWrapper.fxSetTimeout(nTimeout, oExcessiveCPUUsageDetector.fStart);
    finally:
      oExcessiveCPUUsageDetector.oLock.release();
  
  def fStart(oExcessiveCPUUsageDetector):
#    print "@@@ Start excessive CPU usage checks...";
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    oExcessiveCPUUsageDetector.fGetUsageData();
    oExcessiveCPUUsageDetector.oLock.acquire();
    try:
      nTimeout = dxBugIdConfig["nExcessiveCPUUsageCheckInterval"];
      oExcessiveCPUUsageDetector.xCheckUsageTimeout = oCdbWrapper.fxSetTimeout(nTimeout, oExcessiveCPUUsageDetector.fCheckUsage);
    finally:
      oExcessiveCPUUsageDetector.oLock.release();
  
  def fCheckUsage(oExcessiveCPUUsageDetector):
#    print "@@@ Checking for excessive CPU usage...";
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    oExcessiveCPUUsageDetector.oLock.acquire();
    try:
      if oExcessiveCPUUsageDetector.xCheckUsageTimeout is None:
        return; # Analysis was stopped because a new timeout was set.
      oExcessiveCPUUsageDetector.xCheckUsageTimeout = None;
      ddtPrevious_nCPUTime_and_nRunTime_by_uThreadId_by_uProcessId = oExcessiveCPUUsageDetector.xMostRecentData;
      oExcessiveCPUUsageDetector.fGetUsageData();
      ddtCurrent_nCPUTime_and_nRunTime_by_uThreadId_by_uProcessId = oExcessiveCPUUsageDetector.xMostRecentData;
      # Find out which thread in which process used the most CPU time by comparing previous CPU usage and
      # run time values to current values for all threads in all processes that exist in both data sets.
      nMaxCPUPercent = -1;
      nTotalCPUPercent = 0;
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
                nTotalCPUPercent += nCPUPercent;
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
# Use for debugging
#      print "*** Total CPU usage: %d%%, max: %d%% for pid %d, tid %d" % \
#          (nTotalCPUPercent, nMaxCPUPercent, uMaxCPUProcessId, uMaxCPUThreadId);
      # If all threads in all processes combined have excessive CPU usage
      if nTotalCPUPercent > dxBugIdConfig["nExcessiveCPUUsagePercent"]:
        # Find out which function is using excessive CPU time in the most active thread.
        oExcessiveCPUUsageDetector.fInstallWorm(uMaxCPUProcessId, uMaxCPUThreadId);
      else:
        # No thread suspected of excessive CPU usage: measure CPU usage over another interval.
        nTimeout = dxBugIdConfig["nExcessiveCPUUsageCheckInterval"];
        oExcessiveCPUUsageDetector.xCheckUsageTimeout = oCdbWrapper.fxSetTimeout(nTimeout, oExcessiveCPUUsageDetector.fCheckUsage);
    finally:
      oExcessiveCPUUsageDetector.oLock.release();
    
  def fInstallWorm(oExcessiveCPUUsageDetector, uProcessId, uThreadId):
#    print "@@@ Installing excessive CPU usage worm...";
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    # Excessive CPU usage is caused by some code running in a loop. Because this loop is never broken, the
    # function containing the looping code will not return to its caller. The easiest way to get a useful BugId is to
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
    oExcessiveCPUUsageDetector.uWormProcessId = uProcessId;
    oExcessiveCPUUsageDetector.uWormThreadId = uThreadId;
    oExcessiveCPUUsageDetector.uWormBreakpointId = oCdbWrapper.fuGetBreakpointId();
    oExcessiveCPUUsageDetector.uWormVariableId = oCdbWrapper.fuGetVariableId();
    sSetBreakpointCommand = "".join([
      # Save the current IP: it is the highest point on the stack reached so far.
      "r $t%d=@$ip;" % oExcessiveCPUUsageDetector.uWormVariableId,
      '.printf "Excessive CPU usage worm at %p, next breakpoint at %p.\\r\\n", @$ip, @$ra;',
# useful for debugging
#      "k 3;",
      # Set a new one-time breakpoint for the next address on the stack and the current thread. cdb may fail to get the
      # right return address, so make sure the address is valid.
      ".if ($vvalid(@$ra,1)) {",
        '~. bp%d @$ra "${/n:ExcessiveCPUUsageWorm};g;";' % oExcessiveCPUUsageDetector.uWormBreakpointId,
      "};",
    ]);
    # Create the worm code
    sSetAliasCommand = 'aS ExcessiveCPUUsageWorm "%s";' % sSetBreakpointCommand.replace("\\", "\\\\").replace('"', '\\"');
    asNothing = oCdbWrapper.fasSendCommandAndReadOutput(sSetAliasCommand, bIsRelevantIO = False);
    if not oCdbWrapper.bCdbRunning: return;
    assert len(asNothing) == 0, \
        "Unexpected set ExcessiveCPUUsageWorm alias output:\r\n%s" % "\r\n".join(asNothing);
    # Start the worm 
    asNothing = oCdbWrapper.fasSendCommandAndReadOutput("".join([
      # Save the current IP: it is the highest point on the stack reached so far.
      "r $t%d=@$ip;" % oExcessiveCPUUsageDetector.uWormVariableId,
      # Ideally, we'd run the worm code immediately, but that is not possible because cdb does not give the correct
      # return address in @$ra at this point. The reason is unknown, but if we set a breakpoint for this same location
      # the @$ra variable will be set correctly when we hit it, and the worm can start climbing up the stack.
      '~. bp%d @$ip "${/n:ExcessiveCPUUsageWorm};g;";' % oExcessiveCPUUsageDetector.uWormBreakpointId,
    ]), bIsRelevantIO = False);
    if not oCdbWrapper.bCdbRunning: return;
    assert len(asNothing) == 0, \
        "Unexpected set ExcessiveCPUUsageWorm breakpoint output:\r\n%s" % "\r\n".join(asNothing);
    # Set a timeout after which we check what the worm found.
    nTimeout = dxBugIdConfig["nExcessiveCPUUsageCheckInterval"];
    oExcessiveCPUUsageDetector.xCheckWormResultTimeout = oCdbWrapper.fxSetTimeout(nTimeout, oExcessiveCPUUsageDetector.fCheckWormResult);
  
  def fCheckWormResult(oExcessiveCPUUsageDetector):
#    print "@@@ Checking excessive CPU usage worm results...";
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    oExcessiveCPUUsageDetector.oLock.acquire();
    try:
      if oExcessiveCPUUsageDetector.xCheckWormResultTimeout is None:
        return; # Analysis was stopped because a new timeout was set.
      oExcessiveCPUUsageDetector.xCheckWormResultTimeout = None;
      # Select the relevant process and thread
      oCdbWrapper.fSelectProcessAndThread(oExcessiveCPUUsageDetector.uWormProcessId, oExcessiveCPUUsageDetector.uWormThreadId);
      if not oCdbWrapper.bCdbRunning: return;
      # Read the last instruction pointer at which a worm breakpoint was hit.
      asExcessiveCPUUsageWormLastIP = oCdbWrapper.fasSendCommandAndReadOutput('.printf "%%p\\n", @$t%d' % oExcessiveCPUUsageDetector.uWormVariableId, bIsRelevantIO = False);
      if not oCdbWrapper.bCdbRunning: return;
      assert len(asExcessiveCPUUsageWormLastIP) == 1, \
          "Unexpected get ExcessiveCPUUsageWorm last instruction pointer output:\r\n%s" % "\r\n".join(asExcessiveCPUUsageWormLastIP);
      uExcessiveCPUUsageWormLastIP = long(asExcessiveCPUUsageWormLastIP[0], 16);
      # Set a breakpoint when the loop next hits the iunstruction we want to report a bug at.
#      print "@@@ Adding excessive CPU usage bug breakpoint at address 0x%X..." % uExcessiveCPUUsageWormLastIP;
      oExcessiveCPUUsageDetector.uBugBreakpointId = oCdbWrapper.fuAddBugBreakpoint(
          sAddress = "0x%X" % uExcessiveCPUUsageWormLastIP,
          sBugTypeId = "CPUUsage",
          sBugDescription = "The application is using excessive CPU time, most likely caused by a code loop that does not end.",
          sSecurityImpact = None,
#          uProcessId = oExcessiveCPUUsageDetector.uWormProcessId, # Already selected
#          uThreadId = oExcessiveCPUUsageDetector.uWormThreadId,
      );
      if not oCdbWrapper.bCdbRunning: return;
      oExcessiveCPUUsageDetector.fWormCleanup();
      if not oCdbWrapper.bCdbRunning: return;
    finally:
      oExcessiveCPUUsageDetector.oLock.release();
  
  def fWormCleanup(oExcessiveCPUUsageDetector):
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    oExcessiveCPUUsageDetector.uWormProcessId = None;
    oExcessiveCPUUsageDetector.uWormThreadId = None;
    oCdbWrapper.fReleaseBreakpointId(oExcessiveCPUUsageDetector.uWormBreakpointId); # This executes a cdb command, so check if cdb is still running later.
    oExcessiveCPUUsageDetector.uWormBreakpointId = None;
    oCdbWrapper.fReleaseVariableId(oExcessiveCPUUsageDetector.uWormVariableId);
    oExcessiveCPUUsageDetector.uWormVariableId = None;
  
  def fGetUsageData(oExcessiveCPUUsageDetector):
    oCdbWrapper = oExcessiveCPUUsageDetector.oCdbWrapper;
    # Get the amount of CPU time each thread in each process has consumed
    ddtnCPUTime_and_nRunTime_by_uThreadId_by_uProcessId = {};
    sTimeType = None;
    for uProcessId in oCdbWrapper.auProcessIds:
      oCdbWrapper.fSelectProcessAndThread(uProcessId = uProcessId);
      if not oCdbWrapper.bCdbRunning: return;
      asThreadTimes = oCdbWrapper.fasSendCommandAndReadOutput("!runaway 7", bIsRelevantIO = False);
      if not oCdbWrapper.bCdbRunning: return;
      dnCPUTime_by_uThreadId = {};
      dtnCPUTime_and_nRunTime_by_uThreadId = ddtnCPUTime_and_nRunTime_by_uThreadId_by_uProcessId[uProcessId] = {};
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
  #          print "%4d %4d %s => %s = None" % (uProcessId, uThreadId, sLine, sTimeType);
  #        else:
  #          print "%4d %4d %s => %s = %6.3f " % (uProcessId, uThreadId, sLine, sTimeType, nTime);
          if sTimeType == "User Mode Time":
            dnCPUTime_by_uThreadId[uThreadId] = nTime;
          elif sTimeType == "Kernel Mode Time":
            dnCPUTime_by_uThreadId[uThreadId] += nTime;
          else:
            dtnCPUTime_and_nRunTime_by_uThreadId[uThreadId] = (dnCPUTime_by_uThreadId[uThreadId], nTime);
    oExcessiveCPUUsageDetector.xMostRecentData = ddtnCPUTime_and_nRunTime_by_uThreadId_by_uProcessId;
