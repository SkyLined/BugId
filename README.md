BugId
=====

Python module to detect, analyze and id application bugs

Description
-----------
BugId is a python script that runs an application in cdb.exe, a command-line
debugger that is part of Microsoft's Debugging Tools for Windows. It interacts
with cdb.exe to detect any potential bugs in the application, and analyzes them.
When a bug is detected, detailed information is collected and an id is generated
that should be unique and consistent for that particular bug. In other words,
if you run the same application twice and trigger the same bug, the bug id
should be the same.

The bug id can be useful when trying to determine whether two crashes have the
same bug as their root cause. It is used in automated fuzzing frameworks to
allow "bucketizing" crashes to skip known issues and focus on bugs that have
not been found before.

The information collected about the bug is stored in HTML format, and can be
useful when manually analyzing bugs. The code attempts to determine the security
risk of the bug it detected, so even novice users may be able to determine
whether or not a particular bug is likely to be a security issue.

BugId can be used as a command-line utility through BugId.py and integrated into
your own Python project using cBugId.py.

PageHeap.cmd
------------
Page heap should be enabled for the target application to make detection and
analysis of bugs more reliable and detailed. This can be done using the
gflags.exe application that is distributed with Microsoft's Debugging Tools for
Windows. The preferred flags to use are +02109870, see the page heap
documentation for an explanation of the switches in use. The command-line
utility PageHeap.cmd is provided to facilitate enabling/disabling page heap
for an application, it can be used in the following way:

    PageHeap.cmd binary.exe [ON|OFF]

This will enable (ON, default) or disable (OFF) page heap for the provided
binary. Note that some applications, especially those that run parts of
their code in a sandbox, may execute multiple binaries. Page heap should be
enabled for all these binaries.

BugId.py
--------
`BugId.py` is a command-line utility to start an application in BugId. It can be
used in the following ways:

    BugId.py [options] path\to\application.exe [arguments]

Runs the application in the debugger with the provided arguments.

    BugId.py [options] --pids=[comma separated list of process ids]

Attach debugger to the process(es) provided in the list. Not that the processes
*must* all have been suspended, as they will be resumed by the debugger.

    BugId.py [options] [known application] [additional arguments]

Start the given "known" application in the debugger with default argument and
optional additional arguments. A number of "known" applications have been
pre-defined for which BugId.py knows the path to the binary to be executed and
and optionally a number of default arguments to be passed to the application. 
Currently the know applications are:
* firefox: Mozilla Firefox
* chrome: Google Chrome 
* msie: Microsoft Internet Explorer
* msie86: Microsoft Internet Explorer, 32-bit application
* msie64: Microsoft Internet Explorer, 64-bit application

You can add your own applications if you don't want to type the entire binary
path every time you use BugId, or if you want to run it with certain arguments
by default. 

cBugId.py
---------
You can integrate BugId with your own python project by putting it in a
sub-folder (e.g. "BugId") of your project and importing the `cBugId` class:

    from BugId import cBugId;
    
    oBugId = cBugId(...);
    
    oBugId.fWait();
    if oBugId.oErrorReport:
      print "Error: %s" % oErrorReport.sId;

(You can either wait for BugId to finish by calling `fWait`, or perform other
functions until the `fFinishedCallback` is called. See below for more details
on that callback).

An example of a python file that uses the `cBugId` class can be found in
`BugId.py`: the later is a wrapper for the former that makes it into a
command-line utility.

cBugId takes the following optional named arguments:
    asApplicationCommandLine
      list of strings that represent the application command-line to execute.
    auApplicationProcessIds
      list of integers that represent the process ids to attach to.
    asSymbolServerURLs
      list of symbol server urls.
    fApplicationRunningCallback()
      function that gets called when the application is started or resumed
      by the debugger. 
    fExceptionDetectedCallback()
      function that gets called when an exception was detected in the
      application and is being analyzed to determine if it is a bug or not.
    fFinishedCallback(oErrorReport)
      function that gets called when the application terminated cleanly (in
      which case oErrorReport is None) or when it has been terminated after a
      bug was detected (in which case oErrorReport contains information about
      the bug).
    fInternalExceptionCallback(oException)
      function that gets called when an internal error happens in BugId code.
      This can be used to save an error report in case BugId is running
      unattended.

Please note that either `asApplicationCommandLine` or `auApplicationProcessIds`
must be provided and that they are mutually exclusive. Also note that the
callbacks are called from separate threads, so your code needs to be
thread-safe in order to function properly when using these callbacks.

