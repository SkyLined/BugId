from mConsole import oConsole;

from ddxApplicationSettings_by_sKeyword import ddxApplicationSettings_by_sKeyword;
from fPrintLogo import fPrintLogo;
from dxConfig import dxConfig;
from mColors import *;

def fPrintUsageInformation():
  asApplicationKeywords = list(ddxApplicationSettings_by_sKeyword.keys())
  oConsole.fLock();
  try:
    fPrintLogo();
    axBoolean = ["[=", INFO, "true", NORMAL, "|", INFO, "false", NORMAL, "]"];
    oConsole.fOutput(HILITE,"Usage:");
    oConsole.fOutput();
    oConsole.fOutput("  ", INFO, "BugId.py", NORMAL, " [", INFO, "options", NORMAL, "] <", INFO, "target", NORMAL,
                      "> [", INFO, "options", NORMAL, "] [-- ", INFO, "argument ", NORMAL, "[", INFO, "argument ",
                      NORMAL, "[", INFO, "...", NORMAL, "]]]");
    oConsole.fOutput();
    oConsole.fOutput(HILITE, "Targets:");
    oConsole.fOutput("  ", INFO, "\"path\\to\\binary.exe\"");
    oConsole.fOutput("    Start the given binary in the debugger with the given arguments.");
    oConsole.fOutput("  ", INFO, "--pids=pid[,pid[...]]");
    oConsole.fOutput("    Attach debugger to the process(es) provided in the list. The processes ", HILITE, "must");
    oConsole.fOutput("    all have been suspended, as they will be resumed by the debugger.");
    oConsole.fOutput("    Arguments cannot be provided for obvious reasons.");
    oConsole.fOutput("  ", INFO, "--uwp-app=<package name>[!<application id>]");
    oConsole.fOutput("    Start and debug a Universal Windows Platform App identified by the given");
    oConsole.fOutput("    package name and application id. If no application id is provided and the");
    oConsole.fOutput("    package exposes only one if, it will default to that id. Note that only");
    oConsole.fOutput("    a single argument can be passed to a UWP App; additional arguments will be");
    oConsole.fOutput("    silently ignored.");
    oConsole.fOutput("  ", INFO, "<known application keyword>");
    oConsole.fOutput("    BugId has a list of known targets that are identified by a keyword. You can");
    oConsole.fOutput("    use such a keyword to have BugId try to automatically find the binary or");
    oConsole.fOutput("    determine the package name and id for that application, optionally apply");
    oConsole.fOutput("    application specific settings and provide default arguments. This makes it");
    oConsole.fOutput("    easier to run these applications without having to manually provide these.");
    oConsole.fOutput("    You can optioanlly override any default settings by providing them *after*");
    oConsole.fOutput("    the keyword. You can also provide the path to the application binary after");
    oConsole.fOutput("    the keyword to use a different binary than the one BugId automatically");
    oConsole.fOutput("    detects, or if BugId is unable to detect the binary on your system.");
    oConsole.fOutput();
    oConsole.fOutput(HILITE, "Options:");
    oConsole.fOutput("  ", INFO, "-h", NORMAL, ", ", INFO, "--help");
    oConsole.fOutput("    This cruft.");
    oConsole.fOutput("  ", INFO, "--version");
    oConsole.fOutput("    Show version information.");
    oConsole.fOutput("  ", INFO, "--version-check");
    oConsole.fOutput("    Check for updates and show version information.");
    oConsole.fOutput("  ", INFO, "--license");
    oConsole.fOutput("    Show license information.");
    oConsole.fOutput("  ", INFO, "--license-update");
    oConsole.fOutput("    Download license updates and show license information.");
    oConsole.fOutput("  ", INFO, "--arguments", NORMAL, "=<", INFO, "file path", NORMAL, ">");
    oConsole.fOutput("    Load additional arguments from the provided value and insert them in place");
    oConsole.fOutput("    of this argument.");
    
    oConsole.fOutput("  ", INFO, "-q", NORMAL, ", ", INFO, "--quiet", axBoolean);
    oConsole.fOutput("    Output only essential information. (default is \"false\")");
    oConsole.fOutput("  ", INFO, "-v", NORMAL, ", ", INFO, "--verbose", axBoolean);
    oConsole.fOutput("    Output all commands send to cdb.exe and everything it outputs in return.");
    oConsole.fOutput("    Note that -q and -v are not mutually exclusive. (default is \"false\")");
    oConsole.fOutput("  ", INFO, "-p", NORMAL, ", ", INFO, "--pause", axBoolean);
    oConsole.fOutput("    Always wait for the user to press ENTER before terminating at the end.");
    oConsole.fOutput("    (default is \"false\")");
    
    oConsole.fOutput("  ", INFO, "-c", NORMAL, ", ", INFO, "--collateral", NORMAL, "[=", INFO, "number of bugs", NORMAL, "]");
    oConsole.fOutput("    When the specified number of bugs is larger than 1 (default 5), BugId will");
    oConsole.fOutput("    go into \"collateral bug handling\" mode. This means that after certain");
    oConsole.fOutput("    access violation bugs are reported, it will attempt to \"fake\" that the");
    oConsole.fOutput("    instruction that caused the exception succeeded without triggering an");
    oConsole.fOutput("    exception. For read operations, it will set the destination register to a");
    oConsole.fOutput("    tainted value (0x41414141...). For write operations, it will simply step");
    oConsole.fOutput("    over the instruction. It will do this for up to the specified number of");
    oConsole.fOutput("    bugs.");
    oConsole.fOutput("    The upshot of this is that you can get an idea of what would happen if");
    oConsole.fOutput("    you were able to control the bad read/write operation. This can be usedful");
    oConsole.fOutput("    when determining if a particular vulnerability is theoretically exploitable");
    oConsole.fOutput("    or not. E.g. it might show that nothing else happens, that the application");
    oConsole.fOutput("    crashes unavoidably and immediately, both of which indicate that the issue");
    oConsole.fOutput("    is not exploitable. It might also show that reading from or writing to");
    oConsole.fOutput("    otherwise inaccessible parts of memory or controlling execution flow is");
    oConsole.fOutput("    potentially possible, indicating it is exploitable.");
    
    oConsole.fOutput("  ", INFO, "-d", NORMAL, ", ", INFO, "--dump", axBoolean);
    oConsole.fOutput("    Save a mini crash dump when a crash is detected.");
    
    oConsole.fOutput("  ", INFO, "--full-dump", axBoolean);
    oConsole.fOutput("    Save a full crash dump when a crash is detected.");
    
    oConsole.fOutput("  ", INFO, "-f", NORMAL, ", ", INFO, "--fast", axBoolean);
    oConsole.fOutput("    Create no HTML report, do not use symbols. This is an alias for:");
    oConsole.fOutput("        ", INFO, "--bGenerateReportHTML=false");
    oConsole.fOutput("        ", INFO, "--cBugId.asSymbolServerURLs=[]");
    oConsole.fOutput("        ", INFO, "--cBugId.bUse_NT_SYMBOL_PATH=false");
    
    oConsole.fOutput("  ", INFO, "-I", NORMAL, " [", INFO, "arguments", NORMAL, "]");
    oConsole.fOutput("    Install as the default JIT debugger on the system. This allows BugId to");
    oConsole.fOutput("    generate a report whenever an application crashes.");
    oConsole.fOutput("    All arguments after -I will be passed to BugId whenever it is started as");
    oConsole.fOutput("    the JIT debugger. It might be useful to add arguments such as \"--pause\"");
    oConsole.fOutput("    to leave the BugId window open after it generated a report, \"--full-dump\"");
    oConsole.fOutput("    to generate a full memory dump and \"--reports=<path>\" to have the reports");
    oConsole.fOutput("    stored in a specific folder. If you do not provide \"--reports\", it will");
    oConsole.fOutput("    be added automatically to make sure the reports are saved in a folder that");
    oConsole.fOutput("    BugId can write to, and which you can easily find.");
    oConsole.fOutput("  ", INFO, "--jit");
    oConsole.fOutput("    Show details on the currently installed JIT debugger.");
    
    oConsole.fOutput("  ", INFO, "--isa", NORMAL, "=", INFO, "x86", NORMAL, "|", INFO, "x64");
    oConsole.fOutput("    Use the x86 or x64 version of cdb to debug the application. The default is");
    oConsole.fOutput("    to use the ISA* of the OS. Applications build to run on x86 systems can be");
    oConsole.fOutput("    debugged using the x64 version of cdb, and you are strongly encouraged to ");
    oConsole.fOutput("    do so. But you can use the x86 debugger to debug x86 application if you");
    oConsole.fOutput("    want to. (ISA = Instruction Set Architecture)");
    
    oConsole.fOutput("  ", INFO, "-r", NORMAL, ", ", INFO, "--repeat", NORMAL, "[=", INFO, "number of loops", NORMAL, "]");
    oConsole.fOutput("    Restart the application to run another test as soon as the application is");
    oConsole.fOutput("    terminated. Useful when testing the reliability of a repro, detecting the");
    oConsole.fOutput("    various crashes a non-deterministic repro can cause or while making ");
    oConsole.fOutput("    modifications to the repro in order to test how they affect the crash.");
    oConsole.fOutput("    A statistics file is created or updated after each run that contains the");
    oConsole.fOutput("    number of occurances of each Bug Id that was detected. If a number is");
    oConsole.fOutput("    provided, the application will be run that many times. Otherwise the");
    oConsole.fOutput("    application will be run indefinitely.");
    
    oConsole.fOutput("  ", INFO, "--symbols", NORMAL, "=", INFO, "path\\to\\symbols\\folder");
    oConsole.fOutput("    Use the given path as a local symbol folder in addition to the symbol paths");
    oConsole.fOutput("    specified in dxConfig. You can provide this option multiple times to add");
    oConsole.fOutput("    as many additional local symbol paths as needed.");
    
    oConsole.fOutput("  ", INFO, "--reports", NORMAL, "=", INFO, "path\\to\\reports\\folder");
    oConsole.fOutput("    Store reports in the given path. Optional cdb output and crash dumps are");
    oConsole.fOutput("    stored in the same location.");
    
    oConsole.fOutput();
    oConsole.fOutput("  Options also include any of the settings in dxConfig.py; you can specify them");
    oConsole.fOutput("  using ", INFO, "--", NORMAL, "[", INFO, "name", NORMAL, "]=[", INFO, "JSON value", NORMAL, "]. Here are some examples:");
    oConsole.fOutput("  ", INFO, "--bGenerateReportHTML=false");
    oConsole.fOutput("    Do not save a HTML formatted crash report. This should make BugId run");
    oConsole.fOutput("    faster and use less RAM, as it does not need to gather and process the");
    oConsole.fOutput("    information needed for the HTML report.");
    oConsole.fOutput("    If you only need to confirm a crash can be reproduced, you may want to use");
    oConsole.fOutput("    this: it can make the process of analyzing a crash a lot faster. But if");
    oConsole.fOutput("    no local or cached symbols are available, you'll get less information");
    oConsole.fOutput("  ", INFO, "\"--sReportFolderPath=\\\"BugId\\\"\"");
    oConsole.fOutput("    Save report to the specified folder, in this case \"BugId\". The quotes");
    oConsole.fOutput("    mess is needed because of the Windows quirck explained below.");
    oConsole.fOutput("  The remaining dxConfig settings are:");
    for sSettingName in sorted(dxConfig.keys()):
      if sSettingName not in ["bGenerateReportHTML", "sReportFolderPath", "cBugId"]:
        xSettingValue = dxConfig[sSettingName];
        oConsole.fOutput("  ", INFO, "--", sSettingName, NORMAL, " (default value: ", INFO, str(xSettingValue), NORMAL, ")");
    oConsole.fOutput("  See ", INFO, "dxConfig.py", NORMAL, " for details on each setting.");
    oConsole.fOutput();
    oConsole.fOutput("  You can also adjust cBugId specific settings, such as:");
    oConsole.fOutput("  ", INFO, "--cBugId.asSymbolServerURLs=[\"http://msdl.microsoft.com/download/symbols\"]");
    oConsole.fOutput("    Use http://msdl.microsoft.com/download/symbols as a symbol server.");
    oConsole.fOutput("  ", INFO, "--cBugId.asSymbolCachePaths=[\"C:\\Symbols\"]");
    oConsole.fOutput("    Use C:\\Symbols to cache symbol files.");
    oConsole.fOutput("  See ", INFO, "cBugId\\dxConfig.py", NORMAL, " for details on all available settings.");
    oConsole.fOutput("  All values must be valid JSON of the appropriate type. No checks are made to");
    oConsole.fOutput("  ensure this! Providing illegal values may result in exceptions at any time");
    oConsole.fOutput("  during execution. You have been warned!");
    oConsole.fOutput();
    oConsole.fOutput("  Note that you may need to do a bit of \"quote-juggling\" because Windows likes");
    oConsole.fOutput("  to eat quotes for no obvious reason. So, if you want to specify --a=\"b\", you");
    oConsole.fOutput("  will need to use \"--a=\\\"b\\\"\", or BugId will see --a=b and `b` is not valid");
    oConsole.fOutput("  JSON.");
    oConsole.fOutput();
    oConsole.fOutput(HILITE, "Known application keywords:");
    asLine = ["  "];
    uLineLength = 2;
    for sApplicationKeyword in asApplicationKeywords:
      if uLineLength > 2:
        if uLineLength + 2 + len(sApplicationKeyword) + 2 > 80:
          asLine += [NORMAL, ","];
          oConsole.fOutput(*asLine);
          asLine = ["  "];
          uLineLength = 2;
        else:
          asLine += [NORMAL, ", "];
          uLineLength += 2;
      asLine += [INFO, sApplicationKeyword];
      uLineLength += len(sApplicationKeyword);
    asLine += [NORMAL, "."];
    oConsole.fOutput(*asLine);
    oConsole.fOutput();
    oConsole.fOutput("  Run ", INFO, "BugId.py application?", NORMAL, " for an overview of the application specific command");
    oConsole.fOutput("  line arguments and settings.");
    oConsole.fOutput();
    oConsole.fOutput(HILITE, "Exit codes:");
    oConsole.fOutput("  ", INFO, "0", NORMAL," = BugId successfully ran the application ", UNDERLINE, "without detecting a bug", NORMAL, ".");
    oConsole.fOutput("  ", INFO, "1", NORMAL," = BugId successfully ran the application and ", UNDERLINE, "detected a bug", NORMAL, ".");
    oConsole.fOutput("  ", ERROR_INFO, "2", NORMAL, " = BugId was unable to parse the command-line arguments provided.");
    oConsole.fOutput("  ", ERROR_INFO, "3", NORMAL, " = BugId ran into an internal error: please report the details!");
    oConsole.fOutput("  ", ERROR_INFO, "4", NORMAL, " = BugId was unable to start or attach to the application.");
    oConsole.fOutput("  ", ERROR_INFO, "5", NORMAL, " = You do not have a valid license.");
  finally:
    oConsole.fUnlock();