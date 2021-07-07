import sys;

from fPrintUsageInformation import fPrintUsageInformation;
from fPrintVersionInformation import fPrintVersionInformation;
from fPrintLicenseInformation import fPrintLicenseInformation;
from mColors import *;

def fatsArgumentLowerNameAndValue():
  atsArgumentNameAndValue = [];
  asArguments = sys.argv[1:];
  while len(asArguments) > 0:
    sArgument = asArguments.pop(0);
    if sArgument == "--":
      break;
    if len(sArgument) >= 2 and sArgument.startswith("-") or sArgument.startswith("/"):
      if "=" in sArgument:
        (sNameWithPrefix, s0Value) = sArgument.split("=", 1);
      else:
        (sNameWithPrefix, s0Value) = (sArgument, None);
      if sNameWithPrefix.startswith("--"):
        sLowerName = sNameWithPrefix[2:].lower();
      else:
        sLowerName = sNameWithPrefix[1:].lower();
      if sLowerName in ["h", "?", "help"]:
        fPrintUsageInformation();
        sys.exit(0);
      if sLowerName in ["version", "version-check"]:
        fPrintVersionInformation(
          bCheckForUpdates = sLowerName == "version-check",
          bShowInstallationFolders = sLowerName == "version",
        );
        sys.exit(0);
      if sLowerName in ["license", "license-update"]:
        fPrintLicenseInformation(
          bUpdateIfNeeded = sLowerName == "license-update",
        );
        sys.exit(0);
      if sLowerName == "arguments":
        if not s0Value:
          oConsole.fOutput(ERROR, "- Invalid ", ERROR_INFO, sLowerName, ERROR, "argument:");
          oConsole.fOutput(ERROR, "  You must provide a value for this argument.");
          sys.exit(1);
        # Read additional arguments from file and insert them after the current argument.
        oArgumentsFile = cFileSystemItem(s0Value);
        if not oArgumentsFile.fbIsFile():
          oConsole.fOutput(ERROR, "- Invalid ", ERROR_INFO, sLowerName, ERROR, " argument:");
          oConsole.fOutput(ERROR, "  ", ERROR_INFO, oArgumentsFile.sPath);
          oConsole.fOutput(ERROR, "  File not found.");
          sys.exit(1);
        sArgumentsFileContent = str(oArgumentsFile.fsbRead(), "utf-8");
        asArguments = [
          os.path.expandvars(sStrippedArgumentFileLine) for sStrippedArgumentFileLine in [
            sArgumentFileLine.strip() for sArgumentFileLine in sArgumentsFileContent.split("\n")
          ] if sStrippedArgumentFileLine != ""
        ] + asArguments;
      else:
        atsArgumentNameAndValue.append((sArgument, sLowerName, s0Value));
    else:
      atsArgumentNameAndValue.append((sArgument, None, sArgument));
  while len(asArguments) > 0:
    sArgument = asArguments.pop(0);
    atsArgumentNameAndValue.append((sArgument, None, None));
  return atsArgumentNameAndValue;