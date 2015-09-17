import hashlib;
from cErrorReport_foSpecialErrorReport_CppException import cErrorReport_foSpecialErrorReport_CppException;
from cErrorReport_foSpecialErrorReport_STATUS_ACCESS_VIOLATION import cErrorReport_foSpecialErrorReport_STATUS_ACCESS_VIOLATION;
from cErrorReport_foSpecialErrorReport_STATUS_BREAKPOINT import cErrorReport_foSpecialErrorReport_STATUS_BREAKPOINT;
from cErrorReport_foSpecialErrorReport_STATUS_FAIL_FAST_EXCEPTION import cErrorReport_foSpecialErrorReport_STATUS_FAIL_FAST_EXCEPTION;
from cErrorReport_foSpecialErrorReport_STATUS_STACK_BUFFER_OVERRUN import cErrorReport_foSpecialErrorReport_STATUS_STACK_BUFFER_OVERRUN;
from cErrorReport_foSpecialErrorReport_STATUS_STACK_OVERFLOW import cErrorReport_foSpecialErrorReport_STATUS_STACK_OVERFLOW;
from cErrorReport_foSpecialErrorReport_STATUS_STOWED_EXCEPTION import cErrorReport_foSpecialErrorReport_STATUS_STOWED_EXCEPTION;
from cErrorReport_foSpecialErrorReport_STATUS_WX86_BREAKPOINT import cErrorReport_foSpecialErrorReport_STATUS_WX86_BREAKPOINT;
from cException import cException;
from cProcess import cProcess;
from mHTML import *;
from NTSTATUS import *;

