import os;
sBaseFolderPath = os.path.dirname(__file__);
dxConfig = {
  "bSaveReport": True,          # Have BugId.py output a HTML formatted crash report.
  "bSaveTestReports": False,    # Have Tests.py output a HTML formatted crash report.
  "asSymbolServerURLs": ["http://msdl.microsoft.com/download/symbols"],
  "nExcessiveCPUUsageCheckInitialTimeout": 5, # Start checking the application for excessive CPU usage
                                                    # after this many seconds.
  "BugId": {
    # The values from src\dxBugIdConfig.py get loaded here, but you can override them here.
  },
};