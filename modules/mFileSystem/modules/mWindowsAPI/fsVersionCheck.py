import re, urllib;
from sVersion import sVersion;
srVersion = r"(\d{4}[\.\-]\d{2}[\.\-]\d{2}[\. ]\d{2}:?\d{2})";
oVersionMatch = re.match(srVersion, sVersion);
assert oVersionMatch, \
  "Cannot check for updates: local version %s cannot be parsed" % sVersion;
uVersion = long(re.sub(r"[\- \.:]", "", oVersionMatch.group(1)));

sProjectName = "mWindowsAPI";
sUserName = "SkyLined";
sRepositoryName = "mWindowsAPI";
sBranch = "master";

def fsVersionCheck():
  sVersionURL = "https://raw.githubusercontent.com/%s/%s/%s/sVersion.py" % \
      (urllib.quote(sUserName), urllib.quote(sRepositoryName), urllib.quote(sBranch));
  oHTTPRequest = urllib.urlopen(sVersionURL);
  uStatusCode = oHTTPRequest.getcode();
  if uStatusCode != 200:
    return "Cannot check for updates: %s returned HTTP %03d" % (sVersionURL, uStatusCode);
  sResponse = oHTTPRequest.read();
  oLatestVersionMatch = re.match(r'sVersion = "%s";[\r\n]*' % srVersion, sResponse);
  if not oLatestVersionMatch:
    return "Cannot check for updates: remote version file %s cannot be parsed" % (sVersionURL);
  uLatestVersion = long(re.sub(r"[\/ \.]", "", oLatestVersionMatch.group(1)));
  if uVersion == uLatestVersion:
    return "You are running the latest version (%s) of %s" % (sVersion, sProjectName);
  if uVersion > uLatestVersion:
    return "You are running a pre-release version (%s) of %s" % (sVersion, sProjectName);
  sUpdateURL = "https://github.com/%s/%s/archive/%s.zip" % \
      (urllib.quote(sUserName), urllib.quote(sRepositoryName), urllib.quote(sBranch));
  return "An updated version (%s) of %s is available at %s" % (sLatestVersion, sProjectName, sUpdateURL);

if __name__ == "__main__":
  print fsVersionCheck();
