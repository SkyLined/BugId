import os;

# Note that some of these settings may be overwritten by application specific settings found in BugId.py in the
# `gdApplication_dxSettings_by_sKeyword` variable. These settings should probably be moved here, but I am not sure
# yet how I might implement this. For now, if you want to change such settings, you can either modify BugId.py and
# change values in `gdApplication_dxSettings_by_sKeyword`, or provide them on the command line.

dxConfig = {
  "bGenerateReportHTML": True,                    # Set to True to have BugId.py output a HTML formatted crash report.
  "asLocalSymbolPaths": None,                     # List of local symbol paths (symbols created for a local build or
                                                  # downloaded with a remote build, None = use default).
  "asSymbolCachePaths": None,                     # List of symbol cache paths (Where to download symbols from a remote
                                                  # server, None = use default).
  "asSymbolServerURLs": None,                     # List of symbol server URLs (where to try to download symbosl from 
                                                  # if none are found locally, None = use default).
  "bExcessiveCPUUsageCheckEnabled": False,        # Set to True to enabled checking for excessive CPU usage in the
                                                  # application. This used to be the default, but I've found most
                                                  # people prefer not having this check.
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

# Load cBugId and apply its dxConfig:
from cBugId import cBugId;
# Apply desired changes in dxConfig["cBugId"] to cBugId.dxConfig.
for (sName, xValue) in dxConfig["cBugId"].items():
  # Note that this does not allow modifying individual properties of dictionaries in dxConfig for cBugId.
  # But at this time, there are no dictionaries in dxConfig, so this is not required.
  cBugId.dxConfig[sName] = xValue;
# Replace dxConfig["cBugId"] with actual dxConfig for cBugId.
dxConfig["cBugId"] = cBugId.dxConfig;
