import os;
sBaseFolderPath = os.path.dirname(__file__);
dxConfig = {
  "bSaveReport": True,          # Have BugId.py output a HTML formatted crash report.
  "bSaveTestReports": False,    # Have Tests.py output a HTML formatted crash report.
  "asSymbolServerURLs": ["http://msdl.microsoft.com/download/symbols"],
  "nExcessiveCPUUsageCheckInitialTimeout": 5, # Start checking the application for excessive CPU usage
                                                    # after this many seconds.
  "sTest": "http://%s:28876/" % os.getenv("COMPUTERNAME"), # Default URL for browser tests, can be a file path for other applications.
  "BugId": {
    # The values from src\dxBugIdConfig.py get loaded here, but you can override them here.
  },
};