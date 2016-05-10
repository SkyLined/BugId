import re;

def fsHTMLEncode(sLine):
  return sLine.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;');

def cCdbWrapper_fsHTMLEncode(oCdbWrapper, sLine):
  # This will only apply a link to the first match, but improving it would be rather complex. Since I've not encountered
  # a situation where more than one links is needed, I've kept it simple.
  for (srSourceFilePath, sURLTemplate) in oCdbWrapper.dsURLTemplate_by_srSourceFilePath.items():
    oMatch = re.search(srSourceFilePath, sLine);
    if oMatch:
      sBefore = sLine[:oMatch.start()];
      sPath = oMatch.group(0);
      sURL = (sURLTemplate % oMatch.groupdict()).replace("\\", "/");
      sAfter = sLine[oMatch.end():];
      return "%s<a target=\"_blank\" href=\"%s\">%s</a>%s" % \
          (fsHTMLEncode(sBefore), sURL, fsHTMLEncode(sPath), fsHTMLEncode(sAfter));
  else:
    return fsHTMLEncode(sLine);

