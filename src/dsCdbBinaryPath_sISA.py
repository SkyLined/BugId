import os;
from sOSISA import sOSISA;

dasPotentialCdbBinaryPaths_sISA = {"x86": [], "x64": []};

# Add "cdb", "cdb_x86" and "cdb_x64" environment variables if provided:
sCdb = os.getenv("cdb");
if sCdb:
  dasPotentialCdbBinaryPaths_sISA[sOSISA].append(sCdb.strip('"'));
sCdb_x86 = os.getenv("cdb_x86");
if sCdb_x86:
  dasPotentialCdbBinaryPaths_sISA["x86"].append(sCdb_x86.strip('"'));
sCdb_x64 = os.getenv("cdb_x64");
if sCdb_x64:
  dasPotentialCdbBinaryPaths_sISA["x64"].append(sCdb_x64.strip('"'));

# Add default installation paths:
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");
dasPotentialCdbBinaryPaths_sISA["x86"].extend([
  os.path.join(sProgramFilesPath_x86, "Windows Kits", "8.1", "Debuggers", "x86", "cdb.exe"),    # WDK 8.1
  os.path.join(sProgramFilesPath_x86, "Windows Kits", "10", "Debuggers", "x86", "cdb.exe"),    # WDK 8.1
]);
if sOSISA == "x64":
  dasPotentialCdbBinaryPaths_sISA["x64"].extend([
    os.path.join(sProgramFilesPath_x64, "Windows Kits", "8.1", "Debuggers", "x64", "cdb.exe"),  # WDK 8.1
    os.path.join(sProgramFilesPath_x64, "Windows Kits", "10", "Debuggers", "x64", "cdb.exe"),  # WDK 8.1
  ]);

dsCdbBinaryPath_sISA = {};
for (sISA, asPotentialCdbBinaryPaths) in dasPotentialCdbBinaryPaths_sISA.items():
  for sPotentialCdbBinaryPath in asPotentialCdbBinaryPaths:
    if os.path.isfile(sPotentialCdbBinaryPath):
      dsCdbBinaryPath_sISA[sISA] = sPotentialCdbBinaryPath;
      break;