oErrorReport
------------
When BugId detects a bug in the application, it is analyzed and an error report
is created that contains useful information about the bug. This information is
stored in an `cErrorReport` object, specifically in the following properties:

    sId (string)
      Contains a string that is unique to this bug in this application. If
      symbols are available, and compile-time optimizations do not make radical
      changes to the binary, the id should be consistently the same for the
      same bug triggered in different versions of the application and builds
      for different architectures (eg. x86 v.s. AMD64).
    sErrorTypeId (string)
      Contains a string that is unique to this type of bug, e.g. "OOM" for an
      crash triggered by the process running out-of-memory, or "AVR:NULL" for
      a NULL pointer access violation. This is used as part of sId.
    sErrorDescription (string)
      Contains a human readable description of the error caused by the bug.
    sSecurityImpact (string/None)
      Contains a human readable description of the possible security impact of
      this bug, or None if the bug is not a security issue. *Please note* that
      this is a best-guess and not a guarantee!
    sStackId (string)
      Contains a unique id for the stack for the bug. This is created by
      concatinating parts of hashes of the return addresses for some of the
      top stack frames. If that sounds complex, you should see the source for
      the exact details. The HTML details may also make this more clear, see
      below for details on those. This is used as part of sId.
    sCodeId (string)
      Contains a unique id for the code that is considered the cause of the bug.
      This is based on the function name as extracted from the symbol file
      (.pdb) if available, or the name of the module in which the code resides
      if not. This is used as part of sId.
    sCodeDescription (string)
      Contains a human readable string that describes where in the code the bug
      was found.
    sProcessBinaryName (string)
      The name of the binary for the process in which the bug was detected.
      This is used as part of sId.
    sHTMLDetails (string)
      Contains detailed information, including all the information in the
      properties mention above as well as version information for the
      binaries involved and a complete log of the debugging session. This
      is stored in HTML format and can be saved to file for use during
      manual analysis.

Notes
-----
Certain bugs that do not result in an exception immediately, but may
result in various exceptions later on during execution may result in
different bug ids. For instance, a bug that slowly consumes all available
memory can trigger an out-of-memory crash in many different functions, in
many different threads in the application. Also, timing based issues, so
as thread safty issues may result in different crashes too, based on
timing. In these cases, there may be a number of bug ids that are
associated with a particular bug, and two distinct bugs may result in the
same bug id. However, more often than not, such a bug will result in a
limited number of bug ids that are still unique to that bug, so using

Example
-------
Start Microsoft Internet Explorer in BugId and open a page from a web-server
running on the same machine at port 28876:

    H:\dev\py\BugId>BugId.py "C:\Program Files\Internet Explorer\iexplore.exe" http://%COMPUTERNAME%:28876/
    * The debugger is starting the application...
      Command line: C:\Program Files\Internet Explorer\iexplore.exe http://W10-IE11:28876
    * New process 4108.
    * The application was started successfully and is running...
    * New process 5880.
    * Exception code 0x80000003 (Break instruction exception) was detected and is being analyzed...
    * The application was resumed successfully and is running...
    * Exception code 0xC0000005 (Access violation) was detected and is being analyzed...
    * A bug was detected in the application.
    
    Id:               336C AVR:NULL+X iexplore.exe!MSHTML.dll!CTreeNode::GetFancyFormat
    Description:      Access violation while reading memory at 0x8 using a NULL ptr
    Process binary:   iexplore.exe
    Location:         MSHTML.dll!CTreeNode::GetFancyFormat + 0x8
    Security impact:  None
    Error report:     336C AVR.NULL+X iexplore.exe!MSHTML.dll!CTreeNode..GetFancyFormat.html (37675 bytes)
    
    H:\dev\C\EdgeDbg>

The exact same thing, done using the "msie" known application keyword:

    H:\dev\py\BugId>BugId.py msie
    <<<snip>>>

EdgeDbg
-------
To facilitate usage of BugId with Microsoft Edge, the [EdgeDbg]
(https://github.com/SkyLined/EdgeDbg) project includes the `EdgeBugId.cmd`
script, which can be used to run Edge in BugId. More information is available
in the [README](https://github.com/SkyLined/EdgeDbg/blob/master/README.md) file
for that project.

Unit tests
----------
This project comes with executables that can be used trigger a range of bugs,
which makes it possible to test if BugId is functioning correctly. If you are
making modification to the source, you are strongly advised to run these tests
to make sure these changes did not break BugId in some way. The executables
and their source are found in the `Tests\` folder. The python script `Tests.py`
runs a large number of tests and returns an error code of zero if all succeeded
and a non-zero error code if any failed.
