import sys;

from fOutputUsageInformation import fOutputUsageInformation;
from fOutputVersionInformation import fOutputVersionInformation;
from fOutputLicenseInformation import fOutputLicenseInformation;
from mColorsAndChars import *;
from mExitCodes import *;
from mProductDetails import faoGetLicensesFromRegistry, faoGetLicensesFromFile;

def fExitWithBadArgumentValue(sArgumentName, sMessage):
  oConsole.fOutput(
    COLOR_ERROR, CHAR_ERROR,
    COLOR_NORMAL, " Invalid ",
    COLOR_INFO, sArgumentName,
    COLOR_NORMAL, " argument:",
  );
  oConsole.fOutput(
    COLOR_INFO, "  ", sMessage,
  );
  sys.exit(guExitCodeBadArgument);

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
        fOutputUsageInformation();
        sys.exit(guExitCodeSuccess);
      if sLowerName in ["version", "version-check"]:
        fOutputVersionInformation(
          bCheckForUpdates = sLowerName == "version-check",
          bShowInstallationFolders = sLowerName == "version",
        );
        sys.exit(guExitCodeSuccess);
      if sLowerName in ["license", "license-update"]:
        fOutputLicenseInformation(
          bUpdateIfNeeded = sLowerName == "license-update",
        );
        sys.exit(guExitCodeSuccess);
      if sLowerName in ["license-server-url"]:
        bValueIsIsValidURL = False;
        if s0Value:
          try:
            sbLicenseServerURL = bytes(s0Value, "ascii", "strict");
          except UnicodeError:
            pass;
          else:
            bValueIsIsValidURL = True;
        if not bValueIsIsValidURL:
          fExitWithBadArgumentValue(sLowerName, "You must provide a valid URL for a license server as value for this argument.");
        for oProductDetails in mProductDetails.faoGetProductDetailsForAllLoadedModules():
          if oProductDetails.sb0LicenseServerURL is not None:
            oProductDetails.sb0LicenseServerURL = sbLicenseServerURL;
      elif sLowerName in ["license-clear-cache"]:
        # Remove all cached licenses from registry
        aoCachedLicenses = faoGetLicensesFromRegistry();
        if len(aoCachedLicenses) == 0:
          oConsole.fOutput(
            COLOR_WARNING, CHAR_WARNING,
            COLOR_NORMAL, " There are ",
            COLOR_INFO, "no",
            COLOR_NORMAL, " licenses cached in the registry.",
          );
        else:
          oConsole.fOutput(
            COLOR_BUSY, CHAR_BUSY,
            COLOR_NORMAL, " Removing ",
            COLOR_INFO, str(len(aoCachedLicenses)),
            COLOR_NORMAL, " cached licenses from the registry:",
          );
          for oLicense in aoCachedLicenses:
            assert oLicense.fbRemoveFromRegistry(bThrowErrors = True), \
                "Unreachable code !?";
            oConsole.fOutput(
              "  ",
              COLOR_REMOVE, CHAR_REMOVE,
              COLOR_NORMAL, " License ", COLOR_INFO, oLicense.sLicenseId,
              COLOR_NORMAL, " covering ", COLOR_INFO, oLicense.sUsageTypeDescription, 
              COLOR_NORMAL, " by ", COLOR_INFO, oLicense.sLicenseeName,
              COLOR_NORMAL, " of ", COLOR_INFO, oLicense.asProductNames[0],
              COLOR_NORMAL, " on ", COLOR_INFO, str(oLicense.uLicensedInstances),
              COLOR_NORMAL, " machine", "s" if oLicense.uLicensedInstances != 1 else "", ".",
            );
        sys.exit(guExitCodeSuccess);
      elif sLowerName in ["license-load-file"]:
        sPath = s0Value or "#license.asc";
        oLicenseFile = cFileSystemItem(sPath);
        if not oLicenseFile.fbIsFile():
          fExitWithBadArgumentValue(sLowerName, "File %s not found." % oLicenseFile.sPath);
        aoLoadedLicenses = faoGetLicensesFromFile(sPath);
        if len(aoLoadedLicenses) == 0:
          oConsole.fOutput(
            COLOR_WARNING, CHAR_WARNING,
            COLOR_NORMAL, " There are ",
            COLOR_INFO, "no",
            COLOR_NORMAL, " licenses in the file ",
            COLOR_INFO, sPath,
            COLOR_NORMAL, ".",
          );
        else:
          oConsole.fOutput(
            COLOR_BUSY, CHAR_BUSY,
            COLOR_NORMAL, " Caching ",
            COLOR_INFO, str(len(aoLoadedLicenses)),
            COLOR_NORMAL, " licenses from file ",
            COLOR_INFO, sPath,
            COLOR_NORMAL, ":",
          );
          for oLicense in faoGetLicensesFromFile(sPath):
            oLicense.fWriteToRegistry();
            oConsole.fOutput(
              "  ",
              COLOR_ADD, CHAR_ADD,
              COLOR_NORMAL, " License ", COLOR_INFO, oLicense.sLicenseId,
              COLOR_NORMAL, " covering ", COLOR_INFO, oLicense.sUsageTypeDescription, 
              COLOR_NORMAL, " by ", COLOR_INFO, oLicense.sLicenseeName,
              COLOR_NORMAL, " of ", COLOR_INFO, oLicense.asProductNames[0],
              COLOR_NORMAL, " on ", COLOR_INFO, str(oLicense.uLicensedInstances),
              COLOR_NORMAL, " machine", "s" if oLicense.uLicensedInstances != 1 else "", ".",
            );
        sys.exit(guExitCodeSuccess);
      elif sLowerName == "arguments":
        if not s0Value:
          fExitWithBadArgumentValue(sLowerName, "You must provide a path to a file containing arguments as value for this argument.");
        # Read additional arguments from file and insert them after the current argument.
        oArgumentsFile = cFileSystemItem(s0Value);
        if not oArgumentsFile.fbIsFile():
          fExitWithBadArgumentValue(sLowerName, "File %s not found." % oArgumentsFile.sPath);
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