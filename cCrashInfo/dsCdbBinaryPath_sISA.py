import os;
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_AMD64 = os.getenv("ProgramW6432");
dasPotentialCdbBinaryPaths_sISA = {
  "x86": [
    os.path.join(sProgramFilesPath_x86, "Windows Kits", "8.1", "Debuggers", "x86", "cdb.exe"),    # WDK 8.1
    os.path.join(os.path.dirname(__file__), "Debugging Tools for Windows (x86)", "cdb.exe")       # local
  ],
  "AMD64": [
    os.path.join(sProgramFilesPath_AMD64, "Windows Kits", "8.1", "Debuggers", "x64", "cdb.exe"),  # WDK 8.1
    os.path.join(os.path.dirname(__file__), "Debugging Tools for Windows (AMD64)", "cdb.exe"),    # local
  ],
};
dsCdbBinaryPath_sISA = {};
for (sISA, asPotentialCdbBinaryPaths) in dasPotentialCdbBinaryPaths_sISA:
  for sPotentialCdbBinaryPath in asPotentialCdbBinaryPaths:
    if os.path.isfile(sPotentialCdbBinaryPath):
      dsCdbBinaryPath_sISA[sISA] = sPotentialCdbBinaryPath;
      break;