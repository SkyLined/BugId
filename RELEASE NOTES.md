2018-11-21
==========
Externally noticeable changes
-----------------------------
+ Bug ids for Access Violation exceptions have been standardized to the
  following format: `<bug type id>:<memory details>[<size>][<offset>]`. This
  includes bug ids for guard page access exceptions, as
  `STATUS_GUARD_PAGE_VIOLATION` exceptions are just a sub-type of
  `STATUS_ACCESS_VIOLATION`. bug type ids `W2RO` and `DEP` have been changed
  back to `AVW` and `AVE` to simplify things.
+ Text descriptions for Access Violation exceptions should now all follow the
  same format.
+ Determining if an Access Violations happened near the stack is now more
  precise.
+ The integrity level of a process is no longer shown in the report.
+ dxConfig names to represent time have always been in seconds. The names of
  such settings have been updated to reflect this. This was previously done
  for `cBugId` already but `BugId` itself was not updated to use the new names.
  This cause a bug when running `msie`. Also, `BugId` itself has such setings.
  These have now also been renamed.
  `nExcessiveCPUUsageCheckInitialTimeout` -> `nExcessiveCPUUsageCheckInitialTimeoutInSeconds`
  `nApplicationMaxRunTime` -> `nApplicationMaxRunTimeInSeconds`
  `cBugId.nExcessiveCPUUsageCheckInterval` -> `cBugId.nExcessiveCPUUsageCheckIntervalInSeconds`
  `cBugId.nExcessiveCPUUsageWormRunTime` -> `cBugId.nExcessiveCPUUsageWormRunTimeInSeconds`
  `cBugId.nTimeoutGranularity` -> `cBugId.nTimeoutGranularityInSeconds`
  `cBugId.nUWPApplicationAttachTimeout` -> `cBugId.nUWPApplicationAttachTimeoutInSeconds`

2018-11-07
==========
I have forgotten to update this file through a number of releases. Change
logs on GitHub will have to suffice as I unfortunately do not have the time
to retroactively describe all changes here.

Externally noticeable changes
-----------------------------
+ `mMultiThreading` and `mDebugOutput` modules have been added to dependencies
  as they are now used by the `cBugId` module. This required a chance to the
  license for BugId to cover these modules too. **You will need to download a
  new copy of your license file to make sure BugId is using the updated
  license.**
+ All timeouts are now named `TimeoutInSeconds` to clarify the unit used. This
  includes those in `dxConfig.py`.

Internal changes since last release:
------------------------------------
+ `BugId` itself and the modules `mWindowsAPI` and `cBugId` have received quite
  a few changes to improve function and variable naming standardization.
+ Timeout and application interruption implementation has been improved to make
  them more reliable and the simplify the code.

2018-06-06
==========
+ Error messages have been clarified.
+ Python 2.7.15 is now supported, warn when using supported but outdated Python.
+ Warning when using the wrong cdb.exe ISA.
+ BugId will no longer run in Windows older than Windows 10. An error message
  will be shown instead. This is due to a bug in cdb.exe that prevents cBugId
  from functioning properly. There is no work-around, so I will have to stop
  using cdb.exe as the debugging engine to fix this. That is my plan, but it
  will require a lot of work, so it may take quite some time to get there.

2018-06-01
==========
+ Bug fixes and updated README.md.

2018-05-30
==========
+ The `--repeat` argument now takes a number that allows you to specify how
  many times you want BugId to run the application.
+ The cBugId engine has had various improvements; most importantly bug fixes
  and changes to the way register values and disassembly are gathered and
  stored in the report.
+ BugId now checks to make sure you are running the latest version of Python
  as some older versions do not implement certain features required for BugId
  to function.

2018-02-23
==========
BugId and all its modules require a license to use. There is a 30 day trial
period during which you can test BugId without a license. After the trial
period you will need to get a license to continue to use it.

Licenses for non-commercial use are available for free, while licenses for
commercial use can be purchased from the author. For more details, and to
acquire a license, please visit https://bugid.skylined.nl.

+ New cBugId version changes many bug ids and has many improvements. See
  separate `RELEASE NOTES.md` in that project for full details.
