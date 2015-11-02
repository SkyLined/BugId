import re;
from dxBugIdConfig import dxBugIdConfig;
from mHTML import fsHTMLEncode;

def cCdbWrapper_fasReadOutput(oCdbWrapper):
  sLine = "";
  asLines = [];
  while 1:
    sChar = oCdbWrapper.oCdbProcess.stdout.read(1);
    if sChar == "\r":
      pass; # ignored.
    elif sChar in ("\n", ""):
      if sChar == "\n" or sLine:
        if dxBugIdConfig["bOutputStdOut"]:
          print "cdb>%s" % repr(sLine)[1:-1];
        # Add the line to the current block of I/O
        oCdbWrapper.asHTMLCdbStdIOBlocks[-1] += "<span class=\"CDBOutput\">%s</span><br/>" % fsHTMLEncode(sLine)
        asLines.append(sLine);
      if sChar == "":
        break;
      sLine = "";
    else:
      sLine += sChar;
      # Detect the prompt.
      oPromptMatch = re.match("^\d+:\d+(:x86)?> $", sLine);
      if oPromptMatch:
        oCdbWrapper.sCurrentISA = oPromptMatch.group(1) and "x86" or oCdbWrapper.sCdbISA;
        if dxBugIdConfig["bOutputStdOut"]:
          print "cdb>%s" % repr(sLine)[1:-1];
        # The prompt is stored in a new block of I/O
        oCdbWrapper.asHTMLCdbStdIOBlocks.append("<span class=\"CDBPrompt\">%s</span>" % fsHTMLEncode(sLine));
        return asLines;
  oCdbWrapper.bCdbRunning = False;
  return None;
