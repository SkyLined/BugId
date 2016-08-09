import re, threading;
from dxBugIdConfig import dxBugIdConfig;

def cCdbWrapper_fasSendCommandAndReadOutput(oCdbWrapper, sCommand,
    bOutputIsInformative = False,
    bShowOnlyCommandOutput = False,
    bOutputCanContainApplicationOutput = False,
    bHandleSymbolLoadErrors = True,
):
  # Commands can only be execute from within the cCdbWrapper.fCdbStdInOutThread call.
  assert  threading.currentThread() == oCdbWrapper.oCdbStdInOutThread, \
      "Commands can only be sent to cdb from within a cCdbWrapper.fCdbStdInOutThread call.";
  if dxBugIdConfig["bOutputStdIn"]:
    print "cdb<%s" % repr(sCommand)[1:-1];
  try:
    oCdbWrapper.oCdbProcess.stdin.write("%s\r\n" % sCommand);
  except Exception, oException:
    oCdbWrapper.bCdbRunning = False;
    return None;
  if oCdbWrapper.bGetDetailsHTML:
    bAddCommandToHTML = oCdbWrapper.bGetDetailsHTML and (
      dxBugIdConfig["bShowAllCdbCommandsInReport"] or (
        (bOutputIsInformative and dxBugIdConfig["bShowInformativeCdbCommandsInReport"])
        and not bShowOnlyCommandOutput
      )
    ) 
    if bAddCommandToHTML:
      # Add the command to the current output block; this block should contain only one line that has the cdb prompt.
      oCdbWrapper.asCdbStdIOBlocksHTML[-1] += "<span class=\"CDBCommand\">%s</span><br/>" % oCdbWrapper.fsHTMLEncode(sCommand);
    else:
      # Remove the second to last output block: it contains the cdb prompt that is linked to this command and thus it
      # has become irrelevant.
      oCdbWrapper.asCdbStdIOBlocksHTML.pop(-1);
  # The following command will always add a new output block with the new cdb prompt, regardless of bDoNotSaveIO.
  asOutput = oCdbWrapper.fasReadOutput(
    bOutputIsInformative = bOutputIsInformative,
    bOutputCanContainApplicationOutput = bOutputCanContainApplicationOutput,
    bHandleSymbolLoadErrors = bHandleSymbolLoadErrors
  );
  # Detect obvious errors executing the command. (this will not catch everything, but does help development)
  assert asOutput is None or len(asOutput) == 0 or not re.match(r"^(\s*\^ .*|Couldn't resolve error at .+)$", asOutput[0]), \
      "There was a problem executing the command %s:\r\n%s" % \
      (repr(sCommand), "\r\n".join([repr(sLine) for sLine in asOutput]));
  return asOutput;
