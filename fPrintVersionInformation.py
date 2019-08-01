import os, platform;
from faxListOutput import faxListOutput;
from mColors import *;
import mProductDetails;
from mWindowsAPI import fsGetPythonISA, oSystemInfo;
from oConsole import oConsole;

def fPrintProductDetails(oProductDetails, bIsMainProduct, bShowInstallationFolders):
  oConsole.fPrint(*(
    [
      u"\u2502 \u2219 ", (
        HILITE + UNDERLINE if bIsMainProduct else
        INFO if not oProductDetails.bRequiresLicense else
        HILITE if oProductDetails.oLicense else
        WARNING if (oProductDetails.bHasTrialPeriod and oProductDetails.bInTrialPeriod) else
        ERROR
      ),
      oProductDetails.sProductName, NORMAL, " version: ", INFO, str(oProductDetails.oProductVersion),
    ] + (
      bShowInstallationFolders and [
        NORMAL, " installed at ", INFO, oProductDetails.sInstallationFolderPath,
      ] or [ ]
    ) + (
      [] if (not oProductDetails.bRequiresLicense  or oProductDetails.oLicense) else
      [NORMAL, " ", WARNING, "(in trial period)"] if (oProductDetails.bHasTrialPeriod and oProductDetails.bInTrialPeriod) else
      [NORMAL, " ", ERROR, "(no valid license found)"]
    ) + [
      NORMAL, ".",
    ]
  ));
  if oProductDetails.oLatestProductVersion:
    if oProductDetails.bVersionIsPreRelease:
      oConsole.fPrint(
        u"\u2502     You are running a ", HILITE, "pre-release", NORMAL, " version:",
        " the latest released version is ", INFO, str(oProductDetails.oLatestProductVersion), NORMAL, ".",
      );
    elif not oProductDetails.bVersionIsUpToDate:
      oConsole.fPrint(
        u"\u2502     You are running an ", WARNING, "old", NORMAL, " version:",
        " the latest released version is ", HILITE, str(oProductDetails.oLatestProductVersion), NORMAL, ",",
        " available at ", HILITE, oProductDetails.oRepository.sLatestVersionURL, NORMAL, ".",
      );

