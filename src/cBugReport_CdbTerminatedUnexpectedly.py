from sDetailsHTMLTemplate import sDetailsHTMLTemplate;

class cBugReport_CdbTerminatedUnexpectedly(object):
  def __init__(oBugReport, oCdbWrapper, uExitCode):
    if uExitCode < 0:
      uExitCode += 1 << 32;
    oBugReport.sBugTypeId = "CdbTerminated:0x%X" % uExitCode;
    oBugReport.sBugDescription = "Cdb terminated unexpectedly";
    oBugReport.sBugLocation = None;
    oBugReport.sSecurityImpact = None;
    oBugReport.oException = None;
    oBugReport.oStack = None;
    
    if oCdbWrapper.bGetDetailsHTML:
      oBugReport.sImportantOutputHTML = oCdbWrapper.sImportantOutputHTML;
    oBugReport.sProcessBinaryName = "cdb.exe";
    
    oBugReport.sId = oBugReport.sBugTypeId;
    oBugReport.sStackId = None;
    oBugReport.sBugLocation = None;
    oBugReport.sBugSourceLocation = None;
    
    if oCdbWrapper.bGetDetailsHTML:
      # Turn cdb output into formatted HTML. It is separated into blocks, one for the initial cdb output and one for each
      # command executed.
      sCdbStdIOHTML = '<hr/>'.join(oCdbWrapper.asCdbStdIOBlocksHTML);
      del oCdbWrapper.asCdbStdIOBlocksHTML;
      # Create HTML details
      oBugReport.sDetailsHTML = sDetailsHTMLTemplate % {
        "sId": oCdbWrapper.fsHTMLEncode(oBugReport.sId),
        "sBugDescription": oCdbWrapper.fsHTMLEncode(oBugReport.sBugDescription),
        "sBugLocation": oCdbWrapper.fsHTMLEncode(oBugReport.sBugLocation or "Unknown"),
        "sSecurityImpact": oBugReport.sSecurityImpact and \
              '<span class="SecurityImpact">%s</span>' % oCdbWrapper.fsHTMLEncode(oBugReport.sSecurityImpact) or "None",
        "sOptionalBlocks": "",
        "sCdbStdIO": sCdbStdIOHTML,
      };
