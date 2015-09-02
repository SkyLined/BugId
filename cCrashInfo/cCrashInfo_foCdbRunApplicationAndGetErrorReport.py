import re;
from dxCrashInfoConfig import dxCrashInfoConfig;
from cErrorReport import cErrorReport;
from cException import cException;
from cProcess import cProcess;

def cCrashInfo_foCdbRunApplicationAndGetErrorReport(oCrashInfo):
  # The application is now started, read its output until an exception is detected:
  oErrorReport = None;
  while len(oCrashInfo._auProcessIds) > 0:
    oCrashInfo._fApplicationRunningCallback(True);
    asOutput = oCrashInfo._fasSendCommandAndReadOutput("g");
    oCrashInfo._fApplicationRunningCallback(False);
    if not oCrashInfo._bCdbRunning: return None;
    # Get current process id and binary name
    uCurrentProcessId, sBinaryName = cProcess.ftxGetCurrentProcessIdAndBinaryName(oCrashInfo);
    if not oCrashInfo._bCdbRunning: return None;
    # Find out what event caused the debugger break
    asLastEventOutput = oCrashInfo._fasSendCommandAndReadOutput(".lastevent");
    if not oCrashInfo._bCdbRunning: return None;
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
      # A process was created or terminated.
      sCreateExit, sProcessIdHex = oCreateExitProcessMatch.groups();
      uProcessId = int(sProcessIdHex, 16);
      assert uProcessId == uCurrentProcessId, "Current process changed from %d to %d" % (uProcessId, uCurrentProcessId);
      if sCreateExit == "Create":
        oCrashInfo._auProcessIds.append(uProcessId);
        if dxCrashInfoConfig.get("bOutputProcesses", False):
          print "* New sub-process %d/0x%X (%s)" % (uProcessId, uProcessId, sBinaryName);
      else:
        assert uProcessId in oCrashInfo._auProcessIds, \
            "Missing process id: %\r\n%s" % (uProcessId, "\r\n".join(oCrashInfo.asCdbIO));
        oCrashInfo._auProcessIds.remove(uProcessId);
        oCrashInfo._uLastProcessId = uProcessId;
        if dxCrashInfoConfig.get("bOutputProcesses", False):
          print "* Terminated process %d/0x%X (%s)" % (uProcessId, uProcessId, sBinaryName);
    else:
      # A fatal exception was detected.
      # Turn off noizy symbol loading; it can mess up the output of commands, making it unparsable.
      asOutput = oCrashInfo._fasSendCommandAndReadOutput("!sym quiet");
      if not oCrashInfo._bCdbRunning: return None;
      # Get exception description and code...
      oExceptionMatch = re.match(r"^(.*?) \- code ([0-9A-F]+) \(!*\s*(first|second) chance\s*!*\)$", sEvent, re.I);
      assert oExceptionMatch, "The last event was not recognized:\r\n%s" % "\r\n".join(asLastEventOutput);
      sDescription, sCode, sChance = oExceptionMatch.groups();
      uCode = int(sCode, 16);
      # Report that analysis is starting...
      oCrashInfo._fExceptionDetectedCallback(uCode, sDescription);
      # Gather relevant information...
      oProcess = cProcess.foCreate(oCrashInfo, uCurrentProcessId, sBinaryName);
      oException = cException.foCreate(oCrashInfo, oProcess, uCode, sDescription);
      if not oCrashInfo._bCdbRunning: return None;
      # Save the exception report for returning when we're finished.
      oErrorReport = cErrorReport.foCreateFromException(oCrashInfo, oException);
      if not oCrashInfo._bCdbRunning: return None;
      # Stop the debugger if there was a fatal error that needs to be reported.
      if oErrorReport is not None:
        break;
      # Turn on noizy symbol loading if it was enabled.
      if dxCrashInfoConfig.get("bDebugSymbolLoading", False):
        asOutput = oCrashInfo._fasSendCommandAndReadOutput("!sym noizy");
        if not oCrashInfo._bCdbRunning: return None;
    # LOOP: continue the application.
  # Terminate cdb.
  oCrashInfo._bCdbTerminated = True;
  oCrashInfo._fasSendCommandAndReadOutput("q");
  assert not oCrashInfo._bCdbRunning, "Debugger did not terminate when requested";
  return oErrorReport;
