from dxBugIdConfig import dxBugIdConfig;

def cCdbWrapper_fCdbStdErrThread(oCdbWrapper):
  sLine = "";
  while 1:
    sChar = oCdbWrapper.oCdbProcess.stderr.read(1);
    if sChar == "\r":
      pass; # ignored.
    elif sChar in ("\n", ""):
      if sChar == "\n" or sLine:
        oCdbWrapper.asCdbStdErr.append(sLine);
        if dxBugIdConfig["bOutputErrIO"]:
          print "cdb:stderr>%s" % repr(sLine)[1:-1];
      if sChar == "":
        break;
      sLine = "";
    else:
      sLine += sChar;
  oCdbWrapper.bCdbRunning = False;

