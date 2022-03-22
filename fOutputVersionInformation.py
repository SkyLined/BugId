import os, platform;

import mProductDetails;
from mWindowsAPI import fsGetPythonISA, oSystemInfo;
from mConsole import oConsole;

from faxListOutput import faxListOutput;
from mColorsAndChars import *;

try:
  from fOutputLogo import fOutputLogo as f0OutputLogo;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'fOutputLogo'":
    raise;
  f0OutputLogo = None;

def fOutputProductDetails(oProductDetails, bIsMainProduct, bShowInstallationFolders, bCheckForUpdates, bCheckForUpdatesSuccessful):
  oConsole.fOutput(*(
    [
      "│ ", (
        [COLOR_WARNING, CHAR_WARNING] if (
          (
            bCheckForUpdates and (
              not bCheckForUpdatesSuccessful or
              (not oProductDetails.bVersionIsUpToDate and not oProductDetails.bVersionIsPreRelease)
            )
          ) or (
            oProductDetails.bHasTrialPeriod and oProductDetails.bInTrialPeriod
          )
        ) else
        [COLOR_NORMAL, CHAR_LIST] if bCheckForUpdates and bCheckForUpdatesSuccessful and oProductDetails.bVersionIsPreRelease else
        [COLOR_OK, CHAR_OK] if oProductDetails.o0License or not oProductDetails.bRequiresLicense else
        [COLOR_ERROR, CHAR_ERROR]
      ), " ", (
        COLOR_INFO if (not oProductDetails.bRequiresLicense or oProductDetails.o0License) else
        COLOR_WARNING if (oProductDetails.bHasTrialPeriod and oProductDetails.bInTrialPeriod) else
        COLOR_ERROR
      ) + (CONSOLE_UNDERLINE if oProductDetails.o0License else 0),
      oProductDetails.sProductName, COLOR_NORMAL, " version: ", (
        COLOR_WARNING if (
          bCheckForUpdates and (
            not bCheckForUpdatesSuccessful or
            (not oProductDetails.bVersionIsUpToDate and not oProductDetails.bVersionIsPreRelease)
          )
        ) else
        COLOR_HILITE
      ), str(oProductDetails.oProductVersion),
    ] + (
      bShowInstallationFolders and [
        COLOR_NORMAL, " installed at ", COLOR_HILITE, oProductDetails.s0InstallationFolderPath,
      ] or [ ]
    ) + (
      [] if (not oProductDetails.bRequiresLicense or oProductDetails.o0License) else
      [COLOR_NORMAL, " ", COLOR_WARNING, "(in trial period)"] if (oProductDetails.bHasTrialPeriod and oProductDetails.bInTrialPeriod) else
      [COLOR_NORMAL, " ", COLOR_ERROR, "(no valid license found)"]
    ) + (
      [] if not bCheckForUpdates else
      [COLOR_NORMAL, " ", COLOR_WARNING, "(no respository)"] if oProductDetails.o0Repository is None else
      [COLOR_NORMAL, " ", COLOR_ERROR, "(cannot check for updates)"] if not bCheckForUpdatesSuccessful else
      [COLOR_NORMAL, " ", COLOR_INFO, "(pre-release, last release version is ", str(oProductDetails.oLatestProductVersion), ")"]
         if oProductDetails.bVersionIsPreRelease else
      [COLOR_NORMAL, " ", COLOR_WARNING, "(old, latest release version is ", str(oProductDetails.oLatestProductVersion), ")"]
         if not oProductDetails.bVersionIsUpToDate else
      []
    ) + [
      COLOR_NORMAL, ".",
    ]
  ));