+ I have added the "--symbols=path/to/symbols" option, which will use the
  provided local symbol path in additional to whatever you have defined in
  dxConfig.

2018-01-30
==========
Externally noticeable changes
-----------------------------
+ New cBugId version changes many bug ids and has many improvements. See
  separate `RELEASE NOTES.md` in that project for full details.
+ Google Chrome ASan builds should now be supported again. The old code no
  longer worked with recent builds and had been disabled for a while. The new
  code improves on the old code in various ways, even if ASan has removed some
  useful info from its output.
+ Mozilla Firefox's new sandbox is disabled when using the `firefox` keyword,
  as the application would not function correctly otherwise (similar to Google
  Chrome).
+ The maximum amount of memory an application is allowed to allocate is no
  longer limited by default.
+ Relative application binary paths are now made absolute using the current
  working directory as the base.

Internal changes
----------------
+ Module importing has been improved to prevent leaking internal modules to the
  global namespace.
+ The way `dxConfig` settings from `cBugId` are imported has been improved.
+ `fSetup` and `fCleanup` replace `fCheckApplication` and
  `fCleanup` for keyword application.
+ Google Chrome logging is done through stdout instead of stderr.
+ More Google Chrome executables have been allowed to run without page heap.
+ Google Chrome environment variable needed to enable page heap is now set
  when using the `chrome` keyword in case the user forgets to do so.
+ All first-chance access violations are now ignored in Java, not just NULL
  pointers. This is done to prevent having to special case NULL pointers and
  reuse the same code that Google Chrome ASan builds need (which cause various
  access violations, apparently also by design).
+ When checking for updates, failures to connect are now handled correctly.

2017-12-21
==========
+ `cBugId.bIgnoreFirstChanceNULLPointerAccessViolations` in `dxConfig.py`
  allows you to ignore all first-chance NULL pointer access violations.
  This is useful when you are debugging an application that triggers NULL
  pointers on purpose, but handles them correctly. For instance, Java does this
  and without this setting, you will get a report for the same NULL pointer
  every time. Now you can run Java in BugId successfully with
  `--cBugId.bIgnoreFirstChanceNULLPointerAccessViolations=true`.
+ The application keyword `java` has been added for Oracle Java. I've only
  tested this with version 9.0.1. If you have other versions, please let me
  know their installation path and whether you can run them successfully in
  BugId, so I can support them.
+ PageHeap.cmd now has another known application called "java" which can be
  used to enable/disable page heap for Oracle Java.
+ All application keyword settings have been cleaned up and moved to the
  `ddxApplicationSettings_by_sKeyword` folder.
+ The application keyword for Apache Open Office has been removed as I was not
  using it.


2017-12-18
==========
+ `-c` and `--collateral[=int]` can now be used to turn on "collateral" bug
  handling. In this case certain access violation bugs are reported, but rather
  than terminating the application, cBugId will attempt to "fake" that the
  instruction that caused this exception succeeded (providing a tainted value
  0x41414141... as the read result if applicable). This allows you to see what
  would happen if you were able to control this bad read/write operation. Any
  subsequent access violations are treated similarly, up until the maximum
  number of collateral bugs requested. This maximum number of bugs defaults to
  5, but can be overwritten through a value provided for the `--collateral`
  argument.
  Collateral bug handling may be useful when trying to determine if a
  particular vulnerability is theoretically exploitable or not: you can use it
  get an idea of the effect that control over the data would provide. It might
  show that nothing else happens, that the application crashes unavoidably and
  immediately, both of which indicate that the issue is not exploitable. It
  might also show that control over arbitrary parts of memory or the
  instruction pointer is potentially possible, indicating it is exploitable.
+ `--bCleanup` should now work correctly.
+ Application specific settings (i.e. application identified with a "keyword")
  have been moved into `ddxApplicationSettings_by_sKeyword` in a separate
  folder to clean up the code.
+ Updated modules required code changes.
+ Output has been standardized and improved.
+ Line wrapping of code was improved.
+ Internal exception stack numbering was reversed and output improved. A
  version check is now run and results output as well.
+ Added more tests.

2017-11-24
==========
+ Update version of cBugId should resolve all open issues, provide more
  stability, add new features and generally make it more awesome.
+ Cleaned up output

2017-11-21
==========
+ Added `uProcessMaxMemoryUse` and `uTotalMaxMemoryUse` settings in
  `dxConfig.py` that allow you to limit the amount of memory a single process
  or all process in the application combined can allocate.
+ Some output will no longer be shown unless you specify the `-v` command-
  line switch. This switch still also enables cdb output. This should make the
  normal output of BugId cleaner.
+ Changed some output formatting.
+ Fix a bug where application keyword binary paths had spaces insert between
  each character when a `keyword?` argument is provided.
+ Added Windows ISA and Python version and ISA to version information.
+ `PageHeap.cmd` will now say "ON" or "OFF" when querying the state of page
  heap for a specific binary, assuming the default flags are set. If non-
  default flags are set, the flags value is shown.

2017-10-25
==========
+ Process binary name is now lower-cased again. It was accidentally changed to
  use whatever casing the file-system used recently. This made it harder to
  match the the bug location id to previous location ids without having to
  do a case-insensitive match. You can now do a case-sensitive match again.
+ boolean arguments must have no value (defaults to true) or either of "true"
  or "false". Other values are no longer accepted.
+ Other arguments that require a value must now have one; they will no longer
  default to "true" if no value is provided.
+ exception and version information now show the version info on all relevant
  modules (a few new ones were added, but the code was not updated to include
  them in this output before).

2017-10-23
==========
+ `MemGC.cmd ?` can now be used to query MemGC state. Administrator privileges
  are no longer needed to query or set MemGC status.
+ `PageHeap.cmd` accesses the Registry directly to get or set page heap flags.
  This means the user no longer needs to have `pageheap.exe` installed in a
  predictable location for it to work. `PageHeap.cmd [binary|application] ?`
  can now be used to determine if page heap is enabled or not; it provides
  simpler output (enabled or disabled) when possible. You can still run
  `PageHeap.cmd [binary|application]` to show the exact flags that are enabled.
  Administrator privileges are no longer needed to query page heap status.
+ `MemGC.cmd` and `PageHeap.cmd` use the full path to `reg.exe` and `find.exe`
  in the Windows System32 folder. They should now function in all environments,
  including ones where the `PATH` environment variable causes either the `reg`
  and/or `find` command to execute another binary (e.g. PowerShell).
+ Fix mFileSystem module (it was static and is now linked to latest).
+ Delayed path creation for Firefox profile: the profile folder will now be
  created right before Firefox is started through the `firefox` keyword and
  only then. This is required to be able to generate an 8.3 path to the folder,
  which is passed to Firefox in the command-line arguments.
+ Added `pingsender.exe` to the list of page-heap enabled executable for
  Firefox.
+ The Windows version and build number are now read from the Registry and shown
  when an internal exception happens and when the `--version` command-line
  argument is used.
+ BugId will no longer attempt to debug Edge on Windows versions before build
  number 15063. This will not work, so an error message is shown instead and
  the user is told to use EdgeDbg in this case.
+ Added unit-tests.
+ New oConsole module has a bug fix that allows `BugId.py --version` to have
  its output redirected (this woule previously cause an exception).

2017-10-12
==========
+ Update sub-modules and modify code to use these new versions where needed.
+ Use 8.3 path for Firefox profile to make sure Firefox can use it.
+ Use mFileSystem everywhere.
+ Fix issue where statistics written to file for repeated runs would cause an
  exception because a string was converted to Unicode when it should not be.
+ Fixed highlighting of relevant binary versions.

2017-10-10
==========
+ "Cleanup" code is now available for Firefox and Edge; it allows removing of
  stored state before starting the application to prevent previous crashes from
  affecting the outcome of the next run.
+ Version checks have been simplified to only handle recent versions of various
  sub-modules. This means very old versions will throw exceptions, rather than
  be handled correctly as such.