def fPrintVersionInformation(bCheckForUpdates, bCheckAndShowLicenses, bShowInstallationFolders):
  # Read product details for rs and all modules it uses.
  aoProductDetails = mProductDetails.faoGetProductDetailsForAllLoadedModules();
  oMainProductDetails = mProductDetails.foGetProductDetailsForMainModule();
  if bCheckForUpdates:
    uCheckedProductCounter = 0;
    for oProductDetails in aoProductDetails:
      oConsole.fProgressBar(
        uCheckedProductCounter * 1.0 / len(aoProductDetails),
        "Checking %s for updates..." % oProductDetails.sProductName,
      );
      try:
        oProductDetails.oLatestProductDetailsFromRepository;
      except Exception as oException:
        oConsole.fPrint(
          ERROR, u"- Version check for ", ERROR_INFO, oProductDetails.sProductName,
          ERROR, " failed: ", ERROR_INFO, str(oException),
        );
      uCheckedProductCounter += 1;
  oConsole.fLock();
  try:
    if bCheckAndShowLicenses:
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

      oLicenseCheckServer = mProductDetails.cLicenseCheckServer(oMainProductDetails.sLicenseServerURL);
      uCheckedLicenseCounter = 0;
      for oLicense in aoLicenses:
        oConsole.fProgressBar(
          uCheckedLicenseCounter * 1.0 / len(aoLicenses),
          "Checking license %s with server..." % oLicense.sLicenseId,
        );
        sLicenseCheckServerError = oLicense.fsCheckWithServerAndGetError(oLicenseCheckServer, bForceCheck = True);
        if sLicenseCheckServerError:
          oConsole.fPrint(
            ERROR, u"- License check for ", ERROR_INFO, oLicense.sLicenseId,
            ERROR, " on server ", ERROR_INFO, oMainProductDetails.sLicenseServerURL,
            ERROR, " failed: ", ERROR_INFO, sLicenseCheckServerError,
          );
        uCheckedLicenseCounter += 1;
    
    oConsole.fPrint(
      u"\u250C\u2500 ", INFO, "Version information", NORMAL, " ", sPadding = u"\u2500"
    );
    # Output the main product information first, then its dependencies:
    fPrintProductDetails(oMainProductDetails, bIsMainProduct = True, bShowInstallationFolders = bShowInstallationFolders);
    for oProductDetails in aoProductDetails:
      if oProductDetails != oMainProductDetails:
        fPrintProductDetails(oProductDetails, bIsMainProduct = False, bShowInstallationFolders = bShowInstallationFolders);
    
    oConsole.fPrint(
      u"\u2502 \u2219 ", INFO, "Windows",
      NORMAL, " version: ", INFO, oSystemInfo.sOSName,
      NORMAL, " release ", INFO, oSystemInfo.sOSReleaseId,
      NORMAL, ", build ", INFO, oSystemInfo.sOSBuild,
      NORMAL, " ", INFO, oSystemInfo.sOSISA,
      NORMAL, ".",
    );
    oConsole.fPrint(
      u"\u2502 \u2219 ", INFO, "Python",
      NORMAL, " version: ", INFO, str(platform.python_version()),
      NORMAL, " ", INFO, fsGetPythonISA(),
      NORMAL, ".",
    );
    
    if bCheckAndShowLicenses:
      oConsole.fPrint(
        u"\u251C\u2500 ", INFO, "License information", NORMAL, " ", sPadding = u"\u2500",
      );
      if aoLicenses:
        oConsole.fPrint(
          NORMAL, u"\u2502 \u2219 This system is registered with id ", INFO, mProductDetails.fsGetSystemId(), NORMAL, " on the license server",
        );
      for oLicense in aoLicenses:
        oConsole.fPrint(
          u"\u2502 \u2219 License ", INFO, oLicense.sLicenseId,
          NORMAL, " for ", INFO, oLicense.asProductNames[0], 
          NORMAL, " covers ", INFO, oLicense.sUsageTypeDescription, 
          NORMAL, " by ", INFO, oLicense.sLicenseeName,
          NORMAL, " of the following products:",
        );
        oConsole.fPrint(u"\u2502     ", faxListOutput(oLicense.asProductNames, "and", INFO, NORMAL));
      if asProductNamesInTrial:
        oConsole.fPrint(*(
          [
            u"\u2502 \u2219 "
          ] + faxListOutput(asProductNamesInTrial, "and", WARNING_INFO, WARNING)  + [
            WARNING, " ", len(asProductNamesInTrial) == 1 and "is" or "are", " not covered by a valid, active license but ",
            len(asProductNamesInTrial) == 1 and "it is in its" or "they are in their", " trial period.",
          ]
        ));
      if asProductNamesWithoutLicenseRequirement:
        oConsole.fPrint(*(
          [
            u"\u2502 \u2219 "
          ] + faxListOutput(asProductNamesWithoutLicenseRequirement, "and", INFO, NORMAL)  + [
            NORMAL, " ", len(asProductNamesInTrial) == 1 and "does not require a license" or "do not require licenses", ".",
          ]
        ));
      if asUnlicensedProductNames:
        oConsole.fPrint(*(
          [
            u"\u2502 \u2219 "
          ] + faxListOutput(asUnlicensedProductNames, "and", ERROR_INFO, ERROR)  + [
            ERROR, " ", len(asUnlicensedProductNames) == 1 and "is" or "are", " not covered by a valid, active license and ",
            len(asUnlicensedProductNames) == 1 and "has exceeded its" or "have exceeded their", " trial period.",
          ]
        ));
    oConsole.fPrint(
      u"\u2514", sPadding = u"\u2500",
    );
    oConsole.fPrint();
  finally:
    oConsole.fUnlock();

  (asLicenseErrors, asLicenseWarnings) = mProductDetails.ftasGetLicenseErrorsAndWarnings();
  if asLicenseErrors:
    oConsole.fLock();
    try:
      oConsole.fPrint(ERROR, u"\u250C\u2500", ERROR_INFO, " Software license error ", ERROR, sPadding = u"\u2500");
      for sLicenseError in asLicenseErrors:
        oConsole.fPrint(ERROR, u"\u2502 ", ERROR_INFO, sLicenseError);
      oConsole.fPrint(ERROR, u"\u2514", sPadding = u"\u2500");
    finally:
      oConsole.fUnlock();
  if asLicenseWarnings:
    oConsole.fLock();
    try:
      oConsole.fPrint(WARNING, u"\u250C\u2500", WARNING_INFO, " Software license warning ", WARNING, sPadding = u"\u2500");
      for sLicenseWarning in asLicenseWarnings:
        oConsole.fPrint(WARNING, u"\u2502 ", WARNING_INFO, sLicenseWarning);
      oConsole.fPrint(WARNING, u"\u2514", sPadding = u"\u2500");
    finally:
      oConsole.fUnlock();
