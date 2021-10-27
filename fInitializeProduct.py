def fInitializeProduct():
  import json, os, sys;
  
  try:
    from mExitCodes import guExitCodeInternalError, guExitCodeBadDependencyError;
  except: # If mExitCodes does not exist, use default values:
    guExitCodeInternalError = 1;
    guExitCodeBadDependencyError = 3;
  
  import __main__;
  bProductIsAnApplication = hasattr(__main__, "__file__") and os.path.dirname(__main__.__file__) == os.path.dirname(__file__);
  
  bDebugOutput = "--debug-product-initialization" in sys.argv[1:];
  auCurrentLineLength = [0];
  if bDebugOutput:
    def fDebugStatus(sMessage):
      print("\r%s" % sMessage.ljust(auCurrentLineLength[0]), sep = "", end = "\n");
      auCurrentLineLength[0] = len(sMessage);
    def fDebugOutput(sMessage):
      print("\r%s" % sMessage.ljust(auCurrentLineLength[0]), sep = "");
      auCurrentLineLength[0] = 0;
  
  def fo0LoadModule(sProductName, sModuleName, bOptional = False):
    if sModuleName in sys.modules:
      return sys.modules[sModuleName];
    if bDebugOutput: fDebugStatus("\xB7 Loading module %s for %s..." % (sModuleName, sProductName));
    try:
      oModule = __import__(sModuleName, dict(globals()), {}, [], 0);
    except Exception as oException:
      bModuleNotFound = isinstance(oException, ModuleNotFoundError) and oException.args[0] == "No module named '%s'" % sModuleName;
      if bDebugOutput:
        if bModuleNotFound:
          fDebugOutput("- %s %s is not available." % ("Optional module" if bOptional else "Module", sModuleName));
        else:
          fDebugOutput("- %s %s cannot be loaded: %s(%s)." % \
              ("Optional module" if bOptional else "Module", sModuleName, oException.__class__.__name__, repr(oException.args)[1:-1]));
      if bOptional:
        return None;
      if bProductIsAnApplication:
        print("*" * 80);
        if bModuleNotFound:
          print("%s depends on %s which is not available." % (sProductName, sModuleName));
        else:
          print("%s depends on %s which cannot be loaded because of an error:" % (sProductName, sModuleName));
          print("%s: %s" % (oException.__class__.__name__, oException));
        print("*" * 80);
      # Dump exception stack like Python would
      import traceback;
      traceback.print_exc();
      # Terminate with the appropriate exit code from mExitCodes (use standard values if it cannot be loaded).
      sys.exit(guExitCodeBadDependencyError if bModuleNotFound else guExitCodeInternalError);
    if bDebugOutput: fDebugOutput("+ Module %s loaded (%s)." % (sModuleName, os.path.dirname(oModule.__file__)));
    return oModule;
  
  # This is supposed to be the __init__.py file in the module folder.
  sProductFolderPath = os.path.normpath(os.path.dirname(__file__));
  asPotentialModuleParentPaths = [];
  if bProductIsAnApplication:
    # Applications can be stand-alone, where all dependcy modules are in a `modules` sub-folder of the product folder:
    asPotentialModuleParentPaths.append(os.path.join(sProductFolderPath, "modules"));
  # Applications can use shared modules, where dependencies' folders are children of the application's parent
  # folder. Non-application modules' dependencies are always children of the module's parent folder.
  # Therefore we always add the product's parent folder to the modules search path.
  asPotentialModuleParentPaths.append(os.path.dirname(sProductFolderPath));
  asOriginalSysPath = sys.path[:];
  # Our search path will be the main product folder first, its parent folder
  # second, the "modules" child folder of the main product folder third, and
  # whatever was already in the search path last.
  sys.path = asPotentialModuleParentPaths + [sPath for sPath in sys.path if sPath not in asPotentialModuleParentPaths];
  if bDebugOutput:
    fDebugOutput("* Module search path:");
    for sPath in sys.path:
      fDebugOutput("  %s" % sPath);
  # Load the dxProductDetails.json file and extract dependencies:
  sProductDetailsFilePath = os.path.join(sProductFolderPath, "dxProductDetails.json");
  if bDebugOutput: fDebugStatus("\xB7 Loading product details (%s)..." % sProductDetailsFilePath);
  try:
    with open(sProductDetailsFilePath, "rb") as oProductDetailsFile:
      dxProductDetails = json.load(oProductDetailsFile);
  except Exception as oException:
    if bDebugOutput: fDebugOutput("- Product details cannot be loaded from %s: %s(%s)" % \
          (sProductDetailsFilePath, oException.__class__.__name__, repr(oException.args)[1:-1]));
    raise;
  if bDebugOutput: fDebugOutput("+ Product details for %s loaded (%s)" % (
    "%(sProductName)s by %(sProductAuthor)s" % dxProductDetails, 
    sProductDetailsFilePath,
  ));
  for sModuleName in dxProductDetails.get("a0sDependentOnProductNames", []):
    fo0LoadModule(dxProductDetails["sProductName"], sModuleName, bOptional = False);
  for sModuleName in (
    dxProductDetails.get("a0sDebugAdditionalProductNames", []) +
    dxProductDetails.get("a0sReleaseAdditionalProductNames", [])
  ):
    fo0LoadModule(dxProductDetails["sProductName"], sModuleName, bOptional = True);
  if bDebugOutput: fDebugOutput("+ Product %s initialized." % dxProductDetails["sProductName"]);
  # Restore the original module search path
  sys.path = asOriginalSysPath;
  # Remove the debug flag from the arguments if it was provided.
  # We only do this in the main product initializer, otherwise
  # it might be removed by one module initializer before another
  # module is loaded, causing the later module not to display debug
  # output even though it was requested. Once this code is executed
  # in the main product, all modules should have been loaded.
  if bDebugOutput and bProductIsAnApplication:
    sys.argv = sys.argv[:1] + [s for s in sys.argv[1:] if s != "--debug-product-initialization"];
  