import os;


from mNotProvided import zNotProvided;

uKiloByte = 10 ** 3;
uMegaByte = 10 ** 6;
uGigaByte = 10 ** 9;
uTeraByte = 10 ** 12;

# Note that some of these settings may be overwritten by application specific settings found in BugId.py in the
# `gdApplication_dxSettings_by_sKeyword` variable. These settings should probably be moved here, but I am not sure
# yet how I might implement this. For now, if you want to change such settings, you can either modify BugId.py and
# change values in `gdApplication_dxSettings_by_sKeyword`, or provide them on the command line.

dxConfig = {
  "bQuiet": False,                                # Set to True to show very little output.
  "bVerbose": False,                              # Set to True to show verbose output.
  "bInteractive": False,                          # Set to False for fully automatic mode (e.g. do not ask for values
                                                  # when handling collateral bugs).
  "bGenerateReportHTML": True,                    # Set to True to have BugId.py output a HTML formatted crash report.
  "a0sLocalSymbolPaths": None,                    # List of local symbol paths (symbols created for a local build or
                                                  # downloaded with a remote build, None = no local symbol paths).
  "azsSymbolCachePaths": zNotProvided,            # List of symbol cache paths (Where to download symbols from a remote
                                                  # server, zNotProvided = use default).
  "azsSymbolServerURLs": zNotProvided,            # List of symbol server URLs (where to try to download symbosl from 
                                                  # if none are found locally, zNotProvided = use default).
  "bExcessiveCPUUsageCheckEnabled": False,        # Set to True to enabled checking for excessive CPU usage in the
                                                  # application. This used to be the default, but I've found most
                                                  # people prefer not having this check.
  "nExcessiveCPUUsageCheckInitialTimeoutInSeconds": 5, # Start checking the application for excessive CPU usage after this
                                                  # many seconds. Lower values yield results faster, but slow down
                                                  # testing and may give false positives if startup takes long.
  "sDefaultBrowserTestURL": "http://%s:28876/" % os.getenv("COMPUTERNAME"), # Default URL for browser tests.
  "n0ApplicationMaxRunTimeInSeconds": None,       # Terminate BugId if the application has been running for this many
                                                  # seconds without crashing. Set to `None` to allow the application to
                                                  # run forever.
  "u0ProcessMaxMemoryUse": None,                  # Limit the total amount of memory a single process can allocate. If
                                                  # a process attempts to allocate memory that would cause it to have
                                                  # more than this maximum allocated, the allocation will fail.
                                                  # Use this to detect excessive allocations in a single process before
                                                  # they cause a system-wide low memory situation that may prevent
                                                  # BugId and/or other applications from working correctly. Set to None
                                                  # to not apply this limit.
                                                  # This limit is enforced using Job objects or by reserving part of
                                                  # the process' address space. Some applications assign their
                                                  # processes to Job objects themselves and since processes cannot be
                                                  # assigned to more than one Job object, it may not be possible to
                                                  # apply this limit in that way. In such cases, BugId will reserve
                                                  # part of the process' address space to limit the ammount of memory
                                                  # the process can allocate. Unfortunately, this fallback method
                                                  # limits the amount of shared AND private memory the process can
                                                  # allocate AND reserve and may fragment the address space to the
                                                  # point where the process may not be able to allocate or reserve
                                                  # large blocks of memory even if this would not cause it to more than
                                                  # the maximum amount of memory allocated.
  "u0TotalMaxMemoryUse": None,                    # Limit the total amount of memory the application can allocate in
                                                  # all its processes. If a process attempts to allocate additional
                                                  # memory that would cause it to have more than this maximum allocated,
                                                  # the allocation will fail.
                                                  # Use this to detect excessive allocations by the application as a
                                                  # whole before they cause a system-wide low memory situation that may
                                                  # prevent BugId and/or other applications from working correctly. Set
                                                  # to None to not apply this limit.
                                                  # This limit is enforced using Job objects. Some applications assign
                                                  # their processes to Job objects themselves and since processes
                                                  # cannot be assigned to more than one Job object, it may not be
                                                  # possible to apply this limit.
  "bApplicationTerminatesWithMainProcess": False, # Terminate BugId if one of the application's main processes is
                                                  # terminated. This can be useful if the application uses background
                                                  # processes (update checkers, brokers, etc.) which are also debugged,
                                                  # and that do not terminate when the application does: enabling this
                                                  # setting will ensure BugId does not run forever in such cases.
  "bShowLicenseAndDonationInfo": True,            # Set to False to disable the licensing and donations information
                                                  # shown at the end of each run. Feel free to act on it first :)
  "bUseUnicodeReportFileNames": True,             # Disable if you are experiencing "Invalid file name" errors
                                                  # when trying to write bug reports. Enable if you want the report
                                                  # file name to look very similar to the BugId by translating invalid
                                                  # characters to similarly looking Unicode characters.
  "sReportFolderPath": None,                      # You can specify a folder in which you want to save reports. If you
                                                  # set this to None, reports will be stored in the current working
                                                  # directory. Note that the path where memory dumps are stored can be
                                                  # set using dxConfig["cBugId"]["sDumpPath"].
  "bCleanup": False,                              # Run application specific cleanup code (if available) before starting
                                                  # the application. This can be used to clean up corrupted state saved
                                                  # to disk. This is most useful when repeatedly running an application
                                                  # using the `-r` switch, when that application saves state to disk,
                                                  # and this state can get corrupted in a way that interferes with the
                                                  # proper functioning of the application. The cleanup function can be
                                                  # used to reset this state. Examples include web-browsers caching
                                                  # sites to disk, or restoring previously open tabs after a crash.
  "cBugId": {
    # The values from cBugId\dxConfig.py get loaded here unless they are provide here.
    # You can also modify these from the command line using --cBugId.<settings name>=<JSON value>
  },
};