def fOutputVersionInformation(bCheckForUpdates, bShowInstallationFolders, dsAdditionalVersion_by_sName = {}):
  # Read product details for rs and all modules it uses.
  aoProductDetails = mProductDetails.faoGetProductDetailsForAllLoadedModules();
  o0MainProductDetails = mProductDetails.fo0GetProductDetailsForMainModule();
  oConsole.fLock();
  try:
    aoProductDetailsCheckedForUpdates = [];
    aoProductDetailsSuccessfullyCheckedForUpdates = [];
    if bCheckForUpdates:
      for oProductDetails in aoProductDetails:
        if oProductDetails.o0Repository is None:
          continue;
        aoProductDetailsCheckedForUpdates.append(oProductDetails);
        oConsole.fProgressBar(
          len(aoProductDetailsCheckedForUpdates) * 1.0 / len(aoProductDetails),
          "Checking %s for updates..." % oProductDetails.sProductName,
        );
        try:
          oProductDetails.foGetLatestProductDetailsFromRepository();
        except mProductDetails.mExceptions.cProductDetailsException as oException:
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " Version check for ",
            COLOR_INFO, oProductDetails.sProductName,
            COLOR_NORMAL, " failed: ",
            COLOR_INFO, str(oException),
          );
        else:
          aoProductDetailsSuccessfullyCheckedForUpdates.append(oProductDetails);
      if len(aoProductDetailsSuccessfullyCheckedForUpdates) == 0:
          oConsole.fOutput(
            COLOR_WARNING, CHAR_WARNING,
            COLOR_NORMAL, "Failed to get any product version information.",
          );
          oConsole.fOutput(
            "  (This often indicates you are running a ",
            COLOR_INFO, "pre-release",
            COLOR_NORMAL, " version, or a version that is very ",
            COLOR_INFO, "out of date",
            COLOR_NORMAL, ").",
          );
          oConsole.fOutput(
            "  To try and resolve this issue, please update this product to the latest",
          );
          oConsole.fOutput(
            "  version and try again.",
          );
    
    if f0OutputLogo:
      f0OutputLogo();
    
    oConsole.fOutput(
      "┌───[", COLOR_HILITE, " Version information ", COLOR_NORMAL, "]", sPadding = "─",
    );
    # Output the main product information first, then its dependencies alphabetically:
    if o0MainProductDetails:
      fOutputProductDetails(
        o0MainProductDetails,
        bIsMainProduct = True,
        bShowInstallationFolders = bShowInstallationFolders,
        bCheckForUpdates = bCheckForUpdates,
        bCheckForUpdatesSuccessful = o0MainProductDetails in aoProductDetailsSuccessfullyCheckedForUpdates,
      );
    doRemainingProductDetails_by_sName = dict([
      (oProductDetails.sProductName, oProductDetails)
      for oProductDetails in aoProductDetails
      if oProductDetails != o0MainProductDetails
    ]);
    for sProductName in sorted(doRemainingProductDetails_by_sName.keys()):
      oProductDetails = doRemainingProductDetails_by_sName[sProductName];
      fOutputProductDetails(
        oProductDetails,
        bIsMainProduct = False,
        bShowInstallationFolders = bShowInstallationFolders,
        bCheckForUpdates = bCheckForUpdates,
        bCheckForUpdatesSuccessful = oProductDetails in aoProductDetailsSuccessfullyCheckedForUpdates,
      );
    asProductNames = (
      ([o0MainProductDetails.sProductName] if o0MainProductDetails else [])
      + list(doRemainingProductDetails_by_sName.keys())
    );
    
    oConsole.fOutput(
      "│ ", CHAR_LIST, " ", COLOR_INFO, "Windows",
      COLOR_NORMAL, " version: ", COLOR_INFO, oSystemInfo.sOSName,
      COLOR_NORMAL, " release ", COLOR_INFO, oSystemInfo.sOSReleaseId,
      COLOR_NORMAL, ", build ", COLOR_INFO, oSystemInfo.sOSBuild,
      COLOR_NORMAL, " ", COLOR_INFO, oSystemInfo.sOSISA,
      COLOR_NORMAL, ".",
    );
    oConsole.fOutput(
      "│ ", CHAR_LIST, " ", COLOR_INFO, "Python",
      COLOR_NORMAL, " version: ", COLOR_INFO, str(platform.python_version()),
      COLOR_NORMAL, " ", COLOR_INFO, fsGetPythonISA(),
      COLOR_NORMAL, ".",
    );
    
    for (sName, sVersion) in dsAdditionalVersion_by_sName.items():
      oConsole.fOutput(
        "│ ", CHAR_LIST, " ", COLOR_INFO, sName,
        COLOR_NORMAL, " version: ", COLOR_INFO, sVersion,
        COLOR_NORMAL, ".",
      );
    
    oConsole.fOutput(
      "└", sPadding = "─",
    );
  finally:
    oConsole.fUnlock();
  
