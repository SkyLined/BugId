import os;
sBaseFolderPath = os.path.dirname(__file__);
dxConfig = {
  "bSaveReport": True,                            # Set to True to have BugId.py output a HTML formatted crash report.
  "asSymbolServerURLs": [                         # List of symbol server URLs for use by cdb.
    "http://msdl.microsoft.com/download/symbols"
  ],
  "nExcessiveCPUUsageCheckInitialTimeout": 5,     # Start checking the application for excessive CPU usage after this
                                                  # many seconds. Lower values yield results faster, but slow down
                                                  # testing and may give false positives if startup takes long.
  "sDefaultBrowserTestURL": "http://%s:28876/" % os.getenv("COMPUTERNAME"), # Default URL for browser tests.
  "nApplicationMaxRunTime": None,                 # Terminate BugId if the application has been running for this many
                                                  # seconds without crashing. None to allow the application to run
                                                  # forever.
  "bShowLicenseAndDonationInfo": True,            # Set to False to disable the licensing and donations information
                                                  # shown at the end of each run. Feel free to act on it first :)
  "bUseUnicodeReportFileNames": False,            # Disable if you are experiencing "Invalid file name" errors
                                                  # when trying to write bug reports. Enable if you want the report
                                                  # file name to look very similar to the BugId by translating invalid
                                                  # characters to similarly looking Unicode characters.
  "sReportFolderPath": None,                      # You can specify a folder in which you want to save reports. If you
                                                  # set this to None, reports will be stored in the current working
                                                  # directory.
  "BugId": {
    # The values from src\dxBugIdConfig.py get loaded here, but you can override them here.
  },
};