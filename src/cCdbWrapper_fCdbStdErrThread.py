import re;
from dxBugIdConfig import dxBugIdConfig;
from mHTML import fsHTMLEncode;

def cCdbWrapper_fCdbStdErrThread(oCdbWrapper):
  sLine = "";
  while 1:
    sChar = oCdbWrapper.oCdbProcess.stderr.read(1);
    if sChar == "\r":
      pass; # ignored.
    elif sChar in ("\n", ""):
      if sChar == "\n" or sLine:
        for (srSourceFilePath, sURLTemplate) in oCdbWrapper.dsURLTemplate_by_srSourceFilePath.items():
          oMatch = re.search(srSourceFilePath, sLine);
          if oMatch:
            sBefore = sLine[:oMatch.start()];
            sPath = oMatch.group(0);
            sURL = (sURLTemplate % oMatch.groupdict()).replace("\\", "/");
            sAfter = sLine[oMatch.end():];
            sLineHTML = "<span class=\"CDBStdErr\">%s<a target=\"_blank\" href=\"%s\">%s</a>%s</span><br/>" % \
                (fsHTMLEncode(sBefore), sURL, fsHTMLEncode(sPath), fsHTMLEncode(sAfter));
            break;
        else:
          sLineHTML = "<span class=\"CDBStdErr\">%s</span><br/>" % fsHTMLEncode(sLine);
        oCdbWrapper.asCdbStdIOBlocksHTML[-1] += sLineHTML;
        if dxBugIdConfig["bOutputStdErr"]:
          print "cdb:stderr>%s" % repr(sLine)[1:-1];
        if oCdbWrapper.rImportantStdErrLines and oCdbWrapper.rImportantStdErrLines.match(sLine):
          oCdbWrapper.sImportantOutputHTML += sLineHTML;
      if sChar == "":
        break;
      sLine = "";
    else:
      sLine += sChar;
  oCdbWrapper.bCdbRunning = False;

