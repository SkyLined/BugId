from NTSTATUS import *;
from cErrorReport_foHandleException_CppException import cErrorReport_foHandleException_CppException;
from cErrorReport_foHandleException_STATUS_ACCESS_VIOLATION import cErrorReport_foHandleException_STATUS_ACCESS_VIOLATION;
from cErrorReport_foHandleException_STATUS_STACK_BUFFER_OVERRUN import cErrorReport_foHandleException_STATUS_STACK_BUFFER_OVERRUN;
from cErrorReport_foHandleException_STATUS_STACK_OVERFLOW import cErrorReport_foHandleException_STATUS_STACK_OVERFLOW;
from cErrorReport_foHandleException_STATUS_STOWED_EXCEPTION import cErrorReport_foHandleException_STATUS_STOWED_EXCEPTION;
from cErrorReport_foHandleSpecialCases import cErrorReport_foHandleSpecialCases;
from cErrorReport_fProcesssStack import cErrorReport_fProcesssStack;

dfoSpecialErrorReport_uExceptionCode = {
  CPP_EXCEPTION_CODE: cErrorReport_foHandleException_CppException,
  STATUS_ACCESS_VIOLATION: cErrorReport_foHandleException_STATUS_ACCESS_VIOLATION,
  STATUS_STACK_BUFFER_OVERRUN: cErrorReport_foHandleException_STATUS_STACK_BUFFER_OVERRUN,
  STATUS_STOWED_EXCEPTION: cErrorReport_foHandleException_STATUS_STOWED_EXCEPTION,
  STATUS_STACK_OVERFLOW: cErrorReport_foHandleException_STATUS_STACK_OVERFLOW,
};

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
    # Returns cCrashInfo instance if exception is fatal
    # Returns False if exception is not fatal an application should continue running.
    # Returns None if i/o with cdb failed.
    oSelf = cSelf(
      sProcessBinaryName = oException.oProcess.sBinaryName,
      sExceptionTypeId = oException.sTypeId,
      sExceptionDescription = oException.sDescription,
      sSecurityImpact = oException.sSecurityImpact
    );
    
    # Get application version information:
    asBinaryVersionOutput = oCrashInfo._fasSendCommandAndReadOutput("lmv M *%s" % oException.oProcess.sBinaryName);
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
    oSelf.atsAdditionalInformation.append(("%s version information" % oException.oProcess.sBinaryName, asBinaryVersionOutput[2:]));
    
    # Get the stack
    oStack = oException.foGetStack(oCrashInfo);
    if not oCrashInfo._bCdbRunning: return None;
    # Update the exception in specific cases:
    foSpecialErrorReport = dfoSpecialErrorReport_uExceptionCode.get(oException.uCode);
    if foSpecialErrorReport:
      oException = foSpecialErrorReport(oSelf, oCrashInfo, oException, oStack);
      if not oCrashInfo._bCdbRunning: return None;
    
    # Based on the exception and stack, potentially translate the exception details (eg. Firefox triggers a write
    # access violation at NULL in xul.dll!js::CrashAtUnhandlableOOM when an OOM is detected; this should be reported
    # as OOM and not AVR@NULL. MSIE 8 tests is DEP is enabled by attempting to execute RW memory, this should not be
    # reported at all, and MSIE 8 should be allowed to continue execution)
    oErrorReport = cErrorReport_foHandleSpecialCases(oSelf, oException.uCode, oStack);
    if not oCrashInfo._bCdbRunning: return None;
    if oErrorReport is None:
      # This should not be reported, continue the application
      return None;
    # Based on the exception, potentially hide some irrelevant top frames. (eg. kernel32!DebugBreak does not cause a
    # debug break, but only executes it on behalf of the caller.)
    oStack.fHideIrrelevantFrames(oSelf.sExceptionTypeId, oException.uCode);
    
    cErrorReport_fProcesssStack(oSelf, oCrashInfo, oStack, oException);
  
    return oSelf;
