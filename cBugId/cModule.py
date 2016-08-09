import re;
from cFunction import cFunction;

class cModule(object):
  def __init__(oModule, sCdbId, sBinaryName, uStartAddress, uEndAddress):
    oModule.sCdbId = sCdbId;
    oModule.sBinaryName = sBinaryName;
    oModule.uStartAddress = uStartAddress;
    oModule.uEndAddress = uEndAddress;
    oModule._doFunction_by_sSymbol = {};
    oModule.sSimplifiedName = sBinaryName.lower();
    oModule.sUniqueName = sBinaryName.lower();
    oModule.sFileVersion = None;
    oModule.sTimestamp = None;
  
  def foGetOrCreateFunction(oModule, sSymbol):
    if sSymbol not in oModule._doFunction_by_sSymbol:
      oModule._doFunction_by_sSymbol[sSymbol] = cFunction(oModule, sSymbol);
    return oModule._doFunction_by_sSymbol[sSymbol];
  
  def fsGetInformationHTML(oModule, oCdbWrapper):
    # Also sets oModule.sFileVersion if possible.
    asModuleInformationOutput = oCdbWrapper.fasSendCommandAndReadOutput(
      "lmv m *%s; $$ Get module information" % oModule.sCdbId,
      bOutputIsInformative = True,
    );
    if not oCdbWrapper.bCdbRunning: return None;
    # Sample output:
    # |0:004> lmv M firefox.exe
    # |start             end                 module name
    # |00000000`011b0000 00000000`0120f000   firefox    (deferred)             
    # |    Image path: firefox.exe
    # |    Image name: firefox.exe
    # |    Timestamp:        Thu Aug 13 03:23:30 2015 (55CBF192)
    # |    CheckSum:         0006133B
    # |    ImageSize:        0005F000
    # |    File version:     40.0.2.5702
    # |    Product version:  40.0.2.0
    # |    File flags:       0 (Mask 3F)
    # |    File OS:          4 Unknown Win32
    # |    File type:        2.0 Dll
    # |    File date:        00000000.00000000
    # |    Translations:     0000.04b0
    # |    CompanyName:      Mozilla Corporation
    # |    ProductName:      Firefox
    # |    InternalName:     Firefox
    # |    OriginalFilename: firefox.exe
    # |    ProductVersion:   40.0.2
    # |    FileVersion:      40.0.2
    # |    FileDescription:  Firefox
    # |    LegalCopyright:   (c)Firefox and Mozilla Developers; available under the MPL 2 license.
    # |    LegalTrademarks:  Firefox is a Trademark of The Mozilla Foundation.
    # |    Comments:         Firefox is a Trademark of The Mozilla Foundation.
    # The first two lines can be skipped.
    asModuleInformationHTML = [
        "<h2 class=\"SubHeader\">%s</h2>" % oCdbWrapper.fsHTMLEncode(oModule.sBinaryName),
    ];
    for sLine in asModuleInformationOutput[2:]: # First two lines contain no useful information.
      oFileVersionMatch = re.match(r"^    File version:\s*(.*?)\s*$", sLine);
      if oFileVersionMatch:
        oModule.sFileVersion = oFileVersionMatch.group(1);
      oTimestampMatch = re.match(r"^    Timestamp:\s*(.*?)\s*$", sLine);
      if oTimestampMatch:
        oModule.sTimestamp = oTimestampMatch.group(1);
      asModuleInformationHTML.append(
        '<span class="BinaryInformation">%s</span>' % oCdbWrapper.fsHTMLEncode(sLine)
      );
    return "<br/>".join(asModuleInformationHTML);
