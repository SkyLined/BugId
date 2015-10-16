import os;
sBaseFolderPath = os.path.dirname(__file__);
dxConfig = {
  "bSaveReport": True,          # Have BugId.py output a HTML formatted crash report.
  "sKillBinaryPath_x86": os.path.join(sBaseFolderPath, "modules", "Kill", "bin", "Kill_x86.exe"),
  "sKillBinaryPath_x64": os.path.join(sBaseFolderPath, "modules", "Kill", "bin", "Kill_x64.exe"),
};