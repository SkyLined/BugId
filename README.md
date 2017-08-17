BugId
=====

Python module to detect, analyze and id application bugs

<a href="https://www.codewake.com/p/bugid">
  <img style="vertical-align: middle; float: left;" src="https://www.codewake.com/badges/codewake2.svg"/>
</a>
*This project is under very active development and I appreciate any feedback
you can give me; if you are having any problems running it, or have any
questions, please do let me know (e.g. by opening a bug). I will try to help
you and get the issue resolved as soon as possible.*

TL;DR
-----
Do you...
* want to automatically debug an application to detect bugs that cause crashes and excessive CPU usage?
* want to be able to detect duplicates among your bugs?
* want bugs automatically analyzed to see if they might be security vulnerabilities?
* want a nice HTML report of the bugs you found?
* want a full debugger dump when a bug is triggered for manual analyses?
* have no problem integrating a tool written in Python into your framework?

...then BugId may be for you!

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
allow "bucketizing" crashes to skip known bugs and focus on bugs that have not
been found before.

A human-readable report containing information collected about the bug is 
available in HTML format, for use when manually analyzing bugs. The code
attempts to determine the security risk of the bug it detected, so even novice
users may be able to determine whether or not a particular bug is likely to be
a security vulnerability. You can download a number of example reports [here]
(https://github.com/SkyLined/cBugId/tree/master/Tests/Reports).

You can tell BugId to save a debugger dump file when it detects a crash, for
later off-line analysis by a developer.

BugId can be used as a command-line utility through BugId.py and integrated into
your own Python project using cBugId.py.

The bug id format
-----------------
The bug id follows the format `BugType xxx.xxx`, where:
* `BugType` is a keyword that identifies the type of bug that was detected.
  A list of keywords and their meaning is provided below.
* `xxx.xxx` is a stack hash. It consists of a (customizable) number of hashes,
  and each has consists of a (customizable) number of hexadecimal digits. The
  first hash is for the top-most *relevant* function on the call stack, the
  second hash is for the next *relevant* function on the call stack, etc.
  The number of hashes can be set using the `uStackHashFramesCount` setting in
  `dxConfig.py` and the number of digits can be set using
  `uMaxStackFrameHashChars`. The default settings are 2 and 3 respectively,
  meaning the stack hash represents the function in which the bug is considered
  to be located and its caller. However, for recursive function calls involving
  multiple functions, it can hard to determine in which function the call loop
  started. In such cases, one function is deterministically picked from the
  list and treated as the first. If there are less functions involved in the
  loop than `uStackHashFramesCount`, the number of hashes will be less. If there
  are more, the number of hashes will be limited to `uStackHashFramesCount`,
  with the last hash containing a hash of all the remaining functions.

BugId attempts to generate a bug id for each bug in such a way that it is
unique to the bug, and not to the crash. In other words: if you crash an
application twice using the same bug, you should get the same bug id, but if
you crash an application twice using two different bugs, you should get two
different bug ids.

`BugType` can have many values, including:
* `AV?:{memory/address type}{+/-offset}` - An access violation was detected
  while attempting to read (`AVR`), write (`AVW`) or execute (`AVE`) the
  specified type of memory or address, `{address/memory type}` types include:
  * `NULL` - a NULL pointer was used to address the memory,
  * `Assertion` - this address is used to indicate an assertion has failed.
  * `PoisonUninitialized` - the pointer used was read from uninitialized memory.
  * `PoisonFree` - the pointer used was read from freed memory.
  * `PoisonOOB` - the pointer used was read from memory that is out-of-bounds.
  * `Invalid` - the memory at this address is not accessible from user-land.
  * `Unallocated` - no memory is allocated at the address,
  * `Reserved` - memory has been reserved but not committed at this address,
  * `Arbitrary` - memory is allocated at this address, but not accessible,
  * `CFG` - Control Flow Guard (CFG) attempted to check an invalid function
    pointer.
  
  An optional offset is added if the access violation happened near the exact
  address, e.g. AVR:NULL+8 is an attempt to write at offset 8 from a NULL
  pointer (i.e. at address 8).
  
* `AV?[size]{+/-/@offset}` - Similar to above, but the access violation
  happened at the given offset before, in or after an allocated heap block of
  given size, e.g. AVW[4]-1 is 1 byte before, AVW[4]@1 is at offset one inside,
  and AVW[4]+1 is one byte beyond a 4 byte memory block.

* `UAF?` - (Use-After-Free) An access violation was detected while attempting
  to access freed memory. Unfortunately, no information about the size of the
  freed memory block and the offset at which it was accessed can be provided.

* `OOB?[size]{+/-offset}` - (Out-Of-Bounds) The application has written or
  attempted to access a heap block of the given size at the given offset
  before or after the heap block.
  
* `OOBW[Stack] - (Out-Of-Bounds) The application has written outside of the
  stack memory it is allowed to modify, overwriting a stack cookie. The change
  in the stack cookie caused the application to detected and report this issue.
  
  Both the sizes and the offsets used in the above BugIds can be made
  *architecture independent* by setting the `dxBugIdConfig` setting
  `uArchitectureIndependentBugIdBits` to the smallest number of bits for the
  desired architectures (e.g. 32 when testing a 32-bit and 64-bit architecture).
  This causes these values to be presented modulo that number of bits, which
  should make the bug id the same for both architectures. For instance, if a
  32-bit application allocates 0x10 bytes and a 64-bit application 0x20 bytes
  for the same structure (e.g. an array of 4 pointers), an attempt to write to
  the *sixth* entry in this array would lead to BugId `OOBW[0x10]+4` and
  `OOBW[0x20]+8` respectively. With `uArchitectureIndependentBugIdBits` set to
  32 however, both would lead to `OOBW[4*N]`, as 0x4, 0x8, 0x10 and 0x20 are
  all divisible by 4. An attempt to read the *second WORD* after the *fifth*
  pointer (`OOBW[0x10]+6`; 4+2 and `OOBW[0x20]+0xA`; 8+2) would result in
  `OOBW[4*N]+2` for both.

* `Assert` - An assertion has failed.
* `Breakpoint` - A debugger breakpoint was triggered.
* `C++` - An unhandeled C++ exception 
* `CorruptList` - Safe unlinking detect a corrupted LIST_ENTRY
* `CPUUsage` - Excessive CPU usage was detected.
* `FloatDivideByZero` and `IntegerDivideByZero` - A division by zero occured.
* `HeapCorrupt` - Application verifier has detected heap corruption.
* `IllegalInstruction` - An illegal instruction was executed.
* `InvalidHandle` - An operation was performed on an invalid handle.
* `LegacyGS`, `StackCookie` - /GS detected that a stack cookie was modified.
* `RecursiveCall` - A recursive function call loop has used too much stack memory.
* `RefCount` - A reference counter was incremented beyond its maximum value.
* `StackExhaustion` - A function has attempted to allocate too much stack memory.
* `OOM` - Out Of Memory: the application attempted to allocate too much memory.
* `PureCall` - A pure virtual function was called.
* `VTGuard` - VTGuard detected that a virtual function table cookie was modified.
These are the values you are likely to see. For a full list, please refer to the
source code. Every bug report includes a description of the bug, which explains
the type of issue in more detail.

The bug location
----------------
The bug location follows the format `Binary.exe![Module.dll!]FunctionName`,
where:
* `Binary.exe` is the process' main binary
* `Module.dll` is the module that contains the function in which the bug is
  considered to be located, if it was not found in the process' main binary.
* `FunctionName` is the name of the function in which the bug is considered to
  be located.

Note that the first *relevant* function (in which the bug is considered to be
located) may not be the same as the top function on the stack (the one in which
the detected exception occurred). For instance, if a function `A` calls
`KERNELBASE.dll!RaiseException` to raise an exception,
`KERNELBASE.dll!RaiseException` is not considered relevant to the bug. In this
case `A` is considered to be the first *relevant* function, and thus the
location for the bug. For some OOM bugs, a large number of function calls from
the top of the stack may be considered irrelevant because they are part of the
memory allocation code, page heap or OOM handling and not specific to that bug.

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

    BugId.py [options] "path\to\binary.exe" [arguments]

Start the binary in the debugger with the provided arguments.

    BugId.py [options] @application [additional arguments]

(Where `application` is a known application keyword, see below for details)
Start the application identified by the keyword in the debugger using the
application's default binary path and arguments followed by the default
additional arguments or the additional arguments provided and apply application
specific BugId settings.

    BugId.py [options] @application="path\to\binary.exe" [arguments]

Start the application identified by the keyword in the debugger using the
provided binary and arguments (instead of the default binary path and
arguments) followed by the default additional arguments or the additional
arguments provided and apply application specific settings. This allows you to
run a known application with custom binary path and arguments, but default
application specific BugId settings.

    BugId.py [options] [@application] --pids=[process id, process id, ...]

Attach debugger to the process(es) provided in the list. The processes *must
all have been suspended*, as they will be resumed by the debugger. If you
specify the option application keyword, the default application specific
BugId settings will be applied.

### Known application keywords
A few application are known to BugId and can be run without having to specify
their full command-line and/or with application specific settings by using one
of these application specific keywords:
  @aoo-writer: Apache OpenOffice Writer
  @firefox: Mozilla Firefox
  @foxit: Foxit Software Reader
  @chrome: Google Chrome 
  @msie: Microsoft Internet Explorer (32-/64-bit depending on OS)
  @msie86: Microsoft Internet Explorer, 32-bit application
  @msie64: Microsoft Internet Explorer, 64-bit application
  @nightly: Mozilla Firefox Nightly builds

You can find out what these build-in application specific settings are by asking
BugId using the following command line:

    BugId.py @application?

### Options
The file `dxBugIdConfig.py` contains a number of configuration options that
allow you to easily change certain behavior of BugId. You can modify this file
to change the default settings for these options, or you can specify these
options on the command line. Each option takes this form:

    --[option name]=[JSON option value]

Any option specified in `dxConfig.py` can be used as the `option name`; see the
file for a complete list of options. The following options are probably
the most interesting ones:

    --bGenerateReportHTML=true

Tell BugId to save a HTML formatted report for the crash it detects.

    --bSaveDump=true
    --bOverwriteDump=true

Tell BugId to save a dump file, and to overwrite any existing dump file. The
file name of the dump file is based on the crash id.

    --nApplicationMaxRunTime=[number of seconds]

Tell BugId to terminate if the application has been running for this many
seconds without crashing. For instance, if you want to give an application 3
seconds to load and process a test case, use "--nApplicationMaxRunTime=3": if
the application has not crashed after running 3 seconds, it will be terminated
and no bug is reported.

You can also modify the configuration options for `cBugId` itself, as specified
in the `dxBugIdConfig.py` file for that project. These settings can also be
used as the `option name` if they are prefixed with `cBugId.`; see that file
for a complete list of options. For instance:

    --cBugId.sCdbBinaryPath_x86="path\to\cdb.exe"

Tell BugId to use a cdb.exe binary from a specific location.


cBugId.py
---------
You can integrate BugId with your own python project by putting it in a
sub-folder (e.g. "BugId") of your project and importing the `cBugId` class:

    from BugId import cBugId;
    
    oBugId = cBugId(...);
    
    oBugId.fWait();
    if oBugId.oBugReport:
      print "Error: %s" % oBugReport.sId;

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
      fApplicationRunningCallback is called when the application starts and
      after exception analysis is finished for continuable exceptions that are
      not considered a bug. In the later case, fExceptionDetectedCallback is
      called when the application is paused to do the analysis. It indicates
      the application has started or been resumed. If you want to add some
      timeout to your testing, the timeout should probably start/resume when
      this callback gets called.
    fExceptionDetectedCallback()
      fExceptionDetectedCallback is called when an exception that requires some
      analysis is detected in the application. If you added some timeout to
      your testing, you may want to pause it when this callback is called and
      resume it when fApplicationRunningCallback is called after the analysis
      is finished.
    fApplicationExitCallback(),
      Called when (any of) the application's "main" process(es) terminates.
      When you start an application using BugId, the "main" process is the
      first process created. When you are attaching to processes, these are the
      "main" processes. Note that this callback is not called when any other
      process (spawned by these "main" processes, or one of their children) is
      terminated. If you want to detect application termination, you may want
      to use this callback to do so. For instance, some of Microsoft Edge's
      processes have a tendency to terminate for no apparent reason, breaking
      whatever you were doing.
    fFinishedCallback(oErrorReport)
      fFinishedCallback gets called when all processes for the application have
      terminated cleanly (in which case oErrorReport is None) or when a bug is
      detected (in which case oErrorReport contains information about the bug).
    fInternalExceptionCallback(oException)
      fInternalExceptionCallback is called when there is a bug in BugId itself.
      If you want to make sure BugId is working as expected, you may want to
      use this callback. If it gets called, you can file a bug at
      (here)[https://github.com/SkyLined/BugId/issues]. Please add as many
      details from the exception object passed in the argument as you can.

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
      for different architectures (eg. x86 v.s. x64).
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
      concatenating parts of hashes of the return addresses for some of the
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
as thread safety issues may result in different crashes too, based on
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
    
    Id:               336C AVR:NULL+4*N iexplore.exe!MSHTML.dll!CTreeNode::GetFancyFormat
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

License
-------
<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">
  <img alt="Creative Commons License" style="vertical-align: middle; float: left;" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png"/>
</a>
This work is licensed under a [Creative Commons Attribution-NonCommercial 4.0
International License](http://creativecommons.org/licenses/by-nc/4.0/). It is
provided free of charge for non-commercial use only. If you would like to use
it commercially, please contact the author at [bugid@skylined.nl][] to
discuss licensing options. If you find it useful and would like to make a
donation, you can send bitcoin to [183yyxa9s1s1f7JBpPHPmzQ346y91Rx5DX]. 

[183yyxa9s1s1f7JBpPHPmzQ346y91Rx5DX]:bitcoin:183yyxa9s1s1f7JBpPHPmzQ346y91Rx5DX
[bugid@skylined.nl]:mailto:bugid@skylined.nl
