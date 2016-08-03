import re;
from dxBugIdConfig import dxBugIdConfig;

dsTip_by_sErrorCode = {
  "NTSTATUS 0xC00000BB": "Are you using a 32-bit debugger with a 64-bit process?",
};

def fDetectFatalErrorsInOutput(asLines):
  for sLine in asLines:
    oCannotAttachMatch = re.match(r"^Cannot debug pid (\d+), (?:Win32 error 0n(\d+)|NTSTATUS 0x(\w+))\s*$", sLine);
    if oCannotAttachMatch:
      sProcessId, sWin32Error, sNTStatus = oCannotAttachMatch.groups();
      uProcessId = long(sProcessId);
      sErrorCode = sWin32Error and "Win32 %s" % sWin32Error or "NTSTATUS 0x%s" % sNTStatus;
      sTip = dsTip_by_sErrorCode.get(sErrorCode);
      raise AssertionError("Failed to attach to process %d/0x%X!\r\n%scdb output:\r\n%s" % \
          (uProcessId, uProcessId, sTip and "%s\r\n" % sTip or "", "\r\n".join(asLines)));

def cCdbWrapper_fasReadOutput(oCdbWrapper, bIsRelevantIO = True, bMayContainApplicationOutput = False):
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
        if re.match(r"^\(\w+\.\w+\): C\+\+ EH exception \- code \w+ \(first chance\)\s*$", sLine):
          # I cannot figure out how to detect second chance C++ exceptions without cdb outputting a line every time a
          # first chance C++ exception happens. These lines are clutter and MSIE outputs a lot of them, so they are
          # ignored here. TODO: find a way to break on second chance exceptions without getting a report about first
          # chance exceptions.
          pass; 
        else:
          if oCdbWrapper.bGetDetailsHTML and bIsRelevantIO:
            sClass = bMayContainApplicationOutput and "CDBOrApplicationStdOut" or "CDBStdOut";
            sLineHTML = "<span class=\"%s\">%s</span><br/>" % (sClass, oCdbWrapper.fsHTMLEncode(sLine));
            # Add the line to the current block of I/O
            oCdbWrapper.asCdbStdIOBlocksHTML[-1] += sLineHTML;
            # Optionally add the line to the important output
            if bMayContainApplicationOutput and oCdbWrapper.rImportantStdOutLines and oCdbWrapper.rImportantStdOutLines.match(sLine):
              oCdbWrapper.sImportantOutputHTML += sLineHTML;
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
        if oCdbWrapper.bGetDetailsHTML:
          # The prompt is stored in a new block of I/O
          oCdbWrapper.asCdbStdIOBlocksHTML.append("<span class=\"CDBPrompt\">%s</span>" % oCdbWrapper.fsHTMLEncode(sLine));
        fDetectFatalErrorsInOutput(asLines);
        return asLines;
  fDetectFatalErrorsInOutput(asLines);
  oCdbWrapper.bCdbRunning = False;
  return None;
