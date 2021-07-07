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

def fPrintProductDetails(oProductDetails, bIsMainProduct, bShowInstallationFolders, bCheckForUpdates, bCheckForUpdatesSuccessful):
  oConsole.fOutput(*(
    [
      "\u2502 ", (
        [WARNING, WARNING_CHAR] if (
          (
            bCheckForUpdates and (
              not bCheckForUpdatesSuccessful or
              (not oProductDetails.bVersionIsUpToDate and not oProductDetails.bVersionIsPreRelease)
            )
          ) or (
            oProductDetails.bHasTrialPeriod and oProductDetails.bInTrialPeriod
          )
        ) else
        [INFO, BULLET_CHAR] if bCheckForUpdates and bCheckForUpdatesSuccessful and oProductDetails.bVersionIsPreRelease else
        [OK, OK_CHAR] if oProductDetails.oLicense or not oProductDetails.bRequiresLicense else
        [ERROR, ERROR_CHAR]
      ), " ", (
        INFO if (not oProductDetails.bRequiresLicense or oProductDetails.oLicense) else
        WARNING if (oProductDetails.bHasTrialPeriod and oProductDetails.bInTrialPeriod) else
        ERROR
      ) + (UNDERLINE if oProductDetails.oLicense else 0),
      oProductDetails.sProductName, NORMAL, " version: ", (
        WARNING if (
          bCheckForUpdates and (
            not bCheckForUpdatesSuccessful or
            (not oProductDetails.bVersionIsUpToDate and not oProductDetails.bVersionIsPreRelease)
          )
        ) else
        HILITE
      ), str(oProductDetails.oProductVersion),
    ] + (
      bShowInstallationFolders and [
        NORMAL, " installed at ", HILITE, oProductDetails.s0InstallationFolderPath,
      ] or [ ]
    ) + (
      [] if (not oProductDetails.bRequiresLicense or oProductDetails.oLicense) else
      [NORMAL, " ", WARNING, "(in trial period)"] if (oProductDetails.bHasTrialPeriod and oProductDetails.bInTrialPeriod) else
      [NORMAL, " ", ERROR, "(no valid license found)"]
    ) + (
      [] if not bCheckForUpdates else
      [NORMAL, " ", WARNING, "(no respository)"] if oProductDetails.o0Repository is None else
      [NORMAL, " ", ERROR, "(cannot check for updates)"] if not bCheckForUpdatesSuccessful else
      [NORMAL, " ", INFO, "(pre-release, last release version is ", str(oProductDetails.oLatestProductVersion), ")"]
         if oProductDetails.bVersionIsPreRelease else
      [NORMAL, " ", WARNING, "(old, latest release version is ", str(oProductDetails.oLatestProductVersion), ")"]
         if not oProductDetails.bVersionIsUpToDate else
      []
    ) + [
      NORMAL, ".",
    ]
  ));

def fPrintVersionInformation(bCheckForUpdates, bShowInstallationFolders):
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
            ERROR, ERROR_CHAR, " Version check for ", ERROR_INFO, oProductDetails.sProductName,
            ERROR, " failed: ", ERROR_INFO, str(oException),
          );
        else:
          aoProductDetailsSuccessfullyCheckedForUpdates.append(oProductDetails);
      if len(aoProductDetailsSuccessfullyCheckedForUpdates) == 0:
          oConsole.fOutput(
            WARNING, WARNING_CHAR, " ", WARNING_INFO, "All checks failed.",
            WARNING, " This often indicates you are running a ",
            WARNING_INFO, "pre-release", WARNING, " version, or a version that is very ",
            WARNING_INFO, "out of date", WARNING, ".",
          );
          oConsole.fOutput(
            WARNING, "  If you do not have a pre-release version of ", o0MainProductDetails.sProductName, ", ",
            WARNING_INFO, "please try to update to the latest version before trying again.",
          );
    
    if f0PrintLogo:
      f0PrintLogo();
    
    oConsole.fOutput(
      "\u250C\u2500 ", HILITE, "Version information", NORMAL, " ", sPadding = "\u2500"
    );
    # Output the main product information first, then its dependencies alphabetically:
    if o0MainProductDetails:
      fPrintProductDetails(
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
      fPrintProductDetails(
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
      "\u2502 ", BULLET_CHAR, " ", INFO, "Windows",
      NORMAL, " version: ", INFO, oSystemInfo.sOSName,
      NORMAL, " release ", INFO, oSystemInfo.sOSReleaseId,
      NORMAL, ", build ", INFO, oSystemInfo.sOSBuild,
      NORMAL, " ", INFO, oSystemInfo.sOSISA,
      NORMAL, ".",
    );
    oConsole.fOutput(
      "\u2502 ", BULLET_CHAR, " ", INFO, "Python",
      NORMAL, " version: ", INFO, str(platform.python_version()),
      NORMAL, " ", INFO, fsGetPythonISA(),
      NORMAL, ".",
    );
    
    oConsole.fOutput(
      "\u2514", sPadding = "\u2500",
    );
  finally:
    oConsole.fUnlock();
  
