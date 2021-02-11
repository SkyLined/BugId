def fTestDependencies():
  import json, os, sys;
  # Save the list of names of default loaded modules:
  asInitiallyLoadedModuleNames = sys.modules.keys();
  
  # Augment the search path to make the test subject a package and have access to its modules folder.
  sTestsFolderPath = os.path.dirname(os.path.abspath(__file__));
  sMainFolderPath = os.path.dirname(sTestsFolderPath);
  sParentFolderPath = os.path.dirname(sMainFolderPath);
  sModulesFolderPath = os.path.join(sMainFolderPath, "modules");
  asOriginalSysPath = sys.path[:];
  # Load product details
  oProductDetailsFile = open(os.path.join(sMainFolderPath, "dxProductDetails.json"), "rb");
  try:
    dxProductDetails = json.load(oProductDetailsFile);
  finally:
    oProductDetailsFile.close();
  # Load list of dependencies on python internal modules:
  sInternalPythonModuleDepenciesListFilePath = os.path.join(sTestsFolderPath, "internal-python-module-dependencies.txt");
  if os.path.isfile(sInternalPythonModuleDepenciesListFilePath):
    oInternalPythonModuleDepenciesListFile = open(sInternalPythonModuleDepenciesListFilePath, "rb");
    try:
      sInternalPythonModuleDepenciesList = oInternalPythonModuleDepenciesListFile.read();
    finally:
      oInternalPythonModuleDepenciesListFile.close();
    asExpectedDependencyPythonInternalModuleBaseNames = [s.rstrip("\r") for s in sInternalPythonModuleDepenciesList.split("\n") if s.rstrip("\r")];
  else:
    asExpectedDependencyPythonInternalModuleBaseNames = [];
  
  # Find out the type of product and load modules/application modules:
  for sProductType in dxProductDetails["asProductTypes"]:
    if sProductType == "Python module":
      # This product offers a Python module; it should be loaded from the parent folder.
      sys.path = [sParentFolderPath] + asOriginalSysPath;
      __import__(dxProductDetails["sPythonModuleName"], globals(), locals(), [], -1);
    elif sProductType == "Python application":
      # This product offers a a Python application and/or module; it should be loaded from the main folder, with the
      # parent folder in the path too.
      sys.path = [sMainFolderPath, sParentFolderPath] + asOriginalSysPath;
      for sPythonApplicationName in dxProductDetails["asPythonApplicationNames"]:
        __import__(sPythonApplicationName, globals(), locals(), [], -1);
    elif sProductType in ["JavaScript module", "PHP module"]:
      pass;
    else:
      raise AssertionError("Unknown \"asProductTypes\" value %s!" % repr(sProductType));
  
  # Determine which Python internal modules were unexpectedly loaded as dependencies:
  asLoadedPythonInteralModuleBaseNames = [
    sModuleName
    for (sModuleName, o0Module) in sys.modules.items()
    if (
      "." not in sModuleName # Ignore sub-modules
      and not sModuleName.startswith("_") # ignore "private/internal" modules
      and sModuleName not in asInitiallyLoadedModuleNames
      and not (o0Module and hasattr(o0Module, "__file__") and o0Module.__file__.startswith(sParentFolderPath))
    )
  ];
  asUnexpectedDependencyPythonInteralModuleBaseNames = [
    sModuleName
    for sModuleName in asLoadedPythonInteralModuleBaseNames
    if sModuleName not in asExpectedDependencyPythonInternalModuleBaseNames
  ];
  # Determine which Python internal modules were reported as dependencies but not loaded
  asSuperflousDependencyPythonInternalModuleBaseNames = [
    sModuleName
    for sModuleName in asExpectedDependencyPythonInternalModuleBaseNames
    if sModuleName not in asLoadedPythonInteralModuleBaseNames
  ];
  if asUnexpectedDependencyPythonInteralModuleBaseNames:
    print "The product has unreported Python internal module dependencies! (marked with '+')";
  if asSuperflousDependencyPythonInternalModuleBaseNames:
    print "The product has superfluous Python internal module dependencies! (marked with '-')";
  if asUnexpectedDependencyPythonInteralModuleBaseNames or asSuperflousDependencyPythonInternalModuleBaseNames:
    for sModuleName in sorted(asLoadedPythonInteralModuleBaseNames + asSuperflousDependencyPythonInternalModuleBaseNames):
      print "%s %s" % (
        "+" if sModuleName in asUnexpectedDependencyPythonInteralModuleBaseNames
            else "-" if sModuleName in asSuperflousDependencyPythonInternalModuleBaseNames
            else " ",
            sModuleName
      );
    raise AssertionError("Incorrect dependencies on Python internal modules found!");
  
  # Determine which product modules were unexpectedly loaded as dependencies:
  dsLoadedDependencyModules_by_sName = {};
  for (sModuleName, o0Module) in sys.modules.items():
    if "." not in sModuleName and o0Module and hasattr(o0Module, "__file__") and o0Module.__file__:
      sSourceFilePath = o0Module.__file__;
      try:
        bSourceIsUnderParentFolder = not os.path.relpath(sSourceFilePath, sParentFolderPath).startswith("..");
        bSourceIsUnderMainFolder = not os.path.relpath(sSourceFilePath, sMainFolderPath).startswith("..");
        bSourceIsUnderModulesFolder = not os.path.relpath(sSourceFilePath, sModulesFolderPath).startswith("..");
      except ValueError:
        continue; # Not a dependency but a Python internal module
      if not bSourceIsUnderParentFolder:
        continue; # Not a dependency but a Python internal module
      if bSourceIsUnderMainFolder and not bSourceIsUnderModulesFolder:
        continue; # Not a dependency but part of the product
      dsLoadedDependencyModules_by_sName[sModuleName] = o0Module;
  
  asExpectedDependencyModulesNames = dxProductDetails.get("asDependentOnProductNames", []) + dxProductDetails.get("asOptionalProductNames", []);
  asUnexpectedDependencyModuleNames = [
    sModuleName
    for sModuleName in dsLoadedDependencyModules_by_sName.keys()
    if sModuleName not in asExpectedDependencyModulesNames
  ];
  asSuperfluousDependencyModuleNames = [
    sModuleName
    for sModuleName in dxProductDetails.get("asDependentOnProductNames", [])
    if sModuleName not in dsLoadedDependencyModules_by_sName
  ];
  if asUnexpectedDependencyModuleNames:
    print "The product has unreported dependencies! (marked with '+')";
  if asSuperfluousDependencyModuleNames:
    print "The product has superfluous dependencies! (marked with '-')";
  if asUnexpectedDependencyModuleNames or asSuperfluousDependencyModuleNames:
    for sModuleName in sorted(dsLoadedDependencyModules_by_sName.keys() + asSuperfluousDependencyModuleNames):
      print "%s %s%s" % (
        "+" if sModuleName in asUnexpectedDependencyModuleNames
            else "-" if sModuleName in asSuperfluousDependencyModuleNames
            else " ",
        sModuleName,
        " (%s)" % (dsLoadedDependencyModules_by_sName[sModuleName].__file__,) if sModuleName in dsLoadedDependencyModules_by_sName else "",
      );
  
  if asUnexpectedDependencyPythonInteralModuleBaseNames or asSuperflousDependencyPythonInternalModuleBaseNames \
      or asUnexpectedDependencyModuleNames or asSuperfluousDependencyModuleNames:
    for sModuleName in sorted(sys.modules.keys()):
      if "." in sModuleName:
        continue;
      o0Module = sys.modules[sModuleName];
      if not o0Module or not hasattr(o0Module, "__file__") or not o0Module.__file__:
        sOrigin = "INTERNAL";
        sSourceFilePath = "<none>";
      else:
        sSourceFilePath = o0Module.__file__;
        try:
          bSourceIsUnderParentFolder = not os.path.relpath(sSourceFilePath, sParentFolderPath).startswith("..");
          bSourceIsUnderMainFolder = not os.path.relpath(sSourceFilePath, sMainFolderPath).startswith("..");
          bSourceIsUnderModulesFolder = not os.path.relpath(sSourceFilePath, sModulesFolderPath).startswith("..");
          sOrigin = (
            "PRODUCT" if bSourceIsUnderMainFolder and not bSourceIsUnderModulesFolder else
            "DEPENDENCY" if bSourceIsUnderParentFolder else
            "PYTHON"
          );
        except ValueError:
          sOrigin = "PYTHON";
      print "%-30s => %s %s" % (sModuleName, sOrigin, sSourceFilePath);
    raise AssertionError("Incorrect dependencies found!");
