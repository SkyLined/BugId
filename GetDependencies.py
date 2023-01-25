assert __name__ == "__main__", \
    "This is a Python script, not a loadable module.";

import io, json, os, re, sys, urllib.request, zipfile;

sMainFolder = os.path.dirname(__file__);
sModulesFolder = os.path.join(sMainFolder, "modules");
sys.path += [sMainFolder, sModulesFolder];
  
from foConsoleLoader import foConsoleLoader;
from mColorsAndChars import \
  CHAR_BUSY, \
  CHAR_ERROR, \
  CHAR_LIST, \
  CHAR_OK, \
  CHAR_WARNING, \
  COLOR_BUSY, \
  COLOR_ERROR, \
  COLOR_HILITE, \
  COLOR_LIST, \
  COLOR_NORMAL, \
  COLOR_OK, \
  COLOR_WARNING, \
  CONSOLE_UNDERLINE;
oConsole = foConsoleLoader();
from mExitCodes import \
    guExitCodeInternalError;

rIgnoredProductFilesPattern = re.compile(r"^(Tests(\..*)?|lgtm\.yml|modules|releases|Internal error reports)($|\\)|(^|\\)[\.#].*");
if not os.path.isdir(sModulesFolder):
  oConsole.fStatus(
    COLOR_BUSY, CHAR_BUSY,
    COLOR_NORMAL, " Creating ",
    COLOR_HILITE, "modules",
    COLOR_NORMAL, " folder...",
  );
  os.mkdir(sModulesFolder);
  oConsole.fOutput(
    COLOR_OK, CHAR_OK,
    COLOR_NORMAL, " Created ",
    COLOR_HILITE, "modules",
    COLOR_NORMAL, " folder..",
  );
  
asAvailableProductNames = [];
asQueuedProductDetailsJSONFilePaths = [os.path.join(sMainFolder, "dxProductDetails.json")];

while asQueuedProductDetailsJSONFilePaths:
  sQueuedProductDetailsJSONFilePath = asQueuedProductDetailsJSONFilePaths.pop(0);
  oConsole.fStatus(
    COLOR_BUSY, CHAR_BUSY,
    COLOR_NORMAL, " Reading ",
    COLOR_HILITE, sQueuedProductDetailsJSONFilePath,
    COLOR_NORMAL, " file...",
  );
  oProductDetailsFile = open(sQueuedProductDetailsJSONFilePath, "rb");
  try:
    dxProductDetails = json.load(oProductDetailsFile);
  finally:
    oProductDetailsFile.close();
  oConsole.fStatus(
    COLOR_OK, CHAR_OK,
    COLOR_NORMAL, " Read ",
    COLOR_HILITE, sQueuedProductDetailsJSONFilePath,
    COLOR_NORMAL, " file.",
  );
  # Since we now know the product name, add it to the list of products we know to be available.
  asAvailableProductNames.append(dxProductDetails["sProductName"]);
  # Go through the list of dependencies:
  for sProductName in dxProductDetails.get("a0sDependentOnProductNames", []):
    if sProductName in asAvailableProductNames:
      continue; # We already have this product.
    # Download the product source as a zip file from GitHub:
    sProductZipURL = "https://github.com/SkyLined/%s/archive/master.zip" % (sProductName,);
    oConsole.fStatus(
      COLOR_BUSY, CHAR_BUSY,
      COLOR_NORMAL, " Downloading ",
      COLOR_HILITE, sProductName,
      COLOR_NORMAL, " from ",
      COLOR_HILITE + CONSOLE_UNDERLINE, sProductZipURL, 
      COLOR_NORMAL, "...",
    );
    oResponse = urllib.request.urlopen(sProductZipURL);
