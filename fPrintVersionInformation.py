import os, platform, sys;
from mColors import *;
import mProductDetails;
from mWindowsAPI import fsGetPythonISA, oSystemInfo;
from oConsole import oConsole;

def fPrintProductDetails(oProductDetails):
  oConsole.fPrint(
    u"\u2502 ", INFO, oProductDetails.sProductName,
    NORMAL, " version: ", INFO, str(oProductDetails.oProductVersion),
    NORMAL, ".",
  );
  if oProductDetails.oLatestProductVersion:
    if oProductDetails.bVersionIsPreRelease:
      oConsole.fPrint(
        u"\u2502  ", DIM, u"\u2514\u2500",
        NORMAL, " You are running a ", HILITE, "pre-release", NORMAL, " version:",
        " the latest release version is ", INFO, str(oProductDetails.oLatestProductVersion), NORMAL, ".",
      );
    elif not oProductDetails.bVersionIsUpToDate:
      oConsole.fPrint(
        u"\u2502  ", DIM, u"\u2514\u2500",
        NORMAL, "Version ", HILITE, str(oProductDetails.oLatestProductVersion), NORMAL,
        " is available at ", HILITE, oProductDetails.oRepository.sLatestVersionURL, NORMAL, ".",
      );

def fPrintVersionInformation(bCheckForUpdates = True):
  oBugIdProductDetails = mProductDetails.cProductDetails.foGetForProductName("BugId");
  aoAllLoadedProductDetails = oBugIdProductDetails.faoGetAllLoadedProductDetails();
  if bCheckForUpdates:
    uCheckedProductCounter = 0;
    for oProductDetails in aoAllLoadedProductDetails:
      oConsole.fProgressBar(
        uCheckedProductCounter * 1.0 / len(aoAllLoadedProductDetails),
        "Checking %s for updates..." % oProductDetails.sProductName,
      );
      try:
        oProductDetails.oLatestProductDetailsFromRepository;
      except Exception as oException:
        oConsole.fPrint(
          ERROR, u"Version check for ", ERROR_INFO, oProductDetails.sProductName,
          ERROR, " failed: ", ERROR_INFO, str(oException),
        );
      uCheckedProductCounter += 1;
  oConsole.fLock();
  try:
    oConsole.fPrint(
      u"\u250C\u2500", INFO, " Version information ",
      NORMAL, sPadding = u"\u2500"
    );
    # Output the BugId product information first, then its dependencies:
    fPrintProductDetails(oBugIdProductDetails);
    oConsole.fPrint(
      u"\u2502 ", INFO, "Windows",
      NORMAL, " version: ", INFO, oSystemInfo.sOSName,
      NORMAL, " release ", INFO, oSystemInfo.sOSReleaseId,
      NORMAL, ", build ", INFO, oSystemInfo.sOSBuild,
      NORMAL, " ", INFO, oSystemInfo.sOSISA,
      NORMAL, ".",
    );
    oConsole.fPrint(
      u"\u2502 ", INFO, "Python",
      NORMAL, " version: ", INFO, str(platform.python_version()),
      NORMAL, " ", INFO, fsGetPythonISA(),
      NORMAL, ".",
    );
    for oProductDetails in aoAllLoadedProductDetails:
      if oProductDetails != oBugIdProductDetails:
        fPrintProductDetails(oProductDetails);
    oConsole.fPrint(
      u"\u2514", sPadding = u"\u2500",
    );
    oConsole.fPrint();
  finally:
    oConsole.fUnlock();
