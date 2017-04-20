import time;

sNewVersion = time.strftime("%Y-%m-%d %H:%M");
oVersionFile = open("sVersion.py", "wb");
oVersionFile.write("sVersion = %s;\r\n" % repr(sNewVersion));
print "New version = %s" % sNewVersion;
