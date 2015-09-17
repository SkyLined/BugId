import os;

sOSISA = os.getenv("PROCESSOR_ARCHITEW6432") or os.getenv("PROCESSOR_ARCHITECTURE"); # AMD64 or x86
dasPotentialCdbBinaryPaths_sISA = {"x86": [], "AMD64": []};

# Add "cdb", "cdb_x86" and "cdb_x64" environment variables if provided:
sCdb = os.getenv("cdb");
if sCdb:
  dasPotentialCdbBinaryPaths_sISA[sOSISA].append(sCdb);
sCdb_x86 = os.getenv("cdb_x86");
if sCdb_x86:
  dasPotentialCdbBinaryPaths_sISA["x86"].append(sCdb_x86);
sCdb_x64 = os.getenv("cdb_x64");
if sCdb_x64:
  dasPotentialCdbBinaryPaths_sISA["AMD64"].append(sCdb_x64);

# Add default installation paths:
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_AMD64 = os.getenv("ProgramW6432");
dasPotentialCdbBinaryPaths_sISA["x86"].extend([
  os.path.join(sProgramFilesPath_x86, "Windows Kits", "8.1", "Debuggers", "x86", "cdb.exe"),    # WDK 8.1
]);
if sOSISA == "AMD64":
  dasPotentialCdbBinaryPaths_sISA["AMD64"].extend([
    os.path.join(sProgramFilesPath_AMD64, "Windows Kits", "8.1", "Debuggers", "x64", "cdb.exe"),  # WDK 8.1
  ]);

dsCdbBinaryPath_sISA = {};
for (sISA, asPotentialCdbBinaryPaths) in dasPotentialCdbBinaryPaths_sISA.items():
  for sPotentialCdbBinaryPath in asPotentialCdbBinaryPaths:
    if os.path.isfile(sPotentialCdbBinaryPath):
      dsCdbBinaryPath_sISA[sISA] = sPotentialCdbBinaryPath;
      break;
