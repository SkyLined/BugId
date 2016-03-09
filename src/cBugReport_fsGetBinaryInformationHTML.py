def cBugReport_fsGetBinaryInformationHTML(oBugReport, oCdbWrapper):
  # Get the binary's cdb name for retreiving version information:
  asBinaryCdbNames = oCdbWrapper.fasGetCdbIdsForModuleFileNameInCurrentProcess(oBugReport.sProcessBinaryName);
  if not oCdbWrapper.bCdbRunning: return None;
  assert len(asBinaryCdbNames) > 0, "Cannot find binary %s module" % oBugReport.sProcessBinaryName;
  # If the binary is loaded as a module multiple times in the process, the first should be the binary that was
  # executed.
  # If this turns out to be wrong, this code should be switch to use "u @$exentry L1" to determine the cdb id of the
  # module in which the process's entry point is found.
  dsGetVersionCdbId_by_sBinaryName = {oBugReport.sProcessBinaryName: asBinaryCdbNames[0]};
  # Get the id frame's module cdb name for retreiving version information:
  if oBugReport.oTopmostRelevantCodeFrame and oBugReport.oTopmostRelevantCodeFrame.oModule:
    dsGetVersionCdbId_by_sBinaryName[oBugReport.oTopmostRelevantCodeFrame.oModule.sBinaryName] = oBugReport.oTopmostRelevantCodeFrame.oModule.sCdbId;
  sBinaryInformationHTML = "";
  for sBinaryName, sCdbId in dsGetVersionCdbId_by_sBinaryName.items():
    asModuleInformationOutput = oCdbWrapper.fasSendCommandAndReadOutput("lmv m *%s" % sCdbId);
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
    sBinaryInformationHTML += (
      (sBinaryInformationHTML and "<br/><br/>" or "") +
      (
        "<h2 class=\"SubHeader\">%s</h2>" % oCdbWrapper.fsHTMLEncode(sBinaryName) +
        "<br/>".join([oCdbWrapper.fsHTMLEncode(s) for s in asModuleInformationOutput[2:]]) # First two lines contain no useful information.
      )
    );
  return sBinaryInformationHTML;