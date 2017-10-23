import mWindowsRegistry;

def fsReadRegistryValue(sValueName):
  oRegistryValue = mWindowsRegistry.foGetValue("HKLM", r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", sValueName);
  assert oRegistryValue, \
      "Cannor read HKLM\SOFTWARE\Microsoft\Windows NT\%s" % sValueName;
  assert oRegistryValue.sType == "REG_SZ", \
      r"Expected HKLM\SOFTWARE\Microsoft\Windows NT\%s to be REG_SZ, got %s" % (sValueName, oRegistryValue.sType);
  return oRegistryValue.xValue;

class cWindowsVersion(object):
  def __init__(oSelf):
    oSelf.__sProductName = None;
    oSelf.__sReleaseId = None;
    oSelf.__sCurrentBuild = None;
  
  @property
  def sProductName(oSelf):
    if not oSelf.__sProductName:
      oSelf.__sProductName = fsReadRegistryValue("ProductName");
    return oSelf.__sProductName;

  @property
  def sReleaseId(oSelf):
    if not oSelf.__sReleaseId:
      oSelf.__sReleaseId = fsReadRegistryValue("ReleaseId");
    return oSelf.__sReleaseId;
  @property
  def uReleaseId(oSelf):
    return long(oSelf.sReleaseId);

  @property
  def sCurrentBuild(oSelf):
    if not oSelf.__sCurrentBuild:
      oSelf.__sCurrentBuild = fsReadRegistryValue("CurrentBuild");
    return oSelf.__sCurrentBuild;
  @property
  def uCurrentBuild(oSelf):
    return long(oSelf.sCurrentBuild);
  
  def __str__(oSelf):
    return "%s release %s, build %s" % (oSelf.sProductName, oSelf.sReleaseId, oSelf.sCurrentBuild);

oWindowsVersion = cWindowsVersion();