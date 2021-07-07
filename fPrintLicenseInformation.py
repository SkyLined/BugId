import os, platform;

import mProductDetails;
from mWindowsAPI import fsGetPythonISA, oSystemInfo;
from mConsole import oConsole;

from faxListOutput import faxListOutput;
from mColors import *;

try:
  from fPrintLogo import fPrintLogo as f0PrintLogo;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'fPrintLogo'":
    raise;
  f0PrintLogo = None;

OK_CHAR = "\u221A";
WARNING_CHAR = "\u25B2";
ERROR_CHAR = "\xd7";
BULLET_CHAR = "\u2022";

def fPrintLicenseInformation(bUpdateIfNeeded = False):
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
      elif oProductDetails.oLicense:
        if oProductDetails.oLicense not in aoLicenses:
          aoLicenses.append(oProductDetails.oLicense);
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
            ERROR, ERROR_CHAR, " License check for ", ERROR_INFO, oLicense.sLicenseId,
            ERROR, " on server ", ERROR_INFO, sServerURL,
            ERROR, " failed: ", ERROR_INFO, sLicenseServerError,
          );
        uCheckedLicenseCounter += 1;
        if oLicense.bMayNeedToBeUpdated and bUpdateIfNeeded:
          oConsole.fProgressBar(
            uCheckedLicenseCounter * 1.0 / len(aoLicenses),
            "Downloading updated license %s from server..." % oLicense.sLicenseId,
          );
          oUpdatedLicense = oLicenseServer.foDownloadUpdatedLicense(oLicense);
          oConsole.fOutput(
            OK, OK_CHAR, NORMAL, " Downloaded updated license ",
            INFO, oLicense.sLicenseId, NORMAL, " from server ",
            INFO, str(oLicenseServer.sbServerURL, "ascii", "strict"),
            NORMAL, ".",
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
            OK, OK_CHAR, NORMAL, " Saved ",
            INFO, str(len(aoUpdatedLicensesForThisProduct)), NORMAL, " updated license", "" if len(aoUpdatedLicensesForThisProduct) == 1 else "s",
            " for product ", INFO, oProductDetails.sProductName, NORMAL, " in folder ",
            INFO, oProductDetails.sInstallationFolderPath, NORMAL, ".",
          );
    
    if f0PrintLogo:
      f0PrintLogo();
    
    oConsole.fOutput(
      "\u250C\u2500 ", HILITE, "License information", NORMAL, " ", sPadding = "\u2500",
      );
    if aoLicenses:
      oConsole.fOutput(
        NORMAL, "\u2502 ", OK, OK_CHAR, NORMAL, " This system will use id ", INFO, mProductDetails.fsGetSystemId(), NORMAL, " with the license server.",
      );
      oConsole.fOutput(
        "\u250C", sPadding = "\u2500",
      );
    for oLicense in aoLicenses:
      oConsole.fOutput(
        "\u2502 ", OK, OK_CHAR, NORMAL, " License ", INFO, oLicense.sLicenseId,
        NORMAL, " covers ", INFO, oLicense.sUsageTypeDescription, 
        NORMAL, " by ", INFO, oLicense.sLicenseeName,
        NORMAL, " of ", INFO, oLicense.asProductNames[0],
        NORMAL, " on ", INFO, str(oLicense.uLicensedInstances), NORMAL, "machine", "s" if oLicense.uLicensedInstances != 1 else "",
        NORMAL, ".",
      );
      oConsole.fOutput("\u2502   Covered products: ", faxListOutput(oLicense.asProductNames, "and", oLicense.asProductNames, INFO, NORMAL, NORMAL), NORMAL, ".");
      oConsole.fOutput("\u2502   License source:", INFO, oLicense.sLicenseSource, NORMAL, ".");
    if asProductNamesInTrial:
      oConsole.fOutput(
        "\u2502 ", WARNING, WARNING_CHAR, " A ",
        WARNING_INFO, "trial period",
        WARNING, " is active for the following product", "s" if len(asProductNamesInTrial) > 1 else "", ":",
      );
      oConsole.fOutput("\u2502   ", faxListOutput(asProductNamesInTrial, "and", asProductNamesInTrial, WARNING_INFO, WARNING, NORMAL));
    if asProductNamesWithoutLicenseRequirement:
      oConsole.fOutput(
        "\u2502 ", OK_CHAR, " ",
        INFO, "No license",
        NORMAL, " is required to use the following product", "s" if len(asProductNamesWithoutLicenseRequirement) > 1 else "", ":",
      );
      oConsole.fOutput("\u2502   ", faxListOutput(asProductNamesWithoutLicenseRequirement, "and", [], INFO, NORMAL, NORMAL));
    if asUnlicensedProductNames:
      oConsole.fOutput(
        "\u2502 ", ERROR, ERROR_CHAR, " ",
        ERROR_INFO, "No valid license",
        ERROR, " was found and ",
        ERROR_INFO, "the trial period has been exceeded",
        ERROR, " for the following product", "s" if len(asUnlicensedProductNames) > 1 else "", ":",
      );
      oConsole.fOutput("\u2502   ", faxListOutput(asUnlicensedProductNames, "and", asUnlicensedProductNames, ERROR_INFO, ERROR, ERROR));
    
    (asLicenseErrors, asLicenseWarnings) = mProductDetails.ftasGetLicenseErrorsAndWarnings();
    if asLicenseErrors:
      oConsole.fOutput(ERROR, "\u251C\u2500", ERROR_INFO, " Software license error ", ERROR, sPadding = "\u2500");
      for sLicenseError in asLicenseErrors:
        oConsole.fOutput(ERROR, "\u2502 ", ERROR, ERROR_CHAR, " ", ERROR_INFO, sLicenseError);
    if asLicenseWarnings:
      oConsole.fOutput(WARNING, "\u251C\u2500", WARNING_INFO, " Software license warning ", WARNING, sPadding = "\u2500");
      for sLicenseWarning in asLicenseWarnings:
        oConsole.fOutput(WARNING, "\u2502 ", WARNING, WARNING_CHAR, " ", WARNING_INFO, sLicenseWarning);
    oConsole.fOutput(
      "\u2514", sPadding = "\u2500",
    );
  finally:
    oConsole.fUnlock();
