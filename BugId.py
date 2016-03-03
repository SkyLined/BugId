import json, re, os, sys, threading;
# The CWD may not be this script's folder; make sure it looks there for modules first:
sBaseFolderPath = os.path.dirname(__file__);
for sPath in [sBaseFolderPath] + [os.path.join(sBaseFolderPath, x) for x in ["src", "modules"]]:
  sys.path.insert(0, sPath);

from dxConfig import dxConfig;
from cBugId import cBugId;
from fsCreateFileName import fsCreateFileName;

if __name__ == "__main__":
  asArguments = sys.argv[1:];
  if len(asArguments) == 0:
    print "Usage:";
    print "  BugId.py [options] path\\to\\binary.exe [arguments]";
    print "    Start the executable in the debugger with the provided arguments.";
    print "  BugId.py [options] --pids=[comma separated list of process ids]";
    print "    Attach debugger to the process(es) provided in the list. The processes must";
    print "    all have been suspended, as they will be resumed by the debugger.";
    print;
    print "Options:";
    print "  --bSaveReport=false";
    print "    Do not save a HTML formatted crash report.";
    print "  --bSaveDump=true";
    print "    Save a dump file when a crash is detected.";
    print "  --bOutputStdIO=true";
    print "    Show verbose cdb output and input during debugging.";
    print "  --asSymbolCachePaths=[\"C:\\Symbols\"]";
    print "    Use C:\\Symbols to cache symbol (.pdb) files.";
    print "  See dxConfig.py and srv\dxBugIdConfig.py for a list of settings that you can";
    print "  change. All values must be valid JSON of the appropriate type. No checks are";
    print "  made to ensure this. Providing illegal values may result in exceptions at any";
    print "  time during execution. You have been warned.";
    os._exit(0);
  auApplicationProcessIds = None;
  while len(asArguments) and asArguments[0].startswith("--"):
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
    asArguments.pop(0);
  asApplicationCommandLine = len(asArguments) and asArguments or None;
  if asApplicationCommandLine and len(asApplicationCommandLine) == 1:
    sURL = "http://%s:28876/" % os.getenv("COMPUTERNAME");
    sProgramFilesPath = os.getenv("ProgramFiles");
    sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
    sProgramFilesPath_x64 = os.getenv("ProgramW6432");
    asApplicationCommandLine = {
      "chrome": [r"%s\Google\Chrome\Application\chrome.exe" % sProgramFilesPath_x86, sURL, "--disable-default-apps", "--disable-extensions", "--disable-popup-blocking", "--disable-prompt-on-repost", "--force-renderer-accessibility", "--no-sandbox"],
      "firefox": [r"%s\Mozilla Firefox\firefox.exe" % sProgramFilesPath_x86, sURL, "--no-remote"],
      "msie": [r"%s\Internet Explorer\iexplore.exe" % sProgramFilesPath, sURL],
      "msie64": [r"%s\Internet Explorer\iexplore.exe" % sProgramFilesPath_x64, sURL],
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
  
  if asApplicationCommandLine:
    print "* The debugger is starting the application...";
    print "  Command line: %s" % " ".join(asApplicationCommandLine);
  else:
    print "* The debugger is attaching to the application...";
  oBugId = cBugId(
    asApplicationCommandLine = asApplicationCommandLine,
    auApplicationProcessIds = auApplicationProcessIds,
    asSymbolServerURLs = [],
    fApplicationRunningCallback = fApplicationRunningHandler,
    fExceptionDetectedCallback = fExceptionDetectedHandler,
  );
  oBugId.fWait();
  if oBugId.oErrorReport:
    print "* A bug was detected in the application.";
    print;
    print "  Id:               %s" % oBugId.oErrorReport.sId;
    print "  Description:      %s" % oBugId.oErrorReport.sErrorDescription;
    print "  Process binary:   %s" % oBugId.oErrorReport.sProcessBinaryName;
    print "  Code:             %s" % oBugId.oErrorReport.sCodeDescription;
    print "  Security impact:  %s" % oBugId.oErrorReport.sSecurityImpact;
    if dxConfig["bSaveReport"]:
      sFileNameBase = fsCreateFileName(oBugId.oErrorReport.sId);
      # File name may be too long, keep trying to save it with a shorter name or output an error if that's not posible.
      while len(sFileNameBase) > 0:
        sFileName = sFileNameBase + ".html";
        try:
          oFile = open(sFileName, "wb");
        except IOError:
          sFileNameBase = sFileNameBase[:-1];
          continue;
        try:
          oFile.write(oBugId.oErrorReport.sHTMLDetails);
        finally:
          oFile.close();
        print "  Error report:     %s (%d bytes)" % (sFileName, len(oBugId.oErrorReport.sHTMLDetails));
        break;
      else:
        print "  Error report:     cannot be saved";
  else:
    print "* The application has terminated without crashing.";
