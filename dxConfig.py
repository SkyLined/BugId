import os;
sBaseFolderPath = os.path.dirname(__file__);
dxConfig = {
  "bGenerateReportHTML": True,                    # Set to True to have BugId.py output a HTML formatted crash report.
  "asLocalSymbolPaths": None,                     # List of local symbol paths (symbols created for a local build or
                                                  # downloaded with a remote build, None = use default).
  "asSymbolCachePaths": None,                     # List of symbol cache paths (Where to download symbols from a remote
                                                  # server, None = use default).
  "asSymbolServerURLs": None,                     # List of symbol server URLs (where to try to download symbosl from 
                                                  # if none are found locally, None = use default).
  "nExcessiveCPUUsageCheckInitialTimeout": 5,     # Start checking the application for excessive CPU usage after this
                                                  # many seconds. Lower values yield results faster, but slow down
                                                  # testing and may give false positives if startup takes long.
                                                  # Set to 0 or null to disable excessive CPU usage checks.
  "sDefaultBrowserTestURL": "http://%s:28876/" % os.getenv("COMPUTERNAME"), # Default URL for browser tests.
  "nApplicationMaxRunTime": None,                 # Terminate BugId if the application has been running for this many
                                                  # seconds without crashing. None to allow the application to run
                                                  # forever.
  "bApplicationTerminatesWithMainProcess": False, # Terminate BugId if one of the application's main processes is
                                                  # terminated. This can be useful if the application uses background
                                                  # processes (update checkers, brokers, etc.) which are also debugged,
                                                  # and that do not terminate when the application does: enabling this
                                                  # setting will ensure BugId does not run forever in such cases.
  "bShowLicenseAndDonationInfo": True,            # Set to False to disable the licensing and donations information
                                                  # shown at the end of each run. Feel free to act on it first :)
  "bUseUnicodeReportFileNames": False,            # Disable if you are experiencing "Invalid file name" errors
                                                  # when trying to write bug reports. Enable if you want the report
                                                  # file name to look very similar to the BugId by translating invalid
                                                  # characters to similarly looking Unicode characters.
  "sReportFolderPath": None,                      # You can specify a folder in which you want to save reports. If you
                                                  # set this to None, reports will be stored in the current working
                                                  # directory.
  "cBugId": {
    # The values from module\cBugId\dxBugIdConfig.py get loaded here.
    # Any value provided here will override the values loaded above.
    # You can also modify these from the command line using --cBugId.<settings name>=<JSON value>
  },
};