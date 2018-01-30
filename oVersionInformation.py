import json, os, re, urllib;

rVersion = re.compile(r"(\d{4}[\\\- \.:]\d{2}[\\\- \.:]\d{2}[\\\- \.:]\d{2}[\\\- \.:]?\d{2})");
def fuVersion(sVersion):
  if sVersion == "unknown": return 0;
  oVersionMatch = rVersion.match(sVersion);
  if oVersionMatch is None: return None;
  return long(re.sub(r"[\\\- \.:]", "", oVersionMatch.group(1)));

sProjectDetailsJSONFilePath = os.path.join(os.path.dirname(__file__), "ProjectDetails.json");
dsProjectDetails = json.loads(open(sProjectDetailsJSONFilePath).read());
uCurrentVersion = fuVersion(dsProjectDetails["sVersion"]);
assert uCurrentVersion is not None, \
    "Current version (%s) could not be parsed!" % dsProjectDetails["sVersion"];

dsGitHubRepository = dsProjectDetails["dsGitHubRepository"];
sVersionPyURL = "https://raw.githubusercontent.com/%(sUserName)s/%(sRepositoryName)s/%(sBranch)s/sVersion.py" % dsGitHubRepository;
sProjectDetailsJSONURL = "https://raw.githubusercontent.com/%(sUserName)s/%(sRepositoryName)s/%(sBranch)s/ProjectDetails.json" % dsGitHubRepository;
sUpdateURL = "https://github.com/%(sUserName)s/%(sRepositoryName)s/archive/%(sBranch)s.zip" % dsGitHubRepository;

class cVersionInformation(object):
  def __init__(oVersionInformation):
    oVersionInformation.sProjectName = dsProjectDetails["sProjectName"];
    oVersionInformation.sCurrentVersion = dsProjectDetails["sVersion"];
    oVersionInformation.__bRemoteVersionRetreived = False;
    oVersionInformation.__sLatestVersion = "unknown";
    oVersionInformation.__bUpToDate = None;
    oVersionInformation.sUpdateURL = sUpdateURL;
    oVersionInformation.__bPreRelease = None;
    oVersionInformation.sError = None;
  
  @property
  def sLatestVersion(oVersionInformation):
    if not oVersionInformation.__bRemoteVersionRetreived:
      oVersionInformation.__fRetreiveRemoteVersion();
    return oVersionInformation.__sLatestVersion;
  
  @property
  def bUpToDate(oVersionInformation):
    if not oVersionInformation.__bRemoteVersionRetreived:
      oVersionInformation.__fRetreiveRemoteVersion();
    return oVersionInformation.__bUpToDate;
  
  @property
  def bPreRelease(oVersionInformation):
    if not oVersionInformation.__bRemoteVersionRetreived:
      oVersionInformation.__fRetreiveRemoteVersion();
    return oVersionInformation.__bPreRelease;
  
  def __fRetreiveRemoteVersion(oVersionInformation):
    # Call this only once.
    assert not oVersionInformation.__bRemoteVersionRetreived, \
        "Should not be called twice";
    oVersionInformation.__bRemoteVersionRetreived = True;
    sRemoteProjectDetailsJSON = oVersionInformation.__fsReadURL(sProjectDetailsJSONURL);
    if oVersionInformation.sError: return;
    if sRemoteProjectDetailsJSON:
      try:
        dsRemoteProjectDetails = json.loads(sRemoteProjectDetailsJSON);
      except Exception, oException:
        oVersionInformation.sError = "Cannot check for updates: %s did not return valid JSON data" % sProjectDetailsJSONURL;
        return;
      oVersionInformation.__sLatestVersion = dsRemoteProjectDetails["sVersion"];
    else:
      sRemoteVersionPy = oVersionInformation.__fsReadURL(sVersionPyURL);
      if oVersionInformation.sError: return;
      if sRemoteVersionPy:
        oRemoteVersionMatch = re.match(r"^\s*sVersion\s*=\s*['\x22](.*)['\x22]\s*;\s*$", sRemoteVersionPy, re.M);
        if not oRemoteVersionMatch:
          oVersionInformation.sError = "Cannot check for updates: %s returned unexpected data";
        else:
          oVersionInformation.__sLatestVersion = oRemoteVersionMatch.group(1);
    uLatestVersion = fuVersion(oVersionInformation.__sLatestVersion);
    if uLatestVersion is None:
      oVersionInformation.sError = "Cannot check for updates: latest version (%s) could not be parsed" % oVersionInformation.__sLatestVersion;
    oVersionInformation.__bUpToDate = uCurrentVersion >= uLatestVersion;
    oVersionInformation.__bPreRelease = uCurrentVersion > uLatestVersion;
  
  def __fsReadURL(oVersionInformation, sURL):
    try:
      oHTTPRequest = urllib.urlopen(sURL);
    except Exception as oException:
      oVersionInformation.sError = "Cannot check for updates: connection to %s failed with error %s" % (sURL, str(oException));
      return None;
    uStatusCode = oHTTPRequest.getcode();
    if uStatusCode != 200:
      oVersionInformation.sError = "Cannot check for updates: %s returned HTTP %03d" % (sURL, uStatusCode);
      return None;
    return oHTTPRequest.read();

oVersionInformation = cVersionInformation();

if __name__ == "__main__":
  print "* Version information for %s:" % dsProjectDetails["sProjectName"];
  print "  + Current version: %s" % oVersionInformation.sCurrentVersion;
  print "  + Latest version: %s" % oVersionInformation.sLatestVersion;
  if oVersionInformation.sError:
    print "- Error determining latest version.";
  elif oVersionInformation.bUpdateAvailable:
    print "+ An update is available at:";
    print "  %s" % oVersionInformation.sUpdateURL;
  elif oVersionInformation.bPreRelease:
    print "+ You are running a pre-release version.";
  else:
    print "+ You are running the latest version.";
