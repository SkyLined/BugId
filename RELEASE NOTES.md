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