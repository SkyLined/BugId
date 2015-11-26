from mHTML import sHTMLDetailsTemplate, fsHTMLEncode;

class cCdbTerminatedUnexpectedlyErrorReport(object):
  def __init__(oErrorReport, oCdbWrapper, uExitCode):
    oErrorReport.sErrorTypeId = "CdbTerminated:%d" % uExitCode;
    oErrorReport.sErrorDescription = "Cdb terminated unexpectedly";
    oErrorReport.sSecurityImpact = None;
    oErrorReport.oException = None;
    oErrorReport.oStack = None;
    oErrorReport.sStackId = None;
    oErrorReport.sCodeId = None;
    oErrorReport.sCodeDescription = None;
    oErrorReport.atsAdditionalInformation = [];
    oErrorReport.sProcessBinaryName = "cdb.exe";
    oErrorReport.sId = oErrorReport.sErrorTypeId;
    oErrorReport.sHTMLStack = None;
    oErrorReport.sHTMLBinaryInformation = None;
    # Turn cdb output into formatted HTML. It is separated into blocks, one for the initial cdb output and one for each
    # command executed.
    sHTMLCdbStdIO = '<hr class="StdIOSeparator"/>'.join(oCdbWrapper.asHTMLCdbStdIOBlocks);
    del oCdbWrapper.asHTMLCdbStdIOBlocks;
    # Create HTML details
    oErrorReport.sHTMLDetails = sHTMLDetailsTemplate % {
      "sId": fsHTMLEncode(oErrorReport.sId),
      "sExceptionDescription": fsHTMLEncode(oErrorReport.sErrorDescription),
      "sProcessBinaryName": fsHTMLEncode(oErrorReport.sProcessBinaryName),
      "sCodeDescription": fsHTMLEncode(oErrorReport.sCodeDescription or "Unknown"),
      "sSecurityImpact": oErrorReport.sSecurityImpact and \
            '<span class="SecurityImpact">%s</span>' % fsHTMLEncode(oErrorReport.sSecurityImpact) or "None",
      "sStack": oErrorReport.sHTMLStack or "Unknown",
      "sBinaryInformation": oErrorReport.sHTMLBinaryInformation or "Unknown",
      "sCdbStdIO": sHTMLCdbStdIO,
    };
