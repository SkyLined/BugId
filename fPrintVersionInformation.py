import os, platform;
from mColors import *;
import mProductDetails;
from mWindowsAPI import fsGetPythonISA, oSystemInfo;
from oConsole import oConsole;


def fPrintProductDetails(oProductDetails, bIsMainProduct):
  oConsole.fPrint(
    u"\u2502 \u2219 ", bIsMainProduct and HILITE or INFO, oProductDetails.sProductName,
    NORMAL, " version: ", INFO, str(oProductDetails.oProductVersion),
    NORMAL, ".",
  );
  if oProductDetails.oLatestProductVersion:
    if oProductDetails.bVersionIsPreRelease:
      oConsole.fPrint(
        u"\u2502   You are running a ", HILITE, "pre-release", NORMAL, " version",
        " (the latest released version is ", INFO, str(oProductDetails.oLatestProductVersion), NORMAL, ").",
      );
    elif not oProductDetails.bVersionIsUpToDate:
      oConsole.fPrint(
        u"\u2502   You are running an ", WARNING, "old", NORMAL, " version",
        " (the latest released version is  ", HILITE, str(oProductDetails.oLatestProductVersion), NORMAL, ",",
        " available at ", HILITE, oProductDetails.oRepository.sLatestVersionURL, NORMAL, ").",
      );

def fPrintVersionInformation(bCheckForUpdates = True):
  # Read product details for rs and all modules it uses.
  aoProductDetails = mProductDetails.faoGetProductDetailsForAllLoadedModules();
  oMainProductDetails = mProductDetails.foGetProductDetailsForMainModule();
  if bCheckForUpdates:
    bEverythingUpToDate = True;
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
      else:
        bEverythingUpToDate &= oProductDetails.bVersionIsUpToDate; 
      uCheckedProductCounter += 1;
  oConsole.fLock();
  try:
    oConsole.fPrint(
      u"\u250C\u2500", INFO, " Version information ",
      NORMAL, sPadding = u"\u2500"
    );
    # Output the BugId product information first, then its dependencies:
    fPrintProductDetails(oMainProductDetails, True);
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
    for oProductDetails in aoProductDetails:
      if oProductDetails != oMainProductDetails:
        fPrintProductDetails(oProductDetails, False);

    if bCheckForUpdates and bEverythingUpToDate:
      oConsole.fPrint(
        u"\u2502 All modules are up-to-date.",
      );
    oConsole.fPrint(
      u"\u2514", sPadding = u"\u2500",
    );
    oConsole.fPrint();
  finally:
    oConsole.fUnlock();
