import json, re, sys, threading;
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
    print "  --ci.bSaveReport=true";
    print "    Save a HTML formatted crash report using the crash id as the file name.";
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
        sSettingName, sValue = asArguments[0].split("=", 1);
        xValue = json.loads(sValue);
        asGroupNames = sSettingName[2:].split("."); # last element is not a group name
        sFullName = ".".join(asGroupNames);
        sSettingName = asGroupNames.pop();          # so pop it.
        dxConfigGroup = dxConfig;
        asHandledGroupNames = [];
        for sGroupName in asGroupNames:
          asHandledGroupNames.append(sGroupName);
          assert sGroupName in dxConfigGroup, \
              "Unknown config group %s in setting name %s." % (repr(".".join(asHandledGroupNames)), repr(sFullName));
          dxConfigGroup = dxConfigGroup.get(sGroupName, {});
          asHandledGroupNames.append(sGroupName);
        assert sSettingName in dxConfigGroup, \
            "Unknown setting name %s%s." % (sSettingName, \
                len(asHandledGroupNames) > 0 and " in config group %s" % repr(".".join(asHandledGroupNames)) or "");
        if dxConfigGroup[sSettingName] != xValue:
          print "* Changed config setting %s from %s to %s." % (sFullName, repr(dxConfigGroup[sSettingName]), repr(xValue));
          dxConfigGroup[sSettingName] = xValue;
    else:
      raise AssertionError("Unknown switch %s" % repr(asArguments[0]));
    asArguments.pop(0);
  asApplicationCommandLine = len(asArguments) and asArguments or None;
  
  oFinishedEvent = threading.Event();
  
  def fApplicationStartedHandler():
    if asApplicationCommandLine:
      print "* The application was started successfully and is running...";
    else:
      print "* The application was resumed successfully and is running...";
  
  def fFatalExceptionDetectedHandler(uCode, sDescription):
    print "* A fatal exception 0x%X (%s) was detected and is being analyzed..." % (uCode, sDescription);
  
  def fFinishedHandler(oErrorReport):
    if oErrorReport:
      print;
      print "%16s: %s" % ("Id", oErrorReport.sId);
      print "%16s: %s" % ("Description", oErrorReport.sDescription);
      print "%16s: %s" % ("Security impact", oErrorReport.sSecurityImpact);
      if dxCIConfig.get("bSaveReport", False):
        dsMap = {'"': "''", "<": "[", ">": "]", "\\": "!", "/": "!", "?": "!", "*": ".", ":": ";", "|": "!"};
        sFileName = "".join([dsMap.get(sChar, sChar) for sChar in oErrorReport.sId]) + ".html";
        oFile = open(sFileName, "wb");
        try:
          oFile.write(oErrorReport.sHTMLDetails);
        finally:
          oFile.close();
        print "%16s: %s (%d bytes)" % ("Error report", sFileName, len(oErrorReport.sHTMLDetails));
    else:
      print "* The application has terminated without crashing.";
    oFinishedEvent.set();
  
  def fInternalExceptionHandler(oException):
    print "* An internal exception occured...";
    oFinishedEvent.set();
  
  if asApplicationCommandLine:
    print "* CrashInfo is starting the application...";
  else:
    print "* CrashInfo is attaching to the application...";
  oCrashInfo = cCrashInfo(
    asApplicationCommandLine = asApplicationCommandLine,
    auApplicationProcessIds = auApplicationProcessIds,
    sApplicationISA = "irrelevant",
    asSymbolServerURLs = [],
    fApplicationStartedCallback = fApplicationStartedHandler,
    fFatalExceptionDetectedCallback = fFatalExceptionDetectedHandler,
    fFinishedCallback = fFinishedHandler,
    fInternalExceptionCallback = fInternalExceptionHandler,
  );
  oFinishedEvent.wait();
