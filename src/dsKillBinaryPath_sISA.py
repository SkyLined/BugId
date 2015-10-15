import os;
from sOSISA import sOSISA;

dasPotentialKillBinaryPaths_sISA = {"x86": [], "x64": []};

# Add "kill", "kill_x86" and "kill_x64" environment variables if provided:
sKill = os.getenv("kill");
if sKill:
  dasPotentialKillBinaryPaths_sISA[sOSISA].append(sKill.strip('"'));
sKill_x86 = os.getenv("kill_x86");
if sKill_x86:
  dasPotentialKillBinaryPaths_sISA["x86"].append(sKill_x86.strip('"'));
sKill_x64 = os.getenv("kill_x64");
if sKill_x64:
  dasPotentialKillBinaryPaths_sISA["x64"].append(sKill_x64.strip('"'));

# Add default installation paths:
sBaseFolderPath = os.path.dirname(__file__);
sKillBinaryPathTemplate = os.path.join(sBaseFolderPath, "..", "modules", "Kill", "bin", "Kill_%s.exe");
dasPotentialKillBinaryPaths_sISA["x86"].append(sKillBinaryPathTemplate % "x86");
dasPotentialKillBinaryPaths_sISA["x64"].append(sKillBinaryPathTemplate % "x64");

dsKillBinaryPath_sISA = {};
for (sISA, asPotentialKillBinaryPaths) in dasPotentialKillBinaryPaths_sISA.items():
  for sPotentialKillBinaryPath in asPotentialKillBinaryPaths:
    if os.path.isfile(sPotentialKillBinaryPath):
      dsKillBinaryPath_sISA[sISA] = sPotentialKillBinaryPath;
      break;