+ Sub-modules have been overhauled and code has been moved around. These are
  internal changes that should not affect normal usage.

2017-09-25
==========
+ Invalid JSON encoded arguments will now result in error messages that include
  the JSON decode error, which should help resolve these issues faster.

2017-09-22
==========
+ New cBugId version has a few improvements, but nothing mayor for the end
  user of BugId.

2017-09-18
==========
+ New cBugId version has a few improvements, but nothing mayor for the end
  user of BugId.
+ C++ and WinRT exceptions are now disabled in `edge` and `msie`, as they have
  never been associated with a bug in my experience and disabling them speeds
  up BugId and reduces memory usage significantly.
+ Check for binaries that are allowed to run without pageheap is now case-
  insensitive, as file names in Windows are case-insensitive.

2017-08-30
==========
+ New cBugId version checks if page heap has been enabled a lot faster in order
  to speed things up significantly. A few minor bugs where also fixed and if
  symbols cannot be loaded, they will be downloaded again from the server if
  possible, overwriting local cached copies.
+ Application keywords `chrome_x86` and `chrome_x64` will no longer select
  `chrome-sxs_*` if it is installed. `chrome_x64` will select Chrome installed
  in `Program Files (x86)`, as x64 versions of Chrome can be installed there.

2017-08-25
==========
+ New cBugId version fixes bugs #38 & #39.
+ You can now specify the path where you want the dumps to be saved by setting
  `dxConfig["cBugId"]["sDumpPath"]` in `dxConfig.py` or by using the
  `--cBugId.sDumpPath="path"` command-line argument. You can also request a
  full memory dump (as opposed to the default mini dump) by setting
  `dxConfig["cBugId"]["bFullDump"]` in `dxConfig.py` to `True` or by using the
  `--cBugId.bFullDump=true` command-line argument.

2017-08-22
==========
+ New cBugId version fixes a number of bugs and has a few improvements. BugId
  itself did not need to be modified to accommodate some these changes.

2017-08-17
==========
+ New cBugId version fixes a number of bugs and has a few improvements. BugId
  has been modified to accommodate some these changes.
+ Prevent exception when bug location is unknown.
+ conhost.exe is allowed to run without page heap
+ RuntimeBroker.exe is no longer considered part of Edge.
+ Chrome is now run with the `--jsflags"--expose-gc"` and
  `--enable-logging=stderr` command-line arguments.

2017-07-17
==========
+ New cBugId version fixes a bug where the wrong symbol for a function could
  be used in the BugId and HTML report in same cases. In these cases the
  function symbol would have an offset, which no function symbol used by BugId
  should ever have. This new version fixes this issue, and may result in
  different BugIds for the same issue for that reason.
  This new version also has improved bug translations, and gathers up to 100
  stack frames for analysis (up from 40). These to changes may also result in
  different, but improved BugIds for the same bugs.
+ Default Edge argument has been re-introduced; it got removed by accident in
  the recent code changes to be able to debug UWP apps.
+ New `-v`/`--verbose` switch allows you to see cdb.exe I/O. You no longer
  need to modify `cBugId`'s `dxConfig` settings to do this. But you can make
  this the default by setting `bOutputCdbIO` to True in `dxConfig.py`.

2017-07-10
==========
+ Fixed a bug in the previous release that prevented BugId from working
  altogether.
+ New cBugId version has some minor bug fixes and improved bug ids and HTML
  report.

2017-07-03
==========
+ Fixed bug in previous oConsole update so it now handles redirected output
  correctly again.
+ Fixed bug where errorlevel/exit code was not set to 3 for some internal
  errors.
+ New cBugId version has some minor bug fixes.
+ Add errorlevel/exit code to usage information.

2017-06-30
==========
+ Updated oConsole to allow conservation of fore- and background colors, and
  changed BugId to not modify the background color.
+ New cBugId version.

2017-06-27
==========
+ I did not actually change any code, but I forgot to mentioned that the format
  for BugId arguments has changed slightly in previous versions. Most
  importantly, you will need to precede any arguments you want to pass to your
  application with `--` to separate BugId arguments from application arguments,
  as in:
  ```
  > BugId <bug id arguments> -- <application arguments>
  ```
  Run `BugId -?` for a more complete description of the new arguments format.

