def fInitializeProduct():
  import __main__, json, os, sys;
  try:
    from mStandardExitCodes import \
        guExitCodeBadDependencyError, \
        guExitCodeInternalError;
  except ImportError:
    raise AssertionError("Your application does not have a mStandardExitCodes module with standard error codes defined");

  bProductIsAnApplication = hasattr(__main__, "__file__") and os.path.dirname(__main__.__file__) == os.path.dirname(__file__);
  bDebugOutput = "@debug-product-initialization" in sys.argv[1:]; # This flag will be remove from the arguments at the end of this code.
  sProductFolderPath = os.path.normpath(os.path.dirname(__file__));

  if bProductIsAnApplication:
    # If this is not an application, the modules search path has already been set.
    # But if it is, we want to search the application's parent path for modules in the same
    # parent folder as the application (e.g. development mode) as well as modules in the "modules"
    # sub-folder (i.e. release mode).
    asOriginalSysPath = sys.path[:];
    asModulesPaths = [
      os.path.dirname(sProductFolderPath),
      sProductFolderPath,
      os.path.join(sProductFolderPath, "modules"),
    ]
    sys.path = asModulesPaths + [sPath for sPath in sys.path if sPath not in asModulesPaths];
  if bDebugOutput:
    if bProductIsAnApplication:
      print(" Module search paths:");
      for sPath in sys.path:
        print("  * %s." % sPath);

  def fo0LoadModule(sProductName, sModuleName, bOptional = False):
    if sModuleName in sys.modules:
      return sys.modules[sModuleName];
    if bDebugOutput: print("* Loading module %s for %s..." % (
      sModuleName,
      sProductName,
    ));
    try:
      oModule = __import__(sModuleName, dict(globals()), {}, [], 0);
    except Exception as oException:
      bModuleNotFound = isinstance(oException, ModuleNotFoundError) and oException.args[0] == "No module named '%s'" % sModuleName;
      if bProductIsAnApplication or bDebugOutput:
        if bModuleNotFound:
          print("- Optional module %s is not available!" % sModuleName);
        else:
          print("- Optional module %s can not be loaded!" % sModuleName);
          print(
            "  Exception: %s -> %s" % (
            oException.__class__.__name__,
            str(oException),
          ));
      if bOptional:
        return None;
      # Dump exception stack like Python would
      import traceback;
      asExceptionReportLines = traceback.format_exc().split("\n");
      for sLine in asExceptionReportLines:
        print(sLine.rstrip("\r"));
      # Terminate with the appropriate exit code from mExitCodes (use standard values if it cannot be loaded).
      sys.exit(guExitCodeBadDependencyError if bModuleNotFound else guExitCodeInternalError);
    if bDebugOutput: print(" Module %s loaded from %s." % (sModuleName, os.path.dirname(oModule.__file__)));
    return oModule;
  
  # Load the dxProductDetails.json file and extract dependencies:
  sProductDetailsFilePath = os.path.join(sProductFolderPath, "dxProductDetails.json");
  if bDebugOutput: print("* Loading product details file %s..." % (sProductDetailsFilePath,));
  try:
    with open(sProductDetailsFilePath, "rb") as oProductDetailsFile:
      dxProductDetails = json.load(oProductDetailsFile);
  except Exception as oException:
    if bDebugOutput: print("- Product details cannot be loaded from %s!" % (sProductDetailsFilePath,));
    raise;
  if bDebugOutput: print("+ Product details for %s by %s loaded from %s." % (
    dxProductDetails["sProductName"],
    dxProductDetails["sProductAuthor"],
    sProductDetailsFilePath,
  ));
  for sModuleName in dxProductDetails.get("a0sDependentOnProductNames", []):
    fo0LoadModule(dxProductDetails["sProductName"], sModuleName, bOptional = False);
  for sModuleName in (
    dxProductDetails.get("a0sDebugAdditionalProductNames", []) +
    dxProductDetails.get("a0sReleaseAdditionalProductNames", [])
  ):
    fo0LoadModule(dxProductDetails["sProductName"], sModuleName, bOptional = True);
  if bDebugOutput: print("+ Product %s by %s initialized." % (
    dxProductDetails["sProductName"],
    dxProductDetails["sProductAuthor"],
  ));
  # Restore the original module search path
  if bProductIsAnApplication:
    sys.path = asOriginalSysPath;
  # Remove the debug flag from the arguments if it was provided.
  # We only do this in the main product initializer, otherwise
  # it might be removed by one module initializer before another
  # module is loaded, causing the later module not to display debug
  # output even though it was requested. Once this code is executed
  # in the main product, all modules should have been loaded.
  if bDebugOutput and bProductIsAnApplication:
    sys.argv.remove("@debug-product-initialization");
  