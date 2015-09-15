import json, re, os, sys, threading;
from cCrashInfo import cCrashInfo;
from dxConfig import dxConfig;
dxCIConfig = dxConfig.get("ci", {});

if __name__ == "__main__":
  asArguments = sys.argv[1:];
  if len(asArguments) == 0:
    print "Usage:";
    print "  ci.py [options] --pids=[comma separated list of process ids]";
    print "    Attach debugger to the process(es) provided in the list. The processes must";
    print "    all have been suspended, as they will be resumed by the debugger.";
    print "  ci.py [options] path\\to\\executable.exe [arguments]";
    print "    Start the executable in the debugger with the provided arguments.";
    print;
    print "Options:";
    print "  --ci.bSaveReport=false";
    print "    Do not save a HTML formatted crash report.";
    print "  --CrashInfo.bOutputIO=true";
    print "    Show verbose cdb output and input during debugging.";
    print "  --CrashInfo.asSymbolCachePaths=[\"C:\\Symbols\"]";
    print "    Use C:\\Symbols to cache synmbol (.pdb) files.";
    print "  See dxConfig.py and cCrashInfo\dxCrashInfoConfig.py for a list of settings.";
    print "  All values must be valid JSON of the appropriate type. No checks are made";
    print "  to ensure this. Providing illegal values will most likely result in";
    print "  exceptions at some point during crash analysis. You have been warned.";
    sys.exit(1);
  auApplicationProcessIds = None;
  while len(asArguments) and asArguments[0].startswith("--"):
    if asArguments[0].startswith("--"):
      if asArguments[0].startswith("--pids="):
        auApplicationProcessIds = [int(x) for x in asArguments[0].split("=", 1)[1].split(",")];
      else:
        sSettingName, sValue = asArguments[0][2:].split("=", 1);
        xValue = json.loads(sValue);
        asGroupNames = sSettingName.split("."); # last element is not a group name
        sFullName = ".".join(asGroupNames);
        sSettingName = asGroupNames.pop();          # so pop it.
        dxConfigGroup = dxConfig;
        asHandledGroupNames = [];
        for sGroupName in asGroupNames:
          asHandledGroupNames.append(sGroupName);
          assert sGroupName in dxConfigGroup, \
              "Unknown config group %s in setting name %s." % (repr(".".join(asHandledGroupNames)), repr(sFullName));
          dxConfigGroup = dxConfigGroup.get(sGroupName, {});
        assert sSettingName in dxConfigGroup, \
            "Unknown setting name %s%s." % (sSettingName, \
                len(asHandledGroupNames) > 0 and " in config group %s" % ".".join(asHandledGroupNames) or "");
        if json.dumps(dxConfigGroup[sSettingName]) == json.dumps(xValue):
          print "* The default value for config setting %s is %s." % (sFullName, repr(dxConfigGroup[sSettingName]));
        else:
          print "* Changed config setting %s from %s to %s." % (sFullName, repr(dxConfigGroup[sSettingName]), repr(xValue));
          dxConfigGroup[sSettingName] = xValue;
    else:
      raise AssertionError("Unknown switch %s" % repr(asArguments[0]));
    asArguments.pop(0);
  asApplicationCommandLine = len(asArguments) and asArguments or None;
  if asApplicationCommandLine and len(asApplicationCommandLine) == 1:
    sURL = "http://%s:28876" % os.getenv("COMPUTERNAME");
    sProgramFilesPath = os.getenv("ProgramFiles");
    sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
    sProgramFilesPath_AMD64 = os.getenv("ProgramW6432");
    asApplicationCommandLine = {
      "chrome": [r"%s\Google\Chrome\Application\chrome.exe" % sProgramFilesPath_x86, sURL, "--disable-default-apps", "--disable-extensions", "--disable-popup-blocking", "--disable-prompt-on-repost", "--force-renderer-accessibility", "--no-sandbox"],
      "firefox": [r"%s\Mozilla Firefox\firefox.exe" % sProgramFilesPath_x86, sURL, "--no-remote"],
      "msie": [r"%s\Internet Explorer\iexplore.exe" % sProgramFilesPath, sURL],
      "msie64": [r"%s\Internet Explorer\iexplore.exe" % sProgramFilesPath_AMD64, sURL],
      "msie86": [r"%s\Internet Explorer\iexplore.exe" % sProgramFilesPath_x86, sURL],
    }.get(asApplicationCommandLine[0].lower(), asApplicationCommandLine)
  
  oFinishedEvent = threading.Event();
  
  bApplicationIsStarted = asApplicationCommandLine is None; # if we're attaching the application is already started.
  def fApplicationRunningHandler():
    global bApplicationIsStarted;
    if not bApplicationIsStarted:
      # Running for the first time after being started.
      print "* The application was started successfully and is running...";
      bApplicationIsStarted = True;
    else:
      # Running after being resumed.
      print "* The application was resumed successfully and is running...";
  
  def fExceptionDetectedHandler(uCode, sDescription):
    print "* Exception code 0x%X (%s) was detected and is being analyzed..." % (uCode, sDescription);
  
  def fFinishedHandler(oErrorReport):
    if oErrorReport:
      print;
      print "Id:               %s" % oErrorReport.sId;
      print "Description:      %s" % oErrorReport.sErrorDescription;
      print "Process binary:   %s" % oErrorReport.sProcessBinaryName;
      print "Location:         %s" % oErrorReport.sLocationDescription;
      print "Security impact:  %s" % oErrorReport.sSecurityImpact;
      if dxCIConfig.get("bSaveReport", True):
        dsMap = {'"': "''", "<": "[", ">": "]", "\\": "#", "/": "#", "?": "#", "*": "#", ":": ".", "|": "#"};
        sFileNameBase = "".join([dsMap.get(sChar, sChar) for sChar in oErrorReport.sId]);
        # File name may be too long, keep trying to 
        while len(sFileNameBase) > 0:
          sFileName = sFileNameBase + ".html";
          try:
            oFile = open(sFileName, "wb");
          except IOError:
            sFileNameBase = sFileNameBase[:-1];
            continue;
          try:
            oFile.write(oErrorReport.sHTMLDetails);
          finally:
            oFile.close();
          print "Error report:     %s (%d bytes)" % (sFileName, len(oErrorReport.sHTMLDetails));
          break;
        else:
          print "Error report:     cannot be saved";
    else:
      print "* The application has terminated without crashing.";
    oFinishedEvent.set();
  
  def fInternalExceptionHandler(oException):
    print "* An internal exception occured...";
    oFinishedEvent.set();
  
  if asApplicationCommandLine:
    print "* CrashInfo is starting the application...";
    print "  Command line: %s" % " ".join(asApplicationCommandLine);
  else:
    print "* CrashInfo is attaching to the application...";
  oCrashInfo = cCrashInfo(
    asApplicationCommandLine = asApplicationCommandLine,
    auApplicationProcessIds = auApplicationProcessIds,
    asSymbolServerURLs = [],
    fApplicationRunningCallback = fApplicationRunningHandler,
    fExceptionDetectedCallback = fExceptionDetectedHandler,
    fFinishedCallback = fFinishedHandler,
    fInternalExceptionCallback = fInternalExceptionHandler,
  );
  oFinishedEvent.wait();