2017-06-26
==========
+ New cBugId has updates, improvements and bug fixes.
+ Fixed bug in fPrintLogo.

2017-05-31
==========
+ BugId now has an ASCII art logo and outputs text to the console in various
  colors!
+ New cBugId version has lots of improvements. BugId code was changed to use
  some of the new features and work with the changes in the API.
+ Added `--version` switch, which checks for updates and displays version
  information.
+ New processes are shown as they are created.
+ Google Chrome default arguments have been updated.
+ Page heap is now enabled for Firefox updater.exe as well.
+ Adobe Reader is now terminated when the main process exits.
+ The `AdobeARM.exe` binary was added to `pageheap.cmd` for `acrobatdc`.
  I don't have a VM with the non-DC `acrobat` to test if it should be added
  there as well. Let me know if you find that it does and I will add it!
+ When a main process terminates, it's process id and binary name are shown.
+ When page heap is not enabled for a process, an error is shown and BugId
  terminates. This can be disabled with the `--cBugId.bEnsurePageHeap=false`
  switch, or by making the appropriate changed in `dxConfig.py`. A whitelist
  of applications that are allowed to run without page heap is also available
  (`gasBinariesThatAreAllowedToRunWithoutPageHeap` in `BugId.py`). Let me know
  if you would like to see anything added to this whitelist.
+ Internal exceptions now include a call stack. This should make tracking down
  an externally reported issue a lot easier. Don't forget to report any bugs
  you find in BugId itself!!
+ Added `bExcessiveCPUUsageCheckEnabled` (default `False`) which disables
  excessive CPU usage checks by default. Set to `True` to re-enable this.
+ `PageHeap.cmd` now accepts an application keyword, which causes it to enable
  page heap for all the relevant binaries for that application. This replaces
  all the application specific `PageHeap-*.cmd` files.

2017-03-24
==========
+ new "bApplicationTerminatesWithMainProcess" config setting allows an
  application to continue running after any one of the "main" processes
  terminates. This is disabled by default, which is a change from the previous
  behavior. To revert to previous behavior use this command-line arguments:
  "--bApplicationTerminatesWithMainProcess=true".
  The list of know applications config settings has this set to true where
  applicable.
+ New cBugId version provides improved output in some cases.
+ Link to example reports now works again.
+ Timeouts for acrobat have been increased, as I found the application can be
  slow to load.
+ Other cosmetic and internal changes were made that should not affect the
  end-user.

2017-01-31
==========
+ New cBugId version now detects double-frees correctly.

2016-12-30
==========
+ New cBugId version fixes a number of bugs and improves detection of stack
  related access violations.

2016-12-22
==========
+ Update help
+ Reset start-time used to calculate overhead right before application is
  started, so it is not cumulative when running with "--forever".
+ Create statistics file when running with "--forever" that contains info about
  the number of times each Bug Id was seen.
+ New cBugId version fixes a number of bugs and improves detection of recursive
  function calls.

2016-12-15
==========
+ New cBugId version fixes a number of bugs.

2016-12-14
==========
+ New cBugId version fixes a number of bugs.

2016-12-11
==========
+ New cBugId version improves the way symbol loading errors are handled, and
  how VERIFIER STOP messages are handled. This should prevent some assertion
  failures in edge cases. There is also a fix for a bug in the HTML reports
  where blocks where not non-collapsible.

2016-12-05
==========
+ `cBugId` now exposes the `sOSISA` property, which represents the Operating
  System's Instruction Set Architecture. `BugId` will use this property to
  determine which version of cdb to use. This should fix some cases where
  `BugId` incorrectly assumed the OS architecture was `x86` rather than `x64`.

2016-11-30
==========
BugId changes
-------------
+ The use-after-free BugId now contains the offset from the end of the memory
  page in which the freed memory allocation was stored, at which the code
  attempted to use the freed memory. For instance, if an application attempts
  to read data at offset 4 in a freed 0x10 byte memory block, the BugId will
  now be `UAFR[]~0xC`, as the end of the memory block aligns with the end of
  the memory page and a read at offset 4 is 0xC bytes away from that end.
