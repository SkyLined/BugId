import re;
from dxBugIdConfig import dxBugIdConfig;

def cCdbWrapper_fasSendCommandAndReadOutput(oCdbWrapper, sCommand):
  if dxBugIdConfig["bOutputStdIO"] or dxBugIdConfig["bOutputCommands"]:
    print "cdb<%s" % repr(sCommand)[1:-1];
  try:
    oCdbWrapper.oCdbProcess.stdin.write("%s\r\n" % sCommand);
  except Exception, oException:
    oCdbWrapper.bCdbRunning = False;
    return None;
  # Add the command to the last line of the current output block; this block should contain only one line that has the
  # cdb prompt.
  oCdbWrapper.aasCdbStdIO[-1][-1] += sCommand;
  asOutput = oCdbWrapper.fasReadOutput();
  # Detect obvious errors executing the command. (this will not catch everything, but does help development)
  assert asOutput is None or len(asOutput) != 1 or not re.match(r"^\s*\^ .*$", asOutput[0]), \
      "There was a problem executing the command %s: %s\r\n%s" % \
      (repr(sCommand), repr(asOutput), \
          "\r\n".join(["\r\n".join(asCdbStdIO) for asCdbStdIO in oCdbWrapper.aasCdbStdIO]));
  return asOutput;
