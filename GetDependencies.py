import io, json, os, re, sys, urllib2, zipfile;

rIgnoredProductFilesPattern = re.compile(r"^(Tests(\..*)?|lgtm\.yml|modules|releases|Internal error reports)($|\\)|(^|\\)[\.#].*");

if __name__ == "__main__":
  sMainFolder = os.path.dirname(__file__);
  sModulesFolder = os.path.join(sMainFolder, "modules");
  if not os.path.isdir(sModulesFolder):
    print "* Creating 'modules' folders...";
    os.mkdir(sModulesFolder);
  
  asAvailableProductNames = [];
  asQueuedProductDetailsJSONFilePaths = [os.path.join(sMainFolder, "dxProductDetails.json")];
  
  while asQueuedProductDetailsJSONFilePaths:
    sQueuedProductDetailsJSONFilePath = asQueuedProductDetailsJSONFilePaths.pop(0);
    print "* Reading '%s' file..." % (sQueuedProductDetailsJSONFilePath,);
    oProductDetailsFile = open(sQueuedProductDetailsJSONFilePath, "rb");
    try:
      dxProductDetails = json.load(oProductDetailsFile);
    finally:
      oProductDetailsFile.close();
    # Since we now know the product name, add it to the list of products we know to be available.
    asAvailableProductNames.append(dxProductDetails["sProductName"]);
    # Go through the list of dependencies:
    for sProductName in dxProductDetails["asDependentOnProductNames"]:
      if sProductName in asAvailableProductNames:
        continue; # We already have this product.
      # Download the product source as a zip file from GitHub:
      sProductZipURL = "https://github.com/SkyLined/%s/archive/master.zip" % (sProductName,);
      print "* Downloading '%s' from '%s'..." % (sProductName, sProductZipURL);
      oResponse = urllib2.urlopen(sProductZipURL);
      try:
        if oResponse.getcode() != 200:
          print "- Unexpected response code while attempting to download %s:" % (sProductName,);
          print "  Expected 200, got %03d." % oResponse.getcode();
          sys.exit(1);
        if oResponse.geturl() != sProductZipURL:
          print "  * Redirected to: %s" % (oResponse.geturl(),);
        sProductZip = oResponse.read();
      finally:
        oResponse.close();
      # Open the zip file.
      oProductZipFileStream = io.BytesIO(sProductZip);
      oProductZipFile = zipfile.ZipFile(oProductZipFileStream, "r");
      sProductsFileAndFoldersHeader = "%s-master%s" % (sProductName, os.sep); # Really, why!?
      sProductModuleFolderPath = os.path.join("modules", sProductName);
      # Create the module folder.
      if not os.path.isdir(sProductModuleFolderPath):
        print "* Creating '%s' folder..." % (sProductModuleFolderPath,);
        os.mkdir(sProductModuleFolderPath);
      # Go through the list of source files in the zip
      for oZipInfo in oProductZipFile.infolist():
        sProductFileOrFolderInZipName = oZipInfo.filename;
        # Get the desired local path of the file from the name in the zip file:
        sProductFileOrFolderPathWithHeader = oZipInfo.filename.replace(os.altsep, os.sep);
        if not sProductFileOrFolderPathWithHeader.startswith(sProductsFileAndFoldersHeader):
          print "- %s path does not start with %s:" % \
              ("Folder" if sProductFileOrFolderPathWithHeader.endswith(os.sep) else "File", sProductsFileAndFoldersHeader);
          print "  Path: '%s'." % (sProductFileOrFolderPathWithHeader,);
          sys.exit(1);
        sProductFileOrFolderPath = sProductFileOrFolderPathWithHeader[len(sProductsFileAndFoldersHeader):];
        # We ignore certain files (.git, tests, the products' own dependencies folder, etc.)
        if rIgnoredProductFilesPattern.match(sProductFileOrFolderPath):
          continue;
        # Check if it is a folder or file path
        if sProductFileOrFolderPath == "" or sProductFileOrFolderPath.endswith(os.sep):
          # Check if this folder exists and create it if it does not:
          sProductFolderInModulesFolderPath = os.path.join(sProductModuleFolderPath, sProductFileOrFolderPath);
          if not os.path.exists(sProductFolderInModulesFolderPath):
            print "* Creating '%s' folder..." % (sProductFolderInModulesFolderPath,);
            os.mkdir(sProductFolderInModulesFolderPath);
        else:
          # Extract the file:
          sProductFileInModulesFolderPath = os.path.join(sProductModuleFolderPath, sProductFileOrFolderPath);
          print "* Extracting '%s'..." % (sProductFileInModulesFolderPath,);
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
          # If this is a dxProductDetails.json file in the root folder of the product, add it to the
          # queue for processing, so that we also download the dependencies for all dependencies.
          if sProductFileOrFolderPath.lower() == "dxProductDetails.json".lower():
            asQueuedProductDetailsJSONFilePaths.append(sProductFileInModulesFolderPath);
