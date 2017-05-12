import json, re, time;

dsProjectDetails = json.loads(open("ProjectDetails.json", "rb").read());
sOldVersion = dsProjectDetails["sVersion"];
sNewVersion = time.strftime("%Y-%m-%d %H:%M");
if sOldVersion == sNewVersion:
  print "Version was updated less than one minute ago, cannot updating at this time.";
else:
  dsProjectDetails["sVersion"] = sNewVersion;
  open("ProjectDetails.json", "wb").write(re.sub(r"\r?\n", "\r\n", json.dumps(dsProjectDetails, sort_keys = True, indent = 2)));
  print "Version updated from %s to %s" % (sOldVersion, sNewVersion);
