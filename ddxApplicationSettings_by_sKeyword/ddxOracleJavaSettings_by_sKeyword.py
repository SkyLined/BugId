import os;
from fsFirstExistingFile import fsFirstExistingFile;
sProgramFilesPath = os.getenv("ProgramFiles");
sProgramFilesPath_x86 = os.getenv("ProgramFiles(x86)") or os.getenv("ProgramFiles");
sProgramFilesPath_x64 = os.getenv("ProgramW6432");

dxConfigSettings = {
  "bApplicationTerminatesWithMainProcess": True,
  "cBugId.bIgnoreFirstChanceAccessViolations": True,
};

sApplicationBinaryPath_x64 = sProgramFilesPath_x64 and fsFirstExistingFile(
  r"%s\Java\jre-9.0.1\bin\java.exe" % sProgramFilesPath_x64,
  # TODO: add other versions.
);
sApplicationBinaryPath_x86 = fsFirstExistingFile(
  r"%s\Java\jre-9.0.1\bin\java.exe" % sProgramFilesPath_x86,
  # TODO: add other versions.
);
sApplicationBinaryPath = sApplicationBinaryPath_x64 or sApplicationBinaryPath_x86;

def fasGetJavaOptionalArguments(bForHelp = False):
  return ["-jar", "repro.jar"]; # Does not matter if it's for help or not: value is the same

ddxOracleJavaSettings_by_sKeyword = {
  "java": {
    "sBinaryPath": sApplicationBinaryPath,
    "fasGetOptionalArguments": fasGetJavaOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
  },
  "java_x86": {
    "sBinaryPath": sApplicationBinaryPath_x86,
    "fasGetOptionalArguments": fasGetJavaOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x86",
  },
  "java_x64": {
    "sBinaryPath": sApplicationBinaryPath_x64,
    "fasGetOptionalArguments": fasGetJavaOptionalArguments,
    "dxConfigSettings": dxConfigSettings,
    "sISA": "x64",
  },
};