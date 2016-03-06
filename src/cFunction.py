class cFunction(object):
  def __init__(oFunction, oModule, sSymbol):
    oFunction.oModule = oModule;
    oFunction.sSymbol = sSymbol;
    oFunction.sName = "%s!%s" % (oFunction.oModule.sBinaryName, oFunction.sSymbol);
    # Replace complex template stuff with "<...>" to make a symbol easier to read.
    asComponents = [""];
    for sChar in oFunction.sSymbol:
      if sChar == "<":
        asComponents.append("");
      elif sChar == ">":
        if len(asComponents) == 1:
          asComponents[-1] += ">"; # this is not closing a "<".
        else:
          sTemplate = asComponents.pop(); # discard contents of template
          asComponents[-1] += "<...>";
      else:
        asComponents[-1] += sChar;
    sSimpifiedSymbol = "<".join(asComponents);
    oFunction.sSimplifiedName = "%s!%s" % (oFunction.oModule.sSimplifiedName, sSimpifiedSymbol);
    oFunction.sUniqueName = sSymbol;
