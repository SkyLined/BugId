import re;
from dxBugIdConfig import dxBugIdConfig;
from mHTML import fsHTMLEncode;

dsURLTemplate_by_srSourceFilePath = {
  r"c:/builds/moz2_slave/\w+/build/src/(?P<path>[\w\/]+\.\w+):(?P<lineno>\d+)":
      "https://dxr.mozilla.org/mozilla-central/source/%(path)s#%(lineno)s",
};

rImportantLines = re.compile("|".join(["^%s$" % x for x in [
  r"Assertion failure: .*",
]]));

def cCdbWrapper_fCdbStdErrThread(oCdbWrapper):
  sLine = "";
  while 1:
    sChar = oCdbWrapper.oCdbProcess.stderr.read(1);
    if sChar == "\r":
      pass; # ignored.
    elif sChar in ("\n", ""):
      if sChar == "\n" or sLine:
        for (srSourceFilePath, sURLTemplate) in dsURLTemplate_by_srSourceFilePath.items():
          oMatch = re.match(srSourceFilePath, sLine);
          if oMatch:
            sURL = sURLTemplate % oMatch.groupdict();
            sLineHTML = "<a href=\"%s\" class=\"CDBStdErr\">%s</a><br/>" % (sURL, fsHTMLEncode(sLine));
            break;
        else:
          sLineHTML = "<span class=\"CDBStdErr\">%s</span><br/>" % fsHTMLEncode(sLine);
        oCdbWrapper.asHTMLCdbStdIOBlocks[-1] += sLineHTML;
        if dxBugIdConfig["bOutputStdErr"]:
          print "cdb:stderr>%s" % repr(sLine)[1:-1];
        if rImportantLines.match(sLine):
          oCdbWrapper.asImportantStdErrLinesHTML.append(sLineHTML);
      if sChar == "":
        break;
      sLine = "";
    else:
      sLine += sChar;
  oCdbWrapper.bCdbRunning = False;

