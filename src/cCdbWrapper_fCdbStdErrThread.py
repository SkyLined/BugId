from dxBugIdConfig import dxBugIdConfig;

def cCdbWrapper_fCdbStdErrThread(oCdbWrapper):
  sLine = "";
  while 1:
    sChar = oCdbWrapper.oCdbProcess.stderr.read(1);
    if sChar == "\r":
      pass; # ignored.
    elif sChar in ("\n", ""):
      if sChar == "\n" or sLine:
        if oCdbWrapper.bGetDetailsHTML:
          sLineHTML = "<span class=\"CDBStdErr\">%s</span><br/>" % oCdbWrapper.fsHTMLEncode(sLine);
          oCdbWrapper.asCdbStdIOBlocksHTML[-1] += sLineHTML;
          if oCdbWrapper.rImportantStdErrLines and oCdbWrapper.rImportantStdErrLines.match(sLine):
            oCdbWrapper.sImportantOutputHTML += sLineHTML;
        if dxBugIdConfig["bOutputStdErr"]:
          print "cdb:stderr>%s" % repr(sLine)[1:-1];
      if sChar == "":
        break;
      sLine = "";
    else:
      sLine += sChar;
  oCdbWrapper.bCdbRunning = False;

