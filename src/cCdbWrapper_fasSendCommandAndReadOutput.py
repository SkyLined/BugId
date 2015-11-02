import re;
from dxBugIdConfig import dxBugIdConfig;
from mHTML import fsHTMLEncode;

def cCdbWrapper_fasSendCommandAndReadOutput(oCdbWrapper, sCommand):
  if dxBugIdConfig["bOutputStdIn"]:
    print "cdb<%s" % repr(sCommand)[1:-1];
  try:
    oCdbWrapper.oCdbProcess.stdin.write("%s\r\n" % sCommand);
  except Exception, oException:
    oCdbWrapper.bCdbRunning = False;
    return None;
  # Add the command to the current output block; this block should contain only one line that has the cdb prompt.
  oCdbWrapper.asHTMLCdbStdIOBlocks[-1] += "<span class=\"CDBCommand\">%s</span><br/>" % fsHTMLEncode(sCommand);
  asOutput = oCdbWrapper.fasReadOutput();
  # Detect obvious errors executing the command. (this will not catch everything, but does help development)
  assert asOutput is None or len(asOutput) != 1 or not re.match(r"^\s*\^ .*$", asOutput[0]), \
      "There was a problem executing the command %s:\r\n%s" % \
      (repr(sCommand), "\r\n".join([repr(sLine) for sLine in asOutput]));
  return asOutput;
