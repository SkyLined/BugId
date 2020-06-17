import json, os, sys;

class cProductDetails(object):
  def __init__(oSelf, sProductFolderPath):
    oSelf.sProductFolderPath = sProductFolderPath;
    # Load product details
    try:
      sProductDetailsFilePath = os.path.join(sProductFolderPath, "dxProductDetails.json");
      oProductDetailsFile = open(sProductDetailsFilePath, "rb");
      try:
        dxProductDetails = json.load(oProductDetailsFile);
      finally:
        oProductDetailsFile.close();
      oSelf.sProductName = dxProductDetails["sProductName"];
      oSelf.asDependentOnProductNames = dxProductDetails.get("asDependentOnProductNames", []);
    except:
      print "*" * 80;
      print "The file %s does not appear to contain valid product details!" % sProductDetailsFilePath;
      print "*" * 80;
      raise;

def foLoadModule(sProductName, oMainProductDetails):
  try:
    oProductModule = __import__(sProductName, globals(), locals(), [], -1);
  except ImportError as oError:
    print "*" * 80;
    if oError.message == "No module named %s" % sProductName:
      print "%s depends on %s which cannot be found on your system." % (oMainProductDetails.sProductName, sProductName);
      print "You can download the repository from GitHub at the following URL:";
      print "https://github.com/SkyLined/%s/" % sProductName
      print "After downloading, please save the code in one of these two folders:";
      print "    %s" % os.path.normpath(os.path.join(oMainProductDetails.sProductFolderPath, "modules", sProductName));
      print " - or -";
      print "    %s" % os.path.normpath(os.path.join(oMainProductDetails.sProductFolderPath, "..", sProductName));
      print "Once you have completed these steps, please try again.";
      print "*" * 80;
    else:
      print "*" * 80;
      print "%s depends on %s which cannot be loaded." % (oMainProductDetails.sProductName, sProductName);
      print "*" * 80;
    raise;
  return oProductModule;

class cDependencyChecker(object):
  def __init__(oSelf, sMainProductFolderPath):
    oSelf.sMainProductFolderPath = sMainProductFolderPath;
    oSelf.oBaseFolderPath = os.path.dirname(sMainProductFolderPath);
    
    oSelf.doProductDetails_by_sName = {};
    oSelf.oMainProductDetails = oSelf.foLoadProductDetailsForFolderPath(sMainProductFolderPath);
  
  def foLoadProductDetailsForFolderPath(oSelf, sProductFolderPath):
    oProductDetails = cProductDetails(sProductFolderPath);
    assert oProductDetails.sProductName not in oSelf.doProductDetails_by_sName, \
        "Cannot have a single product in two folders: %s found in %s and %s" % \
        (oProductDetails.sProductName, sProductFolderPath, 
        oSelf.doProductDetails_by_sName[oProductDetails.sProductName].sProductFolderPath);
    oSelf.doProductDetails_by_sName[oProductDetails.sProductName] = oProductDetails;
    return oProductDetails;
  
  def fCheck(oSelf):
    asLoadedProductNames = [oSelf.oMainProductDetails.sProductName];
    asCheckedProductNames = [];
    while len(asCheckedProductNames) < len(oSelf.doProductDetails_by_sName):
      for (sProductName, oProductDetails) in oSelf.doProductDetails_by_sName.items():
        if sProductName in asCheckedProductNames:
          continue;
        for sDepentOnProductName in oProductDetails.asDependentOnProductNames:
          if sDepentOnProductName in asLoadedProductNames:
            continue;
          oProductModule = foLoadModule(sDepentOnProductName, oSelf.oMainProductDetails);
          sProductFolderPath = os.path.dirname(oProductModule.__file__);
          # This dependency's module can be loaded; record this.
          asLoadedProductNames.append(sDepentOnProductName);
          # Make sure we check the dependencies of this module as well.
          oSelf.foLoadProductDetailsForFolderPath(sProductFolderPath);
        asCheckedProductNames.append(sProductName);

def fCheckDependencies():
  # This file is supposed to be store in the main product folder.
  # Our search path will be the main product folder first, its parent folder
  # second, the "modules" child folder of the main product folder third, and
  # whatever was already in the search path last.
  sMainProductFolderPath = os.path.normpath(os.path.dirname(__file__));
  sParentFolderPath = os.path.normpath(os.path.dirname(sMainProductFolderPath));
  sModulesFolderPath = os.path.join(sMainProductFolderPath, "modules");
  asOriginalSysPath = sys.path[:];
  sys.path = [sMainProductFolderPath, sParentFolderPath, sModulesFolderPath] + sys.path;
  cDependencyChecker(sMainProductFolderPath).fCheck();
  # Restore the original module search path
  sys.path = asOriginalSysPath;

