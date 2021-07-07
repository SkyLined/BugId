import sys;

gbDebugOutput = False;

def fTestDependencies():
  import json, os, sys;
  # Save the list of names of default loaded modules:
  asInitiallyLoadedModuleNames = list(sys.modules.keys());
  
  # Augment the search path to make the test subject a package and have access to its modules folder.
  sTestsFolderPath = os.path.dirname(os.path.abspath(__file__));
  sMainFolderPath = os.path.dirname(sTestsFolderPath);
  sParentFolderPath = os.path.dirname(sMainFolderPath);
  sModulesFolderPath = os.path.join(sMainFolderPath, "modules");
  asOriginalSysPath = sys.path[:];
  # Load mDebugOutput if available to improve error output
  sys.path = [sParentFolderPath] + asOriginalSysPath;
  try:
    import mDebugOutput as m0DebugOutput;
  except ModuleNotFoundError as oException:
    if oException.args[0] != "No module named 'mDebugOutput'":
      raise;
    m0DebugOutput = None;
  
  try:
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
      asExpectedDependencyPythonInternalModuleBaseNames = [str(s.rstrip(b"\r"), "utf-8") for s in sInternalPythonModuleDepenciesList.split(b"\n") if s.rstrip(b"\r")];
    else:
      asExpectedDependencyPythonInternalModuleBaseNames = [];
    
    # Find out which modules/application are defined:
    atasPathsAndNamesToload = [];
    for sProductType in dxProductDetails["asProductTypes"]:
      if sProductType == "Python module":
        # This product offers a Python module; it should be loaded from the parent folder.
        atasPathsAndNamesToload.append((
          [sParentFolderPath] + asOriginalSysPath,
          [dxProductDetails["s0PythonModuleName"]],
        ));
      elif sProductType == "Python application":
        # This product offers a a Python application and/or module; it should be loaded from the main folder, with the
        # parent folder in the path too.
        atasPathsAndNamesToload.append((
          [sMainFolderPath, sParentFolderPath] + asOriginalSysPath,
          dxProductDetails["a0sPythonApplicationNames"],
        ));
      elif sProductType in ["JavaScript module", "PHP module"]:
        pass;
      else:
        raise AssertionError("Unknown \"asProductTypes\" value %s!" % repr(sProductType));
    # Load all modules/applications, use mDebugOutput to report errors if available.
    for asPaths, asNamesToLoad in atasPathsAndNamesToload:
      sys.path = asPaths;
      for sNameToLoad in asNamesToLoad:
        __import__(sNameToLoad, globals(), locals(), [], 0);
    
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
      if asSuperflousDependencyPythonInternalModuleBaseNames:
        print("  The product also missing ('+') and superfluous ('-') Python internal module dependencies!");
      else:
        print("- The product has unreported Python internal module dependencies! (marked with '+')");
    elif asSuperflousDependencyPythonInternalModuleBaseNames:
      print("The product has superfluous Python internal module dependencies! (marked with '-')");
    if asUnexpectedDependencyPythonInteralModuleBaseNames or asSuperflousDependencyPythonInternalModuleBaseNames:
      for sModuleName in sorted(asLoadedPythonInteralModuleBaseNames + asSuperflousDependencyPythonInternalModuleBaseNames):
        print("%s %s" % (
          "+" if sModuleName in asUnexpectedDependencyPythonInteralModuleBaseNames
              else "-" if sModuleName in asSuperflousDependencyPythonInternalModuleBaseNames
              else " ",
              sModuleName
        ));
      print();
      print("The full list should be:");
      for sModuleName in sorted(asLoadedPythonInteralModuleBaseNames):
        print(sModuleName);
      try:
        from mConsole import oConsole;
        oConsole.fRestoreWindow();
      except:
        pass;
      print("Would you like to automatically update the list? (y/N)");
      if input("> ").lower() in ("y", "yes"):
        print("* Updating... ",);
        oInternalPythonModuleDepenciesListFile = open(sInternalPythonModuleDepenciesListFilePath, "wb");
        try:
          sInternalPythonModuleDepenciesList = oInternalPythonModuleDepenciesListFile.write(b"".join([
            b"%s\r\n" % (bytes(sModuleName, "utf-8"),)
            for sModuleName in sorted(asLoadedPythonInteralModuleBaseNames)
          ]));
        except:
          print("failed!");
          raise;
        else:
          print("ok.");
          asUnexpectedDependencyPythonInteralModuleBaseNames = [];
          asSuperflousDependencyPythonInternalModuleBaseNames = [];
        finally:
          oInternalPythonModuleDepenciesListFile.close();
      else:
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
    
    asExpectedDependencyModulesNames = (
      dxProductDetails.get("a0sDependentOnProductNames", []) +
      dxProductDetails.get("a0sReleaseAdditionalProductNames", []) +
      dxProductDetails.get("a0sDebugAdditionalProductNames", []) 
    );
    asUnexpectedDependencyModuleNames = [
      sModuleName
      for sModuleName in dsLoadedDependencyModules_by_sName.keys()
      if sModuleName not in asExpectedDependencyModulesNames
    ];
    asSuperfluousDependencyModuleNames = [
      sModuleName
      for sModuleName in dxProductDetails.get("a0sDependentOnProductNames", [])
      if sModuleName not in dsLoadedDependencyModules_by_sName
    ];
    if asUnexpectedDependencyModuleNames:
      print("The product has unreported dependencies! (marked with '+')");
    if asSuperfluousDependencyModuleNames:
      print("The product has superfluous dependencies! (marked with '-')");
    if asUnexpectedDependencyModuleNames or asSuperfluousDependencyModuleNames:
      for sModuleName in sorted(list(dsLoadedDependencyModules_by_sName.keys()) + asSuperfluousDependencyModuleNames):
        print("%s %s%s" % (
          "+" if sModuleName in asUnexpectedDependencyModuleNames
              else "-" if sModuleName in asSuperfluousDependencyModuleNames
              else " ",
          sModuleName,
          " (%s)" % (dsLoadedDependencyModules_by_sName[sModuleName].__file__,) if sModuleName in dsLoadedDependencyModules_by_sName else "",
        ));
      sys.exit(1);
    
    if gbDebugOutput:
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
          print("%-30s => %s %s" % (sModuleName, sOrigin, sSourceFilePath));
        raise AssertionError("Incorrect dependencies found!");
  except Exception as oException:
    if m0DebugOutput:
      m0DebugOutput.fTerminateWithException(oException);
    raise;
  finally:
    sys.path = [sMainFolderPath, sParentFolderPath] + asOriginalSysPath;
