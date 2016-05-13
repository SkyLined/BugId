import os;
sBaseFolderPath = os.path.dirname(__file__);
dxConfig = {
  "bSaveReport": True,          # Have BugId.py output a HTML formatted crash report.
  "bSaveTestReports": False,    # Have Tests.py output a HTML formatted crash report.
  "sKillBinaryPath_x86": os.path.join(sBaseFolderPath, "modules", "Kill", "bin", "Kill_x86.exe"),
  "sKillBinaryPath_x64": os.path.join(sBaseFolderPath, "modules", "Kill", "bin", "Kill_x64.exe"),
  "asSymbolServerURLs": ["http://msdl.microsoft.com/download/symbols"],
  "nHighCPUUsageCheckInitialTimeout": 10, # Start checking the application for excessive CPU usage after this many seconds.
  "BugId": {
    # The values from src\dxBugIdConfig.py get loaded here, but you can override them here.
  },
};