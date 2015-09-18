import re;
from dxBugIdConfig import dxBugIdConfig;

def cCdbWrapper_fasSendCommandAndReadOutput(oCdbWrapper, sCommand):
  if dxBugIdConfig["bOutputStdIO"] or dxBugIdConfig["bOutputCommands"]:
    print "cdb<%s" % repr(sCommand)[1:-1];
  # Add command to last line, which should contain the prompt.
  oCdbWrapper.asCdbStdIO[-1] += sCommand;
  try:
    oCdbWrapper.oCdbProcess.stdin.write("%s\r\n" % sCommand);
  except Exception, oException:
    oCdbWrapper.bCdbRunning = False;
    return None;
  asOutput = oCdbWrapper.fasReadOutput();
  # Detect obvious errors executing the command. (this will not catch everything, but does help development)
  assert asOutput is None or len(asOutput) != 1 or not re.match(r"^\s*\^ .*$", asOutput[0]), \
      "There was a problem executing the command %s: %s" % (repr(sCommand), repr(asOutput));
  return asOutput;
