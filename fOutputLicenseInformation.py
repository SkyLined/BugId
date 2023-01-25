import mProductDetails;

from faxListOutput import faxListOutput;
from foConsoleLoader import foConsoleLoader;
from mColorsAndChars import \
  CHAR_ERROR, \
  CHAR_OK, \
  CHAR_WARNING, \
  COLOR_ERROR, \
  COLOR_HILITE, \
  COLOR_INFO, \
  COLOR_NORMAL, \
  COLOR_OK, \
  COLOR_WARNING;
oConsole = foConsoleLoader();

try:
  from fOutputLogo import fOutputLogo as f0OutputLogo;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'fOutputLogo'":
    raise;
  f0OutputLogo = None;

CHAR_LIST = "\u2022";

def fOutputLicenseInformation(bUpdateIfNeeded = False):
  # Read product details for rs and all modules it uses.
  aoProductDetails = mProductDetails.faoGetProductDetailsForAllLoadedModules();
  o0MainProductDetails = mProductDetails.fo0GetProductDetailsForMainModule();
  oConsole.fLock();
  try:
    aoLicenses = [];
    asProductNamesWithoutLicenseRequirement = [];
    asLicensedProductNames = [];
    asProductNamesInTrial = [];
    asUnlicensedProductNames = [];
    for oProductDetails in aoProductDetails:
      if not oProductDetails.bRequiresLicense:
        asProductNamesWithoutLicenseRequirement.append(oProductDetails.sProductName);
      elif oProductDetails.o0License:
        if oProductDetails.o0License not in aoLicenses:
          aoLicenses.append(oProductDetails.o0License);
        asLicensedProductNames.append(oProductDetails.sProductName);
      elif oProductDetails.bHasTrialPeriod and oProductDetails.bInTrialPeriod:
        asProductNamesInTrial.append(oProductDetails.sProductName);
      else:
        asUnlicensedProductNames.append(oProductDetails.sProductName);
    
    if o0MainProductDetails and o0MainProductDetails.sb0LicenseServerURL is not None:
      oLicenseServer = mProductDetails.cLicenseServer(o0MainProductDetails.sb0LicenseServerURL);
      uCheckedLicenseCounter = 0;
      aoUpdatedLicenses = [];
      for oLicense in aoLicenses:
        oConsole.fProgressBar(
          uCheckedLicenseCounter * 1.0 / len(aoLicenses),
          "Checking license %s with server..." % oLicense.sLicenseId,
        );
        sLicenseServerError = oLicense.fsCheckWithServerAndGetError(oLicenseServer, bForceCheck = True);
        sServerURL = str(o0MainProductDetails.sb0LicenseServerURL, "ascii", "strict");
        if sLicenseServerError:
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " License check for ",
            COLOR_INFO, oLicense.sLicenseId,
            COLOR_NORMAL, " on server ",
            COLOR_INFO, sServerURL,
            COLOR_NORMAL, " failed:",
          );
          oConsole.fOutput(
            "  ",
            COLOR_INFO, sLicenseServerError,
          );
        uCheckedLicenseCounter += 1;
        if oLicense.bMayNeedToBeUpdated and bUpdateIfNeeded:
          oConsole.fProgressBar(
            uCheckedLicenseCounter * 1.0 / len(aoLicenses),
            "Downloading updated license %s from server..." % oLicense.sLicenseId,
          );
          oUpdatedLicense = oLicenseServer.foDownloadUpdatedLicense(oLicense);
          oConsole.fOutput(
            COLOR_OK, CHAR_OK, COLOR_NORMAL, " Downloaded updated license ",
            COLOR_INFO, oLicense.sLicenseId, COLOR_NORMAL, " from server ",
            COLOR_INFO, str(oLicenseServer.sbServerURL, "ascii", "strict"),
            COLOR_NORMAL, ".",
          );
          aoUpdatedLicenses.append(oUpdatedLicense);
      if len(aoUpdatedLicenses) > 0:
        for oProductDetails in aoProductDetails:
          if oProductDetails.sb0LicenseServerURL is None:
            continue; # No need for a license == do not store license
          aoUpdatedLicensesForThisProduct = [
            oUpdatedLicense
            for oUpdatedLicense in aoUpdatedLicenses
            if oProductDetails.sProductName in oUpdatedLicense.asProductNames
          ];
          mProductDetails.fWriteLicensesToProductFolder(aoUpdatedLicensesForThisProduct, oProductDetails);
          oConsole.fOutput(
            COLOR_OK, CHAR_OK,
            COLOR_NORMAL, " Saved ",
            COLOR_INFO, str(len(aoUpdatedLicensesForThisProduct)),
            COLOR_NORMAL, " updated license", "" if len(aoUpdatedLicensesForThisProduct) == 1 else "s", " for product ",
            COLOR_INFO, oProductDetails.sProductName,
            COLOR_NORMAL, " in folder ",
            COLOR_INFO, oProductDetails.sInstallationFolderPath,
            COLOR_NORMAL, ".",
          );
    
    if f0OutputLogo:
      f0OutputLogo();
    
    oConsole.fOutput(
      "┌───[", COLOR_HILITE, " License information ", COLOR_NORMAL, "]", sPadding = "─",
    );
    if aoLicenses:
      oConsole.fOutput(
        "│ ",
        COLOR_OK, CHAR_OK,
        COLOR_NORMAL, " This system uses system id ",
        COLOR_INFO, mProductDetails.fsGetSystemId(),
        COLOR_NORMAL, " with the license server.",
      );
      oConsole.fOutput(
        "├", sPadding = "─",
      );
    for oLicense in aoLicenses:
      oConsole.fOutput(
        "│ ",
        COLOR_OK, CHAR_OK,
        COLOR_NORMAL, " License ",
        COLOR_INFO, oLicense.sLicenseId,
        COLOR_NORMAL, " covers ",
        COLOR_INFO, oLicense.sUsageTypeDescription, 
        COLOR_NORMAL, " by ",
        COLOR_INFO, oLicense.sLicenseeName,
        COLOR_NORMAL, " of ",
        COLOR_INFO, oLicense.asProductNames[0],
        COLOR_NORMAL, " on ",
        COLOR_INFO, str(oLicense.uLicensedInstances),
        COLOR_NORMAL, " machine", "s" if oLicense.uLicensedInstances != 1 else "", ".",
      );
      oConsole.fOutput(
        "│   Covered products: ",
        faxListOutput(oLicense.asProductNames, "and", oLicense.asProductNames, COLOR_INFO, COLOR_NORMAL, COLOR_NORMAL),
        COLOR_NORMAL, ".",
      );
      oConsole.fOutput(
        "│   License source: ",
        COLOR_INFO, oLicense.sLicenseSource,
        COLOR_NORMAL, ".",
      );
    if asProductNamesInTrial:
      oConsole.fOutput(
        "│ ",
        COLOR_WARNING, CHAR_WARNING,
        COLOR_NORMAL, " A ",
        COLOR_INFO, "trial period",
        COLOR_NORMAL, " is active for the following product", "s" if len(asProductNamesInTrial) > 1 else "", ":",
      );
      oConsole.fOutput(
        "│   ",
        faxListOutput(asProductNamesInTrial, "and", asProductNamesInTrial, COLOR_INFO, COLOR_NORMAL, COLOR_NORMAL),
        COLOR_NORMAL, ".",
      );
    if asProductNamesWithoutLicenseRequirement:
      oConsole.fOutput(
        "│ ",
        COLOR_OK, CHAR_OK, " ",
        COLOR_INFO, "No license",
        COLOR_NORMAL, " is required to use the following product", "s" if len(asProductNamesWithoutLicenseRequirement) > 1 else "", ":",
      );
      oConsole.fOutput(
        "│   ",
        faxListOutput(asProductNamesWithoutLicenseRequirement, "and", [], COLOR_INFO, COLOR_NORMAL, COLOR_NORMAL),
        COLOR_NORMAL, ".",
      );
    if asUnlicensedProductNames:
      oConsole.fOutput(
        "│ ",
        COLOR_ERROR, CHAR_ERROR,
        COLOR_NORMAL, " ",
        COLOR_INFO, "No valid license",
        COLOR_NORMAL, " was found and ",
        COLOR_INFO, "the trial period has been exceeded",
        COLOR_NORMAL, " for the following product", "s" if len(asUnlicensedProductNames) > 1 else "", ":",
      );
      oConsole.fOutput(
        "│   ",
        faxListOutput(asUnlicensedProductNames, "and", asUnlicensedProductNames, COLOR_INFO, COLOR_NORMAL, COLOR_NORMAL),
        COLOR_NORMAL, ".",
      );
    
    (asLicenseErrors, asLicenseWarnings) = mProductDetails.ftasGetLicenseErrorsAndWarnings();
    if asLicenseErrors:
      oConsole.fOutput("├───[", COLOR_ERROR, " Software license error ", COLOR_NORMAL, "]", sPadding = "─");
      for sLicenseError in asLicenseErrors:
        oConsole.fOutput("│ ", COLOR_ERROR, CHAR_ERROR, COLOR_INFO, " ", sLicenseError);
    if asLicenseWarnings:
      oConsole.fOutput("├───[", COLOR_WARNING, " Software license warning ", COLOR_NORMAL, "]", sPadding = "─");
      for sLicenseWarning in asLicenseWarnings:
        oConsole.fOutput("│ ", COLOR_WARNING, CHAR_WARNING, COLOR_INFO, " ", sLicenseWarning);
    oConsole.fOutput("└", sPadding = "─");
  finally:
    oConsole.fUnlock();
