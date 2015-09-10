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
      return "%s %s %s" % (oErrorReport.sErrorTypeId, oErrorReport.sFunctionId, oErrorReport.sStackId);
    return "%s %s!%s %s" % (oErrorReport.sErrorTypeId, oErrorReport.sProcessBinaryName, oErrorReport.sFunctionId, oErrorReport.sStackId);
  sId = property(fsGetId);
  
  def foTranslateSpecialErrorReport(oErrorReport):
    from cErrorReport_foTranslateSpecialErrorReport import cErrorReport_foTranslateSpecialErrorReport;
    return cErrorReport_foTranslateSpecialErrorReport(oErrorReport);
  
  def foTranslateError(oErrorReport, dtxTranslations):
    from cErrorRepor_foTranslateError import cErrorRepor_foTranslateError;
    return cErrorRepor_foTranslateError(oErrorReport, dtxTranslations);
  
  def fHideTopStackFrames(oErrorReport, dasHiddenFrames_by_sErrorTypeIdRegExp):
    for (sErrorTypeIdRegExp, asHiddenFrames) in dasHiddenFrames_by_sErrorTypeIdRegExp.items():
      if re.match("^(%s)$" % sErrorTypeIdRegExp, oErrorReport.sErrorTypeId):
        oErrorReport.oStack.fHideTopFrames(asHiddenFrames);
  
  @classmethod
  def foCreate(cSelf, oCrashInfo, uExceptionCode, sExceptionDescription):
    # Get current process details
    oProcess = cProcess.foCreate(oCrashInfo);
    if not oCrashInfo._bCdbRunning: return None;
    # Get exception details
    oException = cException.foCreate(oCrashInfo, oProcess, uExceptionCode, sExceptionDescription);
    if not oCrashInfo._bCdbRunning: return None;
    # Get the stack
    oStack = oException.foGetStack(oCrashInfo);
    if not oCrashInfo._bCdbRunning: return None;
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
      oErrorReport = foSpecialErrorReport(oErrorReport, oCrashInfo);
      if not oCrashInfo._bCdbRunning: return None;
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
    for oFrame in oStack.aoFrames:
      if oFrame.bIsHidden:
        # This frame is hidden (because it is irrelevant to the crash)
        asHTMLStack.append("<s>%s</s><br/>" % fsHTMLEncode(oFrame.sAddress));
      else:
        oTopmostRelevantFrame = oTopmostRelevantFrame or oFrame;
        sHTMLAddress = fsHTMLEncode(oFrame.sAddress);
        # Make stack frames without a function symbol italic
        if not oFrame.oFunction:
          sHTMLAddress = "<i>%s</i>" % sHTMLAddress;
        # Hash frame address for id and output frame to html
        if uFramesHashed == oStack.uHashFramesCount:
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
    oErrorReport.sStackId = uFramesHashed == 0 and "##" or sStackId;
    if oStack.bPartialStack:
      asHTMLStack.append("... (rest of the stack was ignored)<br/>");
    # Use a function for the id
    oIdFrame = oTopmostRelevantFunctionFrame or oTopmostRelevantModuleFrame;
    oErrorReport.sFunctionId = oIdFrame and oIdFrame.sSimplifiedAddress or "(unknown)";
    
    # Create the location description 
    oErrorReport.sLocationDescription = oTopmostRelevantFrame and oTopmostRelevantFrame.sAddress or "(unknown)";
    
    # Get the binary's cdb name for retreiving version information:
    asBinaryCdbNames = oCrashInfo.fasGetModuleCdbNames(oErrorReport.sProcessBinaryName);
    if not oCrashInfo._bCdbRunning: return None;
    assert len(asBinaryCdbNames) > 0, "Cannot find binary %s module" % oErrorReport.sProcessBinaryName;
    # Even if the binary is loaded as a module multiple times in the process, the first is always the binary.
    dsGetVersionCdbId_by_sBinaryName = {oErrorReport.sProcessBinaryName: asBinaryCdbNames[0]};
    # Get the id frame's module cdb name for retreiving version information:
    if oIdFrame:
      dsGetVersionCdbId_by_sBinaryName[oIdFrame.oModule.sBinaryName] = oIdFrame.oModule.sCdbId;
    asHTMLBinaryInformation = [];
    for sBinaryName, sCdbId in dsGetVersionCdbId_by_sBinaryName.items():
      asModuleInformationOutput = oCrashInfo._fasSendCommandAndReadOutput("lmv m *%s" % sCdbId);
      if not oCrashInfo._bCdbRunning: return None;
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
      "sCdbIO": "".join(["%s<br/>" % fsHTMLEncode(x) for x in oCrashInfo.asCdbIO]),
    };
    return oErrorReport;