dfoSpecialErrorReport_uExceptionCode = {
  CPP_EXCEPTION_CODE: cErrorReport_foSpecialErrorReport_CppException,
  STATUS_ACCESS_VIOLATION: cErrorReport_foSpecialErrorReport_STATUS_ACCESS_VIOLATION,
  STATUS_BREAKPOINT: cErrorReport_foSpecialErrorReport_STATUS_BREAKPOINT,
  STATUS_FAIL_FAST_EXCEPTION: cErrorReport_foSpecialErrorReport_STATUS_FAIL_FAST_EXCEPTION,
  STATUS_STACK_BUFFER_OVERRUN: cErrorReport_foSpecialErrorReport_STATUS_STACK_BUFFER_OVERRUN,
  STATUS_STOWED_EXCEPTION: cErrorReport_foSpecialErrorReport_STATUS_STOWED_EXCEPTION,
  STATUS_STACK_OVERFLOW: cErrorReport_foSpecialErrorReport_STATUS_STACK_OVERFLOW,
  STATUS_WX86_BREAKPOINT: cErrorReport_foSpecialErrorReport_STATUS_WX86_BREAKPOINT,
};
# Hide some functions at the top of the stack that are merely helper functions and not relevant to the error:
asHiddenTopFrames = [
  "KERNELBASE.dll!RaiseException",
  "ntdll.dll!KiUserExceptionDispatch",
  "ntdll.dll!NtRaiseException",
  "ntdll.dll!RtlDispatchException",
  "ntdll.dll!RtlpExecuteHandlerForException",
  "ntdll.dll!ZwRaiseException",
];
class cErrorReport(object):
  def __init__(oErrorReport, sErrorTypeId, sErrorDescription, sSecurityImpact, oException, oStack):
    oErrorReport.sErrorTypeId = sErrorTypeId;
    oErrorReport.sErrorDescription = sErrorDescription;
    oErrorReport.sSecurityImpact = sSecurityImpact;
    oErrorReport.oException = oException;
    oErrorReport.oStack = oStack;
    oErrorReport.sStackId = None;
    oErrorReport.sFunctionId = None;
    oErrorReport.sLocationDescription = None;
    oErrorReport.atsAdditionalInformation = [];
    oErrorReport.sHTMLDetails = None;
  
  @property
  def sProcessBinaryName(oErrorReport):
    return oErrorReport.oException.oProcess and oErrorReport.oException.oProcess.sBinaryName;
  
  def fsGetId(oErrorReport):
    if not oErrorReport.sProcessBinaryName or oErrorReport.sFunctionId.startswith(oErrorReport.sProcessBinaryName + "!"):
      # If we do not know the process binary ot it's the module in which the error happened, do not mentioning it.
      return "%s %s %s" % (oErrorReport.sStackId, oErrorReport.sErrorTypeId, oErrorReport.sFunctionId);
    return "%s %s %s!%s" % (oErrorReport.sStackId, oErrorReport.sErrorTypeId, oErrorReport.sProcessBinaryName, oErrorReport.sFunctionId);
  sId = property(fsGetId);
  
  def foTranslateSpecialErrorReport(oErrorReport):
    from cErrorReport_foTranslateSpecialErrorReport import cErrorReport_foTranslateSpecialErrorReport;
    return cErrorReport_foTranslateSpecialErrorReport(oErrorReport);
  
  def foTranslateError(oErrorReport, dtxTranslations):
    from cErrorReport_foTranslateError import cErrorReport_foTranslateError;
    return cErrorReport_foTranslateError(oErrorReport, dtxTranslations);
  
  def fHideTopStackFrames(oErrorReport, dasHiddenFrames_by_sErrorTypeIdRegExp):
    for (sErrorTypeIdRegExp, asHiddenFrames) in dasHiddenFrames_by_sErrorTypeIdRegExp.items():
      if re.match("^(%s)$" % sErrorTypeIdRegExp, oErrorReport.sErrorTypeId):
        oErrorReport.oStack.fHideTopFrames(asHiddenFrames);
  
  @classmethod
  def foCreate(cSelf, oCdbWrapper, uExceptionCode, sExceptionDescription):
    # Get current process details
    oProcess = cProcess.foCreate(oCdbWrapper);
    if not oCdbWrapper.bCdbRunning: return None;
    # Get exception details
    oException = cException.foCreate(oCdbWrapper, oProcess, uExceptionCode, sExceptionDescription);
    if not oCdbWrapper.bCdbRunning: return None;
    # Get the stack
    oStack = oException.foGetStack(oCdbWrapper);
    if not oCdbWrapper.bCdbRunning: return None;
    # Hide some functions at the top of the stack that are merely helper functions and not relevant to the error:
    oStack.fHideTopFrames(asHiddenTopFrames);
    # Create a preliminary error report.
    oErrorReport = cSelf(
      sErrorTypeId = oException.sTypeId,
      sErrorDescription = oException.sDescription,
      sSecurityImpact = oException.sSecurityImpact,
      oException = oException,
      oStack = oStack,
    );
    # Make exception specific changes to the error report:
    foSpecialErrorReport = dfoSpecialErrorReport_uExceptionCode.get(oException.uCode);
    if foSpecialErrorReport:
      oErrorReport = foSpecialErrorReport(oErrorReport, oCdbWrapper);
      if not oCdbWrapper.bCdbRunning: return None;
      if not oErrorReport:
        # This exception is not an error, continue the application.
        return None;
    
    # Find out which frame should be the "main" frame and get stack id.
    oTopmostRelevantFrame = None;          # topmost relevant frame
    oTopmostRelevantFunctionFrame = None;  # topmost relevant frame that has a function symbol
    oTopmostRelevantModuleFrame = None;    # topmost relevant frame that has no function symbol but a module
    uFramesHashed = 0;
    asHTMLStack = [];
    sStackId = "";
    for oStackFrame in oStack.aoFrames:
      if oStackFrame.bIsHidden:
        # This frame is hidden (because it is irrelevant to the crash)
        asHTMLStack.append("<s>%s</s><br/>" % fsHTMLEncode(oStackFrame.sAddress));
      else:
        oTopmostRelevantFrame = oTopmostRelevantFrame or oStackFrame;
        sHTMLAddress = fsHTMLEncode(oStackFrame.sAddress);
        # Make stack frames without a function symbol italic
        if not oStackFrame.oFunction:
          sHTMLAddress = "<i>%s</i>" % sHTMLAddress;
        # Hash frame address for id and output frame to html
        if uFramesHashed == oStack.uHashFramesCount:
          # no more hashing is needed: just output as is:
          asHTMLStack.append("%s<br/>" % sHTMLAddress);
        else:
          sStackId += oStackFrame.sId or "__";
          if oStackFrame.sId:
            # frame adds useful infoormation to the id: add hash and output bold
            uFramesHashed += 1;
            asHTMLStack.append("<b>%s</b> (%s in id)<br/>" % (sHTMLAddress, oStackFrame.sId));
            # Determine the top frame for the id:
            if oStackFrame.oFunction:
              oTopmostRelevantFunctionFrame = oTopmostRelevantFunctionFrame or oStackFrame;
            elif oStackFrame.oModule:
              oTopmostRelevantModuleFrame = oTopmostRelevantModuleFrame or oStackFrame;
          else:
            # This is not part of the id, but between frames that are: add "__" to id and output strike-through
            asHTMLStack.append("<s>%s</s><br/>" % sHTMLAddress);
    # If there are not enouogh id-able stack frames, there may be many trailing "_"-s; remove these. Also, if there
    # was not id, or nothing is left after removing the "_"-s, use the id "##".
    oErrorReport.sStackId = sStackId.rstrip("_") or "##";
    if oStack.bPartialStack:
      asHTMLStack.append("... (rest of the stack was ignored)<br/>");
    # Use a function for the id
    oIdFrame = oTopmostRelevantFunctionFrame or oTopmostRelevantModuleFrame;
    oErrorReport.sFunctionId = oIdFrame and oIdFrame.sSimplifiedAddress or "(unknown)";
    
    # Create the location description 
    oErrorReport.sLocationDescription = oTopmostRelevantFrame and oTopmostRelevantFrame.sAddress or "(unknown)";
    
    # Get the binary's cdb name for retreiving version information:
    asBinaryCdbNames = oCdbWrapper.fasGetCdbIdsForModuleFileNameInCurrentProcess(oErrorReport.sProcessBinaryName);
    if not oCdbWrapper.bCdbRunning: return None;
    assert len(asBinaryCdbNames) > 0, "Cannot find binary %s module" % oErrorReport.sProcessBinaryName;
    # If the binary is loaded as a module multiple times in the process, the first should be the binary that was
    # executed.
    dsGetVersionCdbId_by_sBinaryName = {oErrorReport.sProcessBinaryName: asBinaryCdbNames[0]};
    # Get the id frame's module cdb name for retreiving version information:
    if oIdFrame:
      dsGetVersionCdbId_by_sBinaryName[oIdFrame.oModule.sBinaryName] = oIdFrame.oModule.sCdbId;
    asHTMLBinaryInformation = [];
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
      asHTMLBinaryInformation.append(sHTMLBinaryInformationTemplate % {
        "sName": fsHTMLEncode(sBinaryName),
        "sInformation": "".join(["%s<br/>" % fsHTMLEncode(x) for x in asModuleInformationOutput[2:]]),
      });
    
    # Create HTML details
    oErrorReport.sHTMLDetails = sHTMLDetailsTemplate % {
      "sId": fsHTMLEncode(oErrorReport.sId),
      "sExceptionDescription": fsHTMLEncode(oErrorReport.sErrorDescription),
      "sProcessBinaryName": fsHTMLEncode(oErrorReport.sProcessBinaryName),
      "sLocationDescription": fsHTMLEncode(oErrorReport.sLocationDescription),
      "sSecurityImpact": oErrorReport.sSecurityImpact and "<b>%s</b>" % fsHTMLEncode(oErrorReport.sSecurityImpact) or "None",
      "sStack": "".join(asHTMLStack),
      "sBinaryInformation": "".join(asHTMLBinaryInformation),
      "sCdbIO": "".join(["%s<br/>" % fsHTMLEncode(x) for x in oCdbWrapper.asCdbStdIO]),
    };
    return oErrorReport;
