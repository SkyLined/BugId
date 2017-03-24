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