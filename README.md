BugId
=====

Detect, analyze and uniquely identify application bugs.

TL;DR
-----
Do you...
* want to know what kind of bug is causing an application to crash?
* want to know if a bug might be security vulnerability?
* want to find out if two or more crashes are caused by the same bug?
* want a human readable report with an analysis of a bug?

...then BugId may be for you!

Quick setup
-----------
To use BugId, please download and install the following software:
* Latest [Python 2.7.14](https://www.python.org/downloads/release/python-2715/)
* Latest [Debugging Tools for Windows](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/)
* Latest [BugId release](https://github.com/SkyLined/BugId/releases)

If you install Python and Debugging Tools for Windows with their default
settings, BugId should be able to run without adjusting any settings. You can
unzip BugId anywhere you want on your local file system.

Before you start BugId, you should enable *full page heap* in the target application.
This can be done *per binary* by setting certain [Global Flags](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/global-flag-reference). The easiest way to do this is to use the
`pageheap.cmd` script that comes with BugId. For instance, to enable full page heap
for notepad, run the following command:

```
C:\BugId>pageheap notepad.exe ON
```
*(Note that this command must be run from an elevated command-prompt with
administrative access to the machine).*

To make things even easier, `pageheap.cmd` has a list of *known applications*. You
can enable or disable full page heap for any one of them by providing its name, e.g.
`pageheap msie ON` enables full page heap for Microsoft Internet Explorer. Use
`pageheap /?` to get more information about command-line arguments.

At this point, you may want to test if BugId is working correctly. We can do this by
running an application in BugId and crashing it to see if BugId reports the bug
correctly. A good application to use for this test is `rundll32.exe` which is found
on all Windows installations in the `system32` sub-folder of the Windows folder
(`%WinDir%`). It can be used to load any dll found on the local file system and call
an exported function in this dll with a certain call format. There are many dlls in
the `system32` folder that export functions. Most of these exported functions expect
arguments in a completely different format than what rundll32 will provide, causing
the application to crash.

First we must turn on full page heap in rundll32 with the following command:

```
C:\BugId>pageheap rundll32.exe ON
```
Next we will start BugId and tell it to start rundll32 with arguments that instruct it
to load `advapi32.dll` and call `CloseThreadWaitChainSession`. At the time of this
writing that causes a so-called NULL pointer access violation, which BugId should
detect and report.

```
C:\BugId>BugId.cmd %WinDir%\system32\rundll32.exe -- advapi32 CloseThreadWaitChainSession
```
Notice there is a `--` between rundll32.exe and the arguments passed to it.
This is because you may want to provide arguments to both BugId itself and
the application you want to test. These two sets of arguments should be
separated by `--` on the command-line. Everything before `--` is handled by
BugId and everything after is ignored by BugId but passed to the application.

If all is well, the output of BugId will look like this:

```
* Command line: C:\WINDOWS\system32\rundll32.exe advapi32 CloseThreadWaitChainSession
+ Main process 8024/0x1F58 (rundll32.exe): Attached; command line = C:\WINDOWS\system32\rundll32.exe advapi32 CloseThreadWaitChainSession.
,-- A bug was detect in the application ----------------------------------------
| Id @ Location:    AVR@NULL a1f.904 @ rundll32.exe!advapi32.dll!WctRemoveEntry
| Description:      Access violation while reading memory at 0x0 using a NULL pointer.
| Security impact:  Denial of Service
| Version:          rundll32.exe 10.0.16299.15 (x64)
|                   advapi32.DLL 10.0.16299.15 (x64)
| Bug report:       AVR@NULL a1f.904 @ rundll32.exe!advapi32.dll!WctRemoveEntry.html (60703 bytes)
'-------------------------------------------------------------------------------
```

The first line tells you the command-line BugId is going to start. The second
line tells you that this caused a new process to be created with *process id*
8024, running `rundll32.exe` and the command line for this process (which is
of course the same as in the first line). Soon after starting the application,
a bug was detected. BugId generated a unique id (`AVR@NULL a1f.904`) for this
bug and reported its location is in the `WctRemoveEntry` function of the 
`advapi32.dll` dll loaded by `rundll32.exe`. Since NULL pointer crashes are
normally not exploitable other than to crash the application, the bug's
security impact is `Denial of Service`. BugId by default generates a HTML
formatted report for every bug it finds and tells you the location where this
report was stored. As you can see, the file name of the report is based on the
bug id and location.

Every bug id generated by BugId consists of two part separated by a space. The
first part describes the type of bug. In the above example, `AVR@NULL`, this
means *A*ccess *V*iolation *R*eading memory *at* address *NULL*. The second
part describes the location of the bug; it consists of two short hashes
separated by a dot. These hashes are calculated from the top functions on the
stack *that are considered relevant to the bug*. In the example, `a1f.904`
consists of `a1f` (calculated from `advapi32.dll!WctRemoveEntry`) and `904`
(calculated from `advapi32.dll!CloseThreadWaitChainSession`).

If you run that same command again, BugId will report the exact same BugId, as
this should couse the exact same bug in the exact some code.

Congratulations! You are now ready to test your own crashes with BugId, but
you may want to run `BugId.cmd --help` at some point to get information about
the many different command-line options BugId supports.

Notes
-----
BugId has been developed for and tested on a large number of applications
during fuzzing to analyze hundreds of thousands of crashes caused by hundreds
of different bugs. In this role it has proven to be extremely accurate in
analyzing bugs with a very low false positive and negative rate; both are
less than 1%.

Of course not all types of bugs are easy to detect and analyze. Some bugs
cannot currently be detected reliably at the time they happen but cause a
crash much later on in completely unrelated code, leading to a completely
incorrect analysis. In such cases, repeatedly reproducing the same bug will
lead to a number of different bug ids as the application crashes in
different ways at different times. To make sure this is not the case, you
are advised to run your test case in BugId a number of times to see if the
bug id stays the same.

Others bugs cause crashes that look like they are caused by a different
type of bug. This can result in incorrect analysis and bug ids. Most
notably, bugs that are the result of *bad casts* in C/C++ code are
currently impossible to detect and report by BugId. They can result in
various different types of crashes; most commonly access violations when
values stored in properties of an object are incorrectly used as pointers.
If you expect bad casts might be the cause of a crash, you should double
check the analysis done by BugId to make sure it is correct.

BugId is highly dependent on full page heap being used by the application
to be able to detect and analyze a large number of heap related bugs. This
means that it will be much less effective at detecting and analyzing bugs
in application that use their own internal heap manager that does not rely
on the standard Windows heap.

License
-------
<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">
  <img alt="Creative Commons License" style="vertical-align: middle; float: left;" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png"/>
</a>
BugId has a free 30-day trial period for commercial and non-commercial use.
During this trial period this work is licensed under a
[Creative Commons Attribution-NonCommercial 4.0 International License](http://creativecommons.org/licenses/by-nc/4.0/).

After the trial period, paid license must be acquired at
[license.skylined.nl](https://license.skylined.nl) if you want to continue
to use BugId.

Non-Commercial licenses are available for a very small fee; just enough to pay
for my expenses. Commercial licenses for individual security researchers are
available at a huge discount too.

If you have any questions about licensing, or want to discuss a bulk-discount,
please contact [license@skylined.nl](mailto:license@skylined.nl).

BugId has a trial period to allow you to assess its usefulness. If you want to
continue to use BugId after the trial period has ended, I ask that you contribute
a small fee to pay for my work on BugId and handling of the license request. If
you are using BugId commercially, I ask that you pay a regular license fee to
share some of the profit you are making off of your use of BugId.
