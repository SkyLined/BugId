import re;
from dxCrashInfoConfig import dxCrashInfoConfig;

def cCrashInfo_fasReadOutput(oCrashInfo):
  # Read cdb output until an input prompt is detected, or cdb terminates.
  # This is a bit more complex than one might expect because I attempted to make it work with noizy symbol loading.
  # This may interject messages at any point during command execution, which are not part of the commands output and
  # have to be remove to make parsing of the output possible. Unfortuntely, it appears to be too complex to be
  # worth the effort. I've left what i did in here in case I want to try to finish it at some point.
  sLine = "";
  sCleanedLine = "";
  asCleanedLines = [];
  bNextLineIsSymbolLoaderMessage = False;
  while 1:
    sChar = oCrashInfo._oCdbProcess.stdout.read(1);
    if sChar == "\r":
      pass; # ignored.
    elif sChar in ("\n", ""):
      if sChar == "\n" or sLine:
        oCrashInfo.asCdbIO.append(sLine);
        if dxCrashInfoConfig["bOutputIO"]:
          print "cdb>%s" % repr(sLine)[1:-1];
      if sChar == "":
        break;
      sLine = "";
      if sCleanedLine:
        oLineEndsWithWarning = re.match(r"^(.*)\*\*\* WARNING: Unable to verify checksum for .*$", sCleanedLine);
        if oLineEndsWithWarning:
          # Sample output:
          # 
          # |00000073`ce10fda0  00007ff7`cf312200*** WARNING: Unable to verify checksum for CppException_x64.exe
          # | CppException_x64!cException::`vftable'
          # The warning and a "\r\n" appear in the middle of a line od output and need to be removed. The interrupted
          # output continues on the next line.
          sCleanedLine = oLineEndsWithWarning.group(1);
        else:
          oSymbolLoaderMessageMatch = re.match(r"^(?:%s)$" % "|".join([
            r"SYMSRV: .+",
            r"\s*\x08+\s+(?:copied\s*|\d+ percentSYMSRV: .+)",
            r"DBGHELP: .+?( \- (?:private|public) symbols(?: & lines)?)?\s*", # matched
            r"\*\*\*.*",
           ]), sCleanedLine);
          # Sample output:
          # |SYMSRV:  c:\symbols\chakra.pdb\5249D6A2684341B79F239B9E6150169C1\chakra.pdb not found
          # |DBGHELP: \\server\symbols\chakra.pdb\5249D6A2684341B79F239B9E6150169C1\chakra.pdb cached to c:\symbols\chakra.pdb\5249D6A2684341B79F239B9E6150169C1\chakra.pdb
          # |DBGHELP: chakra - public symbols  
          # |        c:\symbols\chakra.pdb\5249D6A2684341B79F239B9E6150169C1\chakra.pdb
          # |*** ERROR: Module load completed but symbols could not be loaded for C:\Windows\System32\Macromed\Flash\Flash.ocx
          # |*************************************************************************
          # |***                                                                   ***
          # |***                                                                   ***
          # |***    Either you specified an unqualified symbol, or your debugger   ***
          # |***    doesn't have full symbol information.  Unqualified symbol      ***
          # |***    resolution is turned off by default. Please either specify a   ***
          # |***    fully qualified symbol module!symbolname, or enable resolution ***
          if oSymbolLoaderMessageMatch:
            # The "DBGHELP:..." line may indicate that another symbol loader message line is to follow:
            bNextLineIsSymbolLoaderMessage = oSymbolLoaderMessageMatch.group(1) is not None;
          elif bNextLineIsSymbolLoaderMessage:
            bNextLineIsSymbolLoaderMessage = False;
          else:
            asCleanedLines.append(sCleanedLine);
          sCleanedLine = "";
    else:
      sLine += sChar;
      sCleanedLine += sChar;
      # Detect the prompt.
      oPromptMatch = re.match("^\d+:\d+(:x86)?> $", sCleanedLine);
      if oPromptMatch:
        if dxCrashInfoConfig["bOutputIO"]:
          print "cdb>%s" % repr(sLine)[1:-1];
        oCrashInfo.asCdbIO.append(sCleanedLine);
        return asCleanedLines;
  # Cdb stdout was closed: the process is terminating.
  assert oCrashInfo._bCdbTerminated or len(oCrashInfo._auProcessIds) == 0, \
      "Cdb terminated unexpectedly! Last output:\r\n%s" % "\r\n".join(oCrashInfo.asCdbIO[-20:]);
  oCrashInfo._bCdbRunning = False;
  return None;