# In the Python 2 version of this code, I would detect a failure to secure the connection
# and explain that this may be caused by outdated root certificates on the local machine.
# I cannot update that code to Python 3 because I do not know how to detected it; I do
# not know how to trigger it in order to determine this either. Should I at some point
# find out; here's the message I used to show in this situation:
#          print "  You may need to update your root certificates!";
#          print "  This can be done from an elevated command-prompt with the following commands:";
#          print "  ";
#          print "  > CERTUTIL.EXE -f -generateSSTFromWU \"%TEMP%\\roots.sst\"";
#          print "  > POWERSHELL.EXE Get-ChildItem -Path \"%TEMP%\\roots.sst\" ^| ";
#          print "         Import-Certificate -CertStoreLocation Cert:\\LocalMachine\\Root";
    try:
      if oResponse.getcode() != 200:
        oConsole.fOutput(
          COLOR_ERROR, CHAR_ERROR,
          COLOR_NORMAL, " Cannot download ",
          COLOR_HILITE, sProductName,
          COLOR_NORMAL, " from ",
          COLOR_HILITE, sProductZipURL,
          COLOR_NORMAL, "!",
        );
        oConsole.fOutput(
          COLOR_NORMAL, "  Expected HTTP 200 response, got ",
          COLOR_HILITE, "HTTP %03d" % oResponse.getcode(),
          COLOR_NORMAL, ".",
        );
        sys.exit(guExitCodeInternalError);
      if oResponse.geturl() != sProductZipURL:
        oConsole.fOutput(
          COLOR_WARNING, CHAR_WARNING,
          COLOR_NORMAL, " Redirected to ",
          COLOR_HILITE, oResponse.geturl(),
          COLOR_NORMAL, ".",
        );
      sProductZip = oResponse.read();
    finally:
      oResponse.close();
    oConsole.fStatus(
      COLOR_OK, CHAR_OK,
      COLOR_NORMAL, " Downloaded ",
      COLOR_HILITE, sProductName,
      COLOR_NORMAL, " from ",
      COLOR_HILITE, sProductZipURL,
      COLOR_NORMAL, ".",
    );
    # Open the zip file.
    oConsole.fStatus(
      COLOR_BUSY, CHAR_BUSY,
      COLOR_NORMAL, " Creating ",
      COLOR_HILITE, sProductName,
      COLOR_NORMAL, "...",
    );
    oProductZipFileStream = io.BytesIO(sProductZip);
    oProductZipFile = zipfile.ZipFile(oProductZipFileStream, "r");
    asProductsFileAndFoldersHeaders = [
      "%s-main%s" % (sProductName, os.sep),
      "%s-master%s" % (sProductName, os.sep),
    ]; # Really, why!?
    sProductModuleFolderPath = os.path.join("modules", sProductName);
    # Create the module folder.
    if not os.path.isdir(sProductModuleFolderPath):
      oConsole.fStatus(
        COLOR_NORMAL, "  ",
        COLOR_BUSY, CHAR_BUSY,
        COLOR_NORMAL, " Creating ",
        COLOR_HILITE, sProductModuleFolderPath,
        COLOR_NORMAL, " folder...",
      );
      os.mkdir(sProductModuleFolderPath);
      oConsole.fOutput(
        COLOR_NORMAL, "  ",
        COLOR_LIST, CHAR_LIST,
        COLOR_NORMAL, " Created ",
        COLOR_HILITE, sProductModuleFolderPath,
        COLOR_NORMAL, " folder.",
      );
    # Go through the list of source files in the zip
    for oZipInfo in oProductZipFile.infolist():
      sProductFileOrFolderInZipName = oZipInfo.filename;
      # Get the desired local path of the file from the name in the zip file:
      sProductFileOrFolderPathWithHeader = oZipInfo.filename.replace(os.altsep, os.sep);
      sProductFileOrFolderPathWithHeader = oZipInfo.filename.replace(os.altsep, os.sep);
      for sProductsFileAndFoldersHeader in asProductsFileAndFoldersHeaders:
        if sProductFileOrFolderPathWithHeader.startswith(sProductsFileAndFoldersHeader):
          break;
      else:
        oConsole.fOutput(
          COLOR_NORMAL, "  ",
          COLOR_ERROR, CHAR_ERROR,
          COLOR_NORMAL, " ", "Folder" if sProductFileOrFolderPathWithHeader.endswith(os.sep) else "File", " ",
          COLOR_HILITE, sProductFileOrFolderPathWithHeader,
          COLOR_NORMAL, " does not start with a known header.",
        );
        sys.exit(guExitCodeInternalError);
      sProductFileOrFolderPath = sProductFileOrFolderPathWithHeader[len(sProductsFileAndFoldersHeader):];
      # We ignore certain files (.git, tests, the products' own dependencies folder, etc.)
      if rIgnoredProductFilesPattern.match(sProductFileOrFolderPath):
        continue;
      # Check if it is a folder or file path
      if sProductFileOrFolderPath == "" or sProductFileOrFolderPath.endswith(os.sep):
        # Check if this folder exists and create it if it does not:
        sProductFolderInModulesFolderPath = os.path.join(sProductModuleFolderPath, sProductFileOrFolderPath);
        if not os.path.exists(sProductFolderInModulesFolderPath):
          oConsole.fStatus(
            COLOR_NORMAL, "  ",
            COLOR_BUSY, CHAR_BUSY,
            COLOR_NORMAL, " Creating ",
            COLOR_HILITE, sProductFolderInModulesFolderPath,
            COLOR_NORMAL, " folder...",
          );
          os.mkdir(sProductFolderInModulesFolderPath);
          oConsole.fOutput(
            COLOR_NORMAL, "  ",
            COLOR_LIST, CHAR_LIST,
            COLOR_NORMAL, " Created ",
            COLOR_HILITE, sProductFolderInModulesFolderPath,
            COLOR_NORMAL, " folder.",
          );
      else:
        # Extract the file:
        sProductFileInModulesFolderPath = os.path.join(sProductModuleFolderPath, sProductFileOrFolderPath);
        oConsole.fStatus(
          COLOR_NORMAL, "  ",
          COLOR_BUSY, CHAR_BUSY,
          COLOR_NORMAL, " Extracting ",
          COLOR_HILITE, sProductFileInModulesFolderPath,
          COLOR_NORMAL, "...",
        );
        oZipFile = oProductZipFile.open(oZipInfo, "r");
        try:
          sProductFile = oZipFile.read();
        finally:
          oZipFile.close();
        oProductFileInModulesFolder = open(sProductFileInModulesFolderPath, "wb");
        try:
          oProductFileInModulesFolder.write(sProductFile);
        finally:
          oProductFileInModulesFolder.close();
        oConsole.fOutput(
          COLOR_NORMAL, "  ",
          COLOR_LIST, CHAR_LIST,
          COLOR_NORMAL, " Extracted ",
          COLOR_HILITE, sProductFileInModulesFolderPath,
          COLOR_NORMAL, ".",
        );
        # If this is a dxProductDetails.json file in the root folder of the product, add it to the
        # queue for processing, so that we also download the dependencies for all dependencies.
        if sProductFileOrFolderPath.lower() == "dxProductDetails.json".lower():
          asQueuedProductDetailsJSONFilePaths.append(sProductFileInModulesFolderPath);
    oConsole.fOutput(
      COLOR_OK, CHAR_OK,
      COLOR_NORMAL, " Created ",
      COLOR_HILITE, sProductName,
      COLOR_NORMAL, ".",
    );
