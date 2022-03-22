import os, re, subprocess;
from mBugId import cBugId;

rbVersion = re.compile(b"^cdb version (.*)\n$");

def fdsGetAdditionalVersionByName():
  dsVersion_by_sName = {};
  
  for sISA in ["x86", "x64"]:
    s0CdbBinaryPath = cBugId.fs0GetCdbBinaryPath(sISA);
    if s0CdbBinaryPath is None:
      dsVersion_by_sName["cdb.exe (%s)" % sISA] = "not available";
    elif not os.path.isfile(s0CdbBinaryPath):
      dsVersion_by_sName["cdb.exe (%s)" % sISA] = "not found";
    else:
      try:
        oCdbProcess = subprocess.run(
          args = [s0CdbBinaryPath, "-version"],
          capture_output = True,
        );
      except Exception as oException:
        dsVersion_by_sName["cdb.exe (%s)" % sISA] = "unknown";
      else:
        obVersionMatch = rbVersion.match(oCdbProcess.stdout);
        if obVersionMatch:
          dsVersion_by_sName["cdb.exe (%s)" % sISA] = str(obVersionMatch.group(1), "ascii", "strict");
        else:
          dsVersion_by_sName["cdb.exe (%s)" % sISA] = "unknown";
  
  return dsVersion_by_sName;