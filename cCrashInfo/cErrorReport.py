import hashlib, re;
from NTSTATUS import *;
from foSpecialErrorReport_CppException import foSpecialErrorReport_CppException;
from foSpecialErrorReport_STATUS_ACCESS_VIOLATION import foSpecialErrorReport_STATUS_ACCESS_VIOLATION;
from foSpecialErrorReport_STATUS_STACK_BUFFER_OVERRUN import foSpecialErrorReport_STATUS_STACK_BUFFER_OVERRUN;
from foSpecialErrorReport_STATUS_STOWED_EXCEPTION import foSpecialErrorReport_STATUS_STOWED_EXCEPTION;
from fErrorReportTranslateException import fErrorReportTranslateException;
from fMarkIrrelevantTopFrames import fMarkIrrelevantTopFrames;
from dxCrashInfoConfig import dxCrashInfoConfig;

dfoSpecialErrorReport_uExceptionCode = {
  CPP_EXCEPTION_CODE: foSpecialErrorReport_CppException,
  STATUS_ACCESS_VIOLATION: foSpecialErrorReport_STATUS_ACCESS_VIOLATION,
  STATUS_STACK_BUFFER_OVERRUN: foSpecialErrorReport_STATUS_STACK_BUFFER_OVERRUN,
  STATUS_STOWED_EXCEPTION: foSpecialErrorReport_STATUS_STOWED_EXCEPTION,
};

sHTMLDetailsTemplate = """
<!doctype html>
<html>
  <head>
    <style>
      * {
        font-family: Courier New, courier, monospace;
      }
      body {
        margin: 5pt;
      }
      div {
        color: white;
        background: black;
        padding: 5pt;
        padding-left: 10pt;
        margin-top: 10pt;
        margin-bottom: 10pt;
      }
      code {
        margin-left: 10pt;
        display: block;
      }
      table, tbody, tr, td {
        cell-padding: 0;
        cell-spacing: 0;
        border: 0;
        padding: 0;
        margin: 0;
      }
      s {
        color: silver;
        text-decoration: line-through;
      }
    </style>
    <title>%(sId)s</title>
  </head>
  <body>
    <div>Details</div>
    <code>
      <table>
        <tbody>
          <tr><td>Id:               </td><td><b>%(sId)s</b></td></tr>
          <tr><td>Description:      </td><td><b>%(sExceptionDescription)s</b></td></tr>
          <tr><td>Process binary:   </td><td>%(sProcessBinaryName)s</td></tr>
          <tr><td>Location:         </td><td>%(sLocationDescription)s</td></tr>
          <tr><td>Security impact:  </td><td>%(sSecurityImpact)s</td></tr>
        </table>
      </tbody>
    </code>
    <div>Stack</div>
    <code>%(sStack)s</code>
    %(sAdditionalInformation)s
    <div>Debugger input/output</div>
    <code>%(sCdbIO)s</code>
  </body>
</html>""".strip();
sHTMLAdditionalInformationTemplate = """
    <div>%(sName)s</div>
    <code>%(sDetails)s</code>
""".strip();
def fsHTMLEncode(sData):
  return sData.replace('&', '&amp;').replace(" ", "&nbsp;").replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;');

class cErrorReport(object):
  def __init__(oSelf, sProcessBinaryName, sExceptionTypeId, sExceptionDescription, sSecurityImpact):
    oSelf.sProcessBinaryName = sProcessBinaryName;
    oSelf.sExceptionTypeId = sExceptionTypeId;
    oSelf.sStackId = None;
    oSelf.sFunctionId = None;
    oSelf.sExceptionDescription = sExceptionDescription;
    oSelf.sLocationDescription = None;
    oSelf.sSecurityImpact = sSecurityImpact;
    oSelf.atsAdditionalInformation = [];
    oSelf.sHTMLDetails = None;
  
  def fsGetId(oSelf):
    if oSelf.sFunctionId.startswith(oSelf.sProcessBinaryName + "!"):
      # No use mentioning this twice.
      return "%s %s %s" % (oSelf.sExceptionTypeId, oSelf.sFunctionId, oSelf.sStackId);
    return "%s %s!%s %s" % (oSelf.sExceptionTypeId, oSelf.sProcessBinaryName, oSelf.sFunctionId, oSelf.sStackId);
  sId = property(fsGetId);
  
  @classmethod
  def foCreateFromException(cSelf, oCrashInfo, oException):
    oSelf = cSelf(
      sProcessBinaryName = oException.oProcess.sBinaryName,
      sExceptionTypeId = oException.sTypeId,
      sExceptionDescription = oException.sDescription,
      sSecurityImpact = oException.sSecurityImpact
    );
    
    # Get application version information:
    asBinaryVersionOutput = oCrashInfo._fasSendCommandAndReadOutput("lmv M *%s" % oException.oProcess.sBinaryName);
    if asBinaryVersionOutput is None: return None;
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
    oSelf.atsAdditionalInformation.append(("%s version information" % oException.oProcess.sBinaryName, asBinaryVersionOutput[2:]));
    
    foSpecialErrorReport = dfoSpecialErrorReport_uExceptionCode.get(oException.uCode);
    if foSpecialErrorReport:
      oException = foSpecialErrorReport(oSelf, oCrashInfo, oException);
      if oException is None: return None;
    
    # Get the stack
    oStack = oException.foGetStack(oCrashInfo);
    if oStack is None: return None;
    # Based on the exception and stack, potentially translate the exception details (eg. Firefox triggers a write
    # access violation at NULL in xul.dll!js::CrashAtUnhandlableOOM when an OOM is detected; this should be reported
    # as OOM and not AVR@NULL.)
    fErrorReportTranslateException(oSelf, oException.uCode, oStack);
    # Based on the exception, potentially mark some top frames as irrelevant. (eg. kernel32!DebugBreak does not cause a
    # debug break, but only executes it on behalf of the caller.)
    fMarkIrrelevantTopFrames(oSelf, oException.uCode, oStack);
    
    # Find out which frame should be the "main" frame and get stack id.
    # * Stack exhaustion can be caused by recursive function calls, where one or more functions repeatedly call
    #   themselves. If possible, this is detected, and the alphabetically first functions is chosen as the main function
    #   The stack hash is created using only the looping functions.
    #   ^^^^ THIS IS NOT YET IMPLEMENTED ^^^
    
    oTopmostRelevantFrame = None;          # topmost relevant frame
    oTopmostRelevantFunctionFrame = None;  # topmost relevant frame that has a function symbol
    oTopmostRelevantModuleFrame = None;    # topmost relevant frame that has no function symbol but a module
    uFramesHashed = 0;
    asHTMLStack = [];
    sStackId = "";
    for oFrame in oStack.aoFrames:
      if oFrame.bIsIrrelevant:
        # This frame is irrelevant
        asHTMLStack.append("<s>%s</s><br/>" % fsHTMLEncode(oFrame.sAddress));
      else:
        oTopmostRelevantFrame = oTopmostRelevantFrame or oFrame;
        sHTMLAddress = fsHTMLEncode(oFrame.sAddress);
        # Make stack frames without a function symbol italic
        if not oFrame.oFunction:
          sHTMLAddress = "<i>%s</i>" % sHTMLAddress;
        # Hash frame address for id and output frame to html
        if uFramesHashed == dxCrashInfoConfig.get("uStackHashFramesCount", 3):
          # no more hashing is needed: just output as is:
          asHTMLStack.append("%s<br/>" % sHTMLAddress);
        elif oFrame.sIdAddress:
          # frame is part of id: add hash and output bold
          oHasher = hashlib.md5();
          oHasher.update(oFrame.sIdAddress);
          sFrameId = "%02X" % ord(oHasher.digest()[0]);
          sStackId += sFrameId;
          uFramesHashed += 1;
          asHTMLStack.append("<b>%s</b> (%s in id)<br/>" % (sHTMLAddress, sFrameId));
          # Determine the top frame for the id:
          if oFrame.oFunction:
            oTopmostRelevantFunctionFrame = oTopmostRelevantFunctionFrame or oFrame;
          elif oFrame.oModule:
            oTopmostRelevantModuleFrame = oTopmostRelevantModuleFrame or oFrame;
        else:
          # This is not part of the id, but between frames that are: add "__" to id and output strike-through
          sStackId += "__";
          asHTMLStack.append("<s>%s</s><br/>" % sHTMLAddress);
    oSelf.sStackId = uFramesHashed == 0 and "##" or sStackId;
    if oStack.bPartialStack:
      asHTMLStack.append("... (rest of the stack was ignored)<br/>");
    # Use a function for the id
    oIdFrame = oTopmostRelevantFunctionFrame or oTopmostRelevantModuleFrame;
    oSelf.sFunctionId = oIdFrame and oIdFrame.sSimplifiedAddress or "(unknown)";
    
    # Create the location description 
    oSelf.sLocationDescription = oTopmostRelevantFrame and oTopmostRelevantFrame.sAddress or "(unknown)";
    
    # Create HTML details
    oSelf.sHTMLDetails = sHTMLDetailsTemplate % {
      "sId": fsHTMLEncode(oSelf.sId),
      "sExceptionDescription": fsHTMLEncode(oSelf.sExceptionDescription),
      "sProcessBinaryName": fsHTMLEncode(oException.oProcess.sBinaryName),
      "sLocationDescription": fsHTMLEncode(oSelf.sLocationDescription),
      "sSecurityImpact": oSelf.sSecurityImpact and "<b>%s</b>" % fsHTMLEncode(oSelf.sSecurityImpact) or "None",
      "sStack": "".join(asHTMLStack),
      "sAdditionalInformation": "".join(
        [
          sHTMLAdditionalInformationTemplate % {
            "sName": fsHTMLEncode(sName),
            "sDetails": "".join(["%s<br/>" % fsHTMLEncode(x) for x in asDetails]),
          }
          for (sName, asDetails) in oSelf.atsAdditionalInformation
        ]
      ),
      "sCdbIO": "".join(["%s<br/>" % fsHTMLEncode(x) for x in oCrashInfo.asCdbIO]),
    };
    return oSelf;
