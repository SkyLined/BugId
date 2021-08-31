import sys;

from fPrintUsageInformation import fPrintUsageInformation;
from fPrintVersionInformation import fPrintVersionInformation;
from fPrintLicenseInformation import fPrintLicenseInformation;
from mColors import *;
from mProductDetails import faoGetLicensesFromRegistry, faoGetLicensesFromFile;

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
      if sLowerName in ["license-server-url"]:
        if not s0Value:
          oConsole.fOutput(ERROR, "- Invalid ", ERROR_INFO, sLowerName, ERROR, " argument:");
          oConsole.fOutput(ERROR, "  You must provide a URL for a license server as value for this argument.");
          sys.exit(1);
        try:
          sbLicenseServerURL = bytes(s0Value, "ascii", "strict");
        except:
          oConsole.fOutput(ERROR, "- Invalid ", ERROR_INFO, sLowerName, ERROR, " argument:");
          oConsole.fOutput(ERROR, "  You must provide a valid URL for a license server as value for this argument.");
          sys.exit(1);
        for oProductDetails in mProductDetails.faoGetProductDetailsForAllLoadedModules():
          if oProductDetails.sb0LicenseServerURL is not None:
            oProductDetails.sb0LicenseServerURL = sbLicenseServerURL;
      elif sLowerName in ["license-clear-cache"]:
        # Remove all cached licenses from registry
        aoCachedLicenses = faoGetLicensesFromRegistry();
        if len(aoCachedLicenses) == 0:
          oConsole.fOutput("* There are ", INFO, "no", NORMAL, " licenses cached in the registry.");
        else:
          oConsole.fOutput("* Removing ", INFO, str(len(aoCachedLicenses)), NORMAL, " cached licenses from the registry:");
          for oLicense in aoCachedLicenses:
            assert oLicense.fbRemoveFromRegistry(bThrowErrors = True), \
                "Unreachable code !?";
            oConsole.fOutput(
              "  - License ", INFO, oLicense.sLicenseId,
              NORMAL, " covering ", INFO, oLicense.sUsageTypeDescription, 
              NORMAL, " by ", INFO, oLicense.sLicenseeName,
              NORMAL, " of ", INFO, oLicense.asProductNames[0],
              NORMAL, " on ", INFO, str(oLicense.uLicensedInstances), NORMAL, " machine", "s" if oLicense.uLicensedInstances != 1 else "",
              NORMAL, ".",
            );
        sys.exit(0);
      elif sLowerName in ["license-load-file"]:
        sPath = s0Value or "#license.asc";
        aoLoadedLicenses = faoGetLicensesFromFile(sPath);
        if len(aoLoadedLicenses) == 0:
          oConsole.fOutput("* There are ", INFO, "no", NORMAL, " licenses in the file ", INFO, sPath, NORMAL, ".");
        else:
          oConsole.fOutput("* Caching ", INFO, str(len(aoLoadedLicenses)), NORMAL, " licenses from file ", INFO, sPath, NORMAL, ":");
          for oLicense in faoGetLicensesFromFile(sPath):
            oLicense.fWriteToRegistry();
            oConsole.fOutput(
              "  ", OK, "+", NORMAL, " License ", INFO, oLicense.sLicenseId,
              NORMAL, " covering ", INFO, oLicense.sUsageTypeDescription, 
              NORMAL, " by ", INFO, oLicense.sLicenseeName,
              NORMAL, " of ", INFO, oLicense.asProductNames[0],
              NORMAL, " on ", INFO, str(oLicense.uLicensedInstances), NORMAL, " machine", "s" if oLicense.uLicensedInstances != 1 else "",
              NORMAL, ".",
            );
        sys.exit(0);
      elif sLowerName == "arguments":
        if not s0Value:
          oConsole.fOutput(ERROR, "- Invalid ", ERROR_INFO, sLowerName, ERROR, " argument:");
          oConsole.fOutput(ERROR, "  You must provide a path to a file containing arguments as value for this argument.");
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