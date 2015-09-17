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

The information collected can be stored in HTML format, and can be useful when
manually analyzing bugs. The code attempts to determine the security risk of
the bug it detected, so even novice users may be able to determine whether or
not a particular bug is likely to be a security issue.

Usage
-----
There are multiple ways to use the code. First, you can simply start BugId from
the command line in the following ways:

    BugId.py [options] path\to\binary.exe [arguments]

Runs the binary in the debugger with the provided arguments.

    BugId.py [options] --pids=[comma separated list of process ids]

Attach debugger to the process(es) provided in the list. Not that the processes
*must* all have been suspended, as they will be resumed by the debugger.

    BugId.py [options] [known application] [additional arguments]

A number of "known" applications have been defined, which includes the path to
the binary to be executed and any default arguments to be provided to the
application. This makes it possible to execute these applications with those
argument in BugId by using a single keyword. Currently the know applications
are:
* firefox: Mozilla Firefox
* chrome: Google Chrome 
* msie: Microsoft Internet Explorer
* msie86: Microsoft Internet Explorer, 32-bit application
* msie64: Microsoft Internet Explorer, 64-bit application

Second, you can use BugId directly in your own python script by putting it in a
sub-folder (ee.g. "BugId") of your project and importing the cBugId class:

    from BugId import cBugId;
    
    oBugId = cBugId(...);
    
    oBugId.fWait();
    if oBugId.oErrorReport:
      print "Error: %s" % oErrorReport.sId;

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
must be provided and that they are mutually exclusive. 

EdgeDbg
-------
To facilitate usage of BugId with Microsoft Edge, the [EdgeDbg]
(https://github.com/SkyLined/EdgeDbg) project includes the `EdgeBugId.cmd`
script, which can be used to run Edge in BugId. More information is available
in the [README](https://github.com/SkyLined/EdgeDbg/blob/master/README.md) file
for that project.

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

Unit tests
----------
This project comes with executables that can be used trigger a range of bugs,
which makes it possible to test if BugId is functioning correctly. If you are
making modification to the source, you are strongly advised to run these tests
to make sure these changes did not break BugId in some way. The executables
and their source are found in the `Tests\` folder. The python script `Tests.py`
runs a large number of tests and returns an error code of zero if all succeeded
and a non-zero error code if any failed.
