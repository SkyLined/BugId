import re;

def cCdbWrapper_fGet_ddtnCPUTime_and_nRunTime_by_uThreadId_by_uProcessId(oCdbWrapper):
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
  return ddtnCPUTime_and_nRunTime_by_uThreadId_by_uProcessId;
