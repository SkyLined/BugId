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
  sys.path = [sMainFolderPath, sParentFolderPath, sModulesFolderPath] + asOriginalSysPath;
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
  # Load list of dependencies on python internal modules:
  sMainPythonModulesListFilePath = os.path.join(sTestsFolderPath, "main-python-modules.txt");
  assert os.path.isfile(sMainPythonModulesListFilePath), \
      "main-python-modules.txt is missing!";
  oMainPythonModulesListFile = open(sMainPythonModulesListFilePath, "rb");
  try:
    sMainPythonModulesList = oMainPythonModulesListFile.read();
  finally:
    oMainPythonModulesListFile.close();
  asMainPythonModuleNames = [s.rstrip("\r") for s in sMainPythonModulesList.split("\n") if s.rstrip("\r")];
  assert asMainPythonModuleNames, \
      "main-python-modules.txt is empty!";
  
  # Load the main modules, which should load all their dependencies:
  for sMainPythonModuleName in asMainPythonModuleNames:
    __import__(sMainPythonModuleName, globals(), locals(), [], -1);
  
  
  # Determine which Python internal modules were unexpectedly loaded as dependencies:
  asLoadedPythonInteralModuleBaseNames = [
    sModuleName
    for (sModuleName, o0Module) in sys.modules.items()
    if (
      "." not in sModuleName # Ignore sub-modules
      and sModuleName not in asInitiallyLoadedModuleNames
      and not (o0Module and hasattr(o0Module, "__file__") and o0Module.__file__.startswith(sParentFolderPath))
    )
  ];
  asUnexpectedDependencyPythonInteralModuleBaseNames = [
    sModuleName
    for sModuleName in asLoadedPythonInteralModuleBaseNames
    if (
      not sModuleName.startswith("_") # ignore "private/internal" modules
      and sModuleName not in asExpectedDependencyPythonInternalModuleBaseNames
    )
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
  dsLoadedDependencyModules_by_sName = dict([
    (sModuleName, o0Module)
    for (sModuleName, o0Module) in sys.modules.items()
    if (
      "." not in sModuleName # Ignore sub-modules
      and o0Module and hasattr(o0Module, "__file__") # Must have a path
      and o0Module.__file__.startswith(sParentFolderPath) # Must not be an internal module
      and not (
        o0Module.__file__.startswith(sMainFolderPath) # ignore modules in product folder
        and not o0Module.__file__.startswith(sModulesFolderPath) # except if in "/modules/" folder (which contains dependencies)
      )
    )
  ]);
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
      if "." not in sModuleName:
        o0Module = sys.modules[sModuleName];
        s0SourceFilePath = o0Module and getattr(o0Module, "__file__");
        sOrigin = (
          "PYTHON" if (
            s0SourceFilePath is None
            or not s0SourceFilePath.startswith(sParentFolderPath)
          ) else
          "DEPENDENCY" if not (
            s0SourceFilePath.startswith(sMainFolderPath)
            and not s0SourceFilePath.startswith(sModulesFolderPath)
          ) else 
          "PRODUCT"
        );
        print "%-30s => %s %s" % (sModuleName, sOrigin, sFile);
    raise AssertionError("Incorrect dependencies found!");