+ A use-after-free that is also out-of-bounds will now be reported as such
  whenever possible. For instance, if an application attempts to read data at
  offset 0x14 in a freed 0x10 byte memory block (i.e. beyond the end of the
  freed memory block), the BugId will now be `OOBUAFR[]+0x4`, as the end of the
  memory block aligns with the end of the memory page and a read at offset 0x14
  is 0x4 bytes after that end.
Note that because of alignment, a 0xC byte memory block will be stored 0x10
bytes before the end of a page, just like a 0x10 byte memory block. The above
two changes in the BugId do not provide any information about the memory block
size, as this is currently not possible. The offset they provide is therefore
only marginally useful. However, they are highly useful if you are
investigating a vuln and manage to modify this offset by modifying the repro
case, as this indicates your changes to the repro provide some level of control
over the use-after-free vulnerability.

2016-11-24
==========
+ Minor fixes and improvements in cBugId engine, which require some rewriting
  of BugId. This should solve a timing issue where a callback could get called
  before the cBugId constructor was finished, causing BugId to try to use the
  oBugId global before it was set to a cBugId instance.

2016-11-22
==========
+ Minor fixes and improvements in cBugId engine.

2016-11-21
==========
+ Size of memory region dumps is now limited to prevent errors, long analysis
  time and very large HTML reports.
+ HTML reports for access violations should now always contain the access
  violation address in memory region dumps if applicable.
+ Fixed minor errors in cBugId engine.

2016-11-17
==========
+ HTML reports now start with the Stack section opened.

2016-11-16
==========
+ Added a `--forever` switch, which runs the application repeatedly with the
  given settings.
+ New cBugId version has various improvements, including better rendering of
  HTML reports in MSIE and twitter card info in HTML reports. It also fixes a
  few minor issues.

2016-11-08
==========
+ Added a `--fast` switch, which disables HTML reports, symbol servers and
  the use of `_NT_SYMBOL_PATH`. This speeds up analysis and can be very useful
  if symbols are already cached and you do not need a report.
+ cBugId has had quite a few changes, some of these can result in different
  BugIds for the same crash compared to previous versions. They also include
  some changes that should speed up analysis significantly.
+ Symbol sources are now separated into local symbol paths, local symbol cache
  paths, and symbol server URLs. See `dxConfig` for details.
+ Symbol loading is less aggressive than it used to be, as this improves the
  analysis speed significantly. If you notice odd BugIds because symbol fail to
  load, try setting `BugId.bMakeSureSymbolsAreLoaded` to `true` to switch back
  to the older, slower behavior. Once Symbols have been cached, you should be
  able to set it back to `false` and enjoy the speedup without further symbol
  related issues.

2016-10-20
==========
+ cBugId no longer counts stack frames without a symbol towards the number of
  hashed frames. They are added to the hash as a placeholder (`-`), so the hash
  may get larger than what you might have previously expected.

2016-10-13
==========
+ HTML report now has tabs replaced with spaces where appropriate.
+ A number of other minor cBugId changes and/or bug fixes.

2016-10-12
==========
+ cBugId now cleans up stack for VERIFIER STOP messages.

2016-10-11
==========
+ cBugId bug fixes and reverse change that enables page heap automatically (it
  was causing access violations).

2016-10-10
==========
+ Page heap settings are now applied by default to all processes. The BugId
  settings can be used to disable this or modify which settings are applied.
+ Detect and report misaligned frees as `MisalignedFree[size]+offset`. e.g if
  the code attempts to free heap using a pointer that is at offset 0x8 of a
  0x20 byte block, you will get a BugId of `MisalignedFree[0x20]+8`
+ The `FailFast2:` prefix was removed from FailFast exceptions.
+ Both `LegacyGS` and `StackCookie` FailFast exceptions are now reported as
  `OOBW[Stack]` (as in: Out-Of-Bounds Write on the Stack).
+ New version of cBugId includes additional minor improvements and bug fixes.

2016-10-05
==========
+ New version of cBugId fixes two bugs.

2016-10-04
==========
+ New version of cBugId fixes a few bugs and improves HTML reports.

2016-09-29
==========
+ PageHeap-Chrome.cmd now sets the CHROME_ALLOCATOR environment variable to the
  right value both in the current process and in all processes through the
  registry. The later requires logging off and on again to propagate.

2016-09-13
==========
Breaking changes
----------------
+ Default security impact is no longer None but "Denial of Service".

New features
------------
+ Add support for Chrome Canary through the `chrome-sxs`, `chrome-sxs_x86`,
  and `chrome-sxs_x64` keywords.
+ Add support for Firefox Developer Edition through the `firefox-dev`,
  `firefox-dev_x86` and `firefox-dev_x64` keywords.
+ Improve detection of x86/x64 versions of chrome, firefox and MSIE. i.e.
  the `chrome` keyword will now run the x64 or x86 version of chrome, whichever
  is installed (preferring x64 over x86 if both are installed).

Improvements
------------
+ Make HTML report information similar to what BugId outputs on the console.

Bug fixes
---------
+ Fix bug where binary version information was not available when HTML report
  was not generated.

2016-09-12
==========
Breaking changes
----------------
+ Remove "@" prefix from application keywords; as this doesn't always work with
  powershell: the argument appears to disappear. Now you can (again) simply use
  `chrome`, `foxit`, `msie`, etc...
+ New version of cBugId handles STATUS_HANDLE_NOT_CLOSABLE exceptions similar
  to other handle related exceptions.

New features
------------
+ Output binary version information for the process' binary and optionally the
  binary in which the bug is located, if it's not the process' binary.
+ New version of cBugId outputs application command-line in HTML report.
+ Add support for Adobe Reader DC through `acrobatdc` keyword.

Bug fixes
---------
+ Rewrote argument parsing logic to fix issue #21.
+ Fix path for Adobe Reader through the `acrobat` keyword.
+ Apply settings provided on the command line after applying application
  specific settings, so you can override the later using the former.
+ Update cBugId to latest version, which includes bug fixes.

2016-09-08
==========
+ Add PageHeap-*.cmd scripts for Chrome, Firefox and Flash (though you won't
  want to use the first two, as these browsers use their own heap allocation
  engine and page heap will have little use).
+ Support for Adobe Reader through the @acrobat keyword.
+ Update cBugId to latest version, which includes bug fixes.

2016-09-07
==========
+ Update cBugId to latest version, which includes bug fixes and modifies some
  BugIds by replacing "?" with "_" in "AV?" and stack hashes.

2016-09-05
==========
+ Update cBugId to latest version, which includes bug fixes but no API changes.

2016-08-31
==========
+ Make @chrome OS ISA dependent and add @chrome_x86 and @chrome_x64 to select
  different ISAs when you want to use a specific ISA.
+ Make @firefox OS ISA dependent and add @firefox_x86 and @firefox_x64 to
  select different ISAs when you want to use a specific ISA.
+ Rename @msie32 and @msie64 to @msie_x86 and @msie_x64 for consistency.
+ Update version of cBugId, which has the following mayor changes:
  + The BugId can now include the number of overwritten bytes, and a hash of
    their values if you supply the --BugId.uHeapCorruptedBytesHashChars=uint
    argument with a value of 1 or more. This can be useful when you want to
    detect if two instances of heap corruption wrote the same data to corrupt
    the heap. When enabled, a string with format "~L:H" is added to the BugId,
    where "L" is the length of the corruption and "H" is the hash. Note that L
    is not influenced by the --BugId.uArchitectureIndependentBugIdBits setting,
    so BugId's created using this feature on x86 and x64 versions of an
    application may differ.
  + You can now specify which version of cdb (x86 or x64) you want BugId to
    use. This can improve results when you use the x86 cdb to debug x86
    applications: using the x64 cdb may prevent BugId from collecting page heap
    information. The correct cdb version is automatically select for
    applications run using an "@keyword". 
  See the cBugId RELEASE NOTES.txt file for all details.