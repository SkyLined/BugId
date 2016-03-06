import hashlib, re;
from cBugReport_foAnalyzeException_Cpp import cBugReport_foAnalyzeException_Cpp;
from cBugReport_foAnalyzeException_STATUS_ACCESS_VIOLATION import cBugReport_foAnalyzeException_STATUS_ACCESS_VIOLATION;
from cBugReport_foAnalyzeException_STATUS_BREAKPOINT import cBugReport_foAnalyzeException_STATUS_BREAKPOINT;
from cBugReport_foAnalyzeException_STATUS_INVALID_HANDLE import cBugReport_foAnalyzeException_STATUS_INVALID_HANDLE;
from cBugReport_foAnalyzeException_STATUS_FAIL_FAST_EXCEPTION import cBugReport_foAnalyzeException_STATUS_FAIL_FAST_EXCEPTION;
from cBugReport_foAnalyzeException_STATUS_STACK_BUFFER_OVERRUN import cBugReport_foAnalyzeException_STATUS_STACK_BUFFER_OVERRUN;
from cBugReport_foAnalyzeException_STATUS_STACK_OVERFLOW import cBugReport_foAnalyzeException_STATUS_STACK_OVERFLOW;
from cBugReport_foAnalyzeException_STATUS_STOWED_EXCEPTION import cBugReport_foAnalyzeException_STATUS_STOWED_EXCEPTION;
from cBugReport_foAnalyzeException_STATUS_WX86_BREAKPOINT import cBugReport_foAnalyzeException_STATUS_WX86_BREAKPOINT;
from cBugReport_foTranslate import cBugReport_foTranslate;
from cBugReport_fbGetDisassemblyHTML import cBugReport_fbGetDisassemblyHTML;
from cBugReport_fbGetReferencedMemoryHTML import cBugReport_fbGetReferencedMemoryHTML;
from cBugReport_fbGetBinaryInformationHTML import cBugReport_fbGetBinaryInformationHTML;
from cBugReport_fProcessStackIdHTMLAndBugLocation import cBugReport_fProcessStackIdHTMLAndBugLocation;
from cException import cException;
from cProcess import cProcess;
from mHTML import *;
from NTSTATUS import *;

dfoAnalyzeException_by_uExceptionCode = {
  CPP_EXCEPTION_CODE:  cBugReport_foAnalyzeException_Cpp,
  STATUS_ACCESS_VIOLATION: cBugReport_foAnalyzeException_STATUS_ACCESS_VIOLATION,
  STATUS_BREAKPOINT: cBugReport_foAnalyzeException_STATUS_BREAKPOINT,
  STATUS_INVALID_HANDLE: cBugReport_foAnalyzeException_STATUS_INVALID_HANDLE,
  STATUS_FAIL_FAST_EXCEPTION: cBugReport_foAnalyzeException_STATUS_FAIL_FAST_EXCEPTION,
  STATUS_STACK_BUFFER_OVERRUN: cBugReport_foAnalyzeException_STATUS_STACK_BUFFER_OVERRUN,
  STATUS_STACK_OVERFLOW: cBugReport_foAnalyzeException_STATUS_STACK_OVERFLOW,
  STATUS_STOWED_EXCEPTION: cBugReport_foAnalyzeException_STATUS_STOWED_EXCEPTION,
  STATUS_WX86_BREAKPOINT: cBugReport_foAnalyzeException_STATUS_WX86_BREAKPOINT,
};
# Hide some functions at the top of the stack that are merely helper functions and not relevant to the bug:
asHiddenTopFrames = [
  "KERNELBASE.dll!RaiseException",
  "ntdll.dll!KiUserExceptionDispatch",
  "ntdll.dll!NtRaiseException",
  "ntdll.dll!RtlDispatchException",
  "ntdll.dll!RtlpExecuteHandlerForException",
  "ntdll.dll!ZwRaiseException",
];
class cBugReport(object):
  def __init__(oBugReport, oCdbWrapper, sBugTypeId, sBugDescription, sSecurityImpact, oException, oStack):
    oBugReport.oCdbWrapper = oCdbWrapper;
    oBugReport.sBugTypeId = sBugTypeId;
    oBugReport.sBugDescription = sBugDescription;
    oBugReport.sSecurityImpact = sSecurityImpact;
    oBugReport.oException = oException;
    oBugReport.oStack = oStack;
    
    oBugReport.sImportantOutputHTML = oCdbWrapper.sImportantOutputHTML;
    oBugReport.sProcessBinaryName = oException.oProcess and oException.oProcess.sBinaryName;
    # This information is gathered later, when it turns out this bug needs to be reported:
    oBugReport.sStackId = None;
    oBugReport.sId = None;
    oBugReport.sStackHTML = "";
    oBugReport.oTopmostRelevantCodeFrame = None;
    oBugReport.sBugLocation = None;
    oBugReport.sRegistersHTML = "";
    oBugReport.sMemoryHTML = "";
    oBugReport.sDisassemblyHTML = "";
    oBugReport.sBinaryInformationHTML = "";
  
  def foTranslateBug(oBugReport, dtxTranslations):
    return cBugReport_foTranslate(oBugReport, dtxTranslations);
  
  def fHideTopStackFrames(oBugReport, dasHiddenFrames_by_sBugTypeIdRegExp):
    for (sBugTypeIdRegExp, asHiddenFrames) in dasHiddenFrames_by_sBugTypeIdRegExp.items():
      if re.match("^(%s)$" % sBugTypeIdRegExp, oBugReport.sBugTypeId):
        oBugReport.oStack.fHideTopFrames(asHiddenFrames);
  
  @property
  def sDetailsHTML(oBugReport):
    if not hasattr(oBugReport, "_sDetailsHTML"):
      # Turn cdb output into formatted HTML. It is separated into blocks, one for the initial cdb output and one for each
      # command executed.
      sCdbStdIOHTML = '<hr/>'.join(oBugReport.oCdbWrapper.asCdbStdIOBlocksHTML);
      del oBugReport.oCdbWrapper.asCdbStdIOBlocksHTML;
      # Create HTML details
      asBlocksHTML = [];
      if oBugReport.sImportantOutputHTML:
        asBlocksHTML.append(sBlockHTMLTemplate % {"sName": "Potentially important application output", "sContent": oBugReport.sImportantOutputHTML});
      if oBugReport.sStackHTML:
        asBlocksHTML.append(sBlockHTMLTemplate % {"sName": "Stack", "sContent": oBugReport.sStackHTML});
      if oBugReport.sRegistersHTML:
        asBlocksHTML.append(sBlockHTMLTemplate % {"sName": "Registers", "sContent": oBugReport.sRegistersHTML});
      if oBugReport.sMemoryHTML:
        asBlocksHTML.append(sBlockHTMLTemplate % {"sName": "Memory", "sContent": oBugReport.sMemoryHTML});
      if oBugReport.sDisassemblyHTML:
        asBlocksHTML.append(sBlockHTMLTemplate % {"sName": "Disassembly", "sContent": oBugReport.sDisassemblyHTML});
      if oBugReport.sBinaryInformationHTML:
        asBlocksHTML.append(sBlockHTMLTemplate % {"sName": "Binary information", "sContent": oBugReport.sBinaryInformationHTML});
      
      oBugReport._sDetailsHTML = sDetailsHTMLTemplate % {
        "sId": fsHTMLEncode(oBugReport.sId),
        "sBugDescription": fsHTMLEncode(oBugReport.sBugDescription),
        "sBugLocation": fsHTMLEncode(oBugReport.sBugLocation),
        "sSecurityImpact": oBugReport.sSecurityImpact and \
              '<span class="SecurityImpact">%s</span>' % fsHTMLEncode(oBugReport.sSecurityImpact) or "None",
        "sOptionalBlocks": "".join(asBlocksHTML),
        "sCdbStdIO": sCdbStdIOHTML,
      };
    return oBugReport._sDetailsHTML;
  
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
    # Compare stack with exception information
    if oException.sAddressSymbol:
      doModules_by_sCdbId = oCdbWrapper.fdoGetModulesByCdbIdForCurrentProcess();
      (
        uAddress,
        sUnloadedModuleFileName, oModule, uModuleOffset,
        oFunction, uFunctionOffset
      ) = oCdbWrapper.ftxSplitSymbolOrAddress(oException.sAddressSymbol, doModules_by_sCdbId);
      sCdbSource = oException.sAddressSymbol;
    else:
      sCdbSource = "%X" % oException.uAddress; # Kinda faking it here :)
      uAddress = oException.uAddress;
      sUnloadedModuleFileName, oModule, uModuleOffset = None, None, None;
      oFunction, uFunctionOffset = None, None;
    if not oStack.aoFrames:
      # Failed to get stack, use information from exception.
      uFrameNumber = 0;
      oStack.fCreateAndAddStackFrame(oCdbWrapper, uFrameNumber, sCdbSource, uAddress, sUnloadedModuleFileName, oModule, uModuleOffset, oFunction, uFunctionOffset);
    else:
      if oException.uCode in [STATUS_WX86_BREAKPOINT, STATUS_BREAKPOINT]:
        # A breakpoint happens at an int 3 instruction, and eip/rip may have been updated to the next instruction.
        # If the first stack frame is not the same as the exception address, fix this off-by-one:
        oFrame = oStack.aoFrames[0];
        if (
          oFrame.uAddress == uAddress
          and oFrame.sUnloadedModuleFileName == sUnloadedModuleFileName
          and oFrame.oModule == oModule
          and oFrame.uModuleOffset == uModuleOffset
          and oFrame.oFunction == oFunction
          and oFrame.uFunctionOffset == uFunctionOffset
        ):
          pass;
        else:
          if uAddress is not None:
            uAddress -= 1;
          elif uModuleOffset is not None:
            uModuleOffset -= 1;
          elif uFunctionOffset is not None:
            oFrame.uFunctionOffset -= 1;
          else:
            raise AssertionError("The first stack frame appears to have no address or offet to adjust.");
          assert (
            oFrame.uAddress == uAddress
            and oFrame.sUnloadedModuleFileName == sUnloadedModuleFileName
            and oFrame.oModule == oModule
            and oFrame.uModuleOffset == uModuleOffset
            and oFrame.oFunction == oFunction
            and oFrame.uFunctionOffset == uFunctionOffset
          ), "The first stack frame does not appear to match the exception address";
      else:
        # Check that the address where the exception happened is on the stack and hide any frames that appear above it,
        # as these are not interesting (e.g. ntdll!RaiseException).
        for oFrame in oStack.aoFrames:
          if (
            oFrame.uAddress == uAddress
            and oFrame.sUnloadedModuleFileName == sUnloadedModuleFileName
            and oFrame.oModule == oModule
            and oFrame.uModuleOffset == uModuleOffset
            and oFrame.oFunction == oFunction
            and oFrame.uFunctionOffset == uFunctionOffset
          ):
            break;
          oFrame.bIsHidden = True;
        else:
          raise AssertionError("The exception address %s was not found on the stack" % sCdbSource);
      
    # Hide some functions at the top of the stack that are merely helper functions and not relevant to the error:
    oStack.fHideTopFrames(asHiddenTopFrames);
    # Create a preliminary error report.
    oBugReport = cSelf(
      oCdbWrapper = oCdbWrapper,
      sBugTypeId = oException.sTypeId,
      sBugDescription = oException.sDescription,
      sSecurityImpact = oException.sSecurityImpact,
      oException = oException,
      oStack = oStack,
    );
    
    # Perform exception specific analysis:
    foAnalyzeException = dfoAnalyzeException_by_uExceptionCode.get(oException.uCode);
    if foAnalyzeException:
      oBugReport = foAnalyzeException(oBugReport, oCdbWrapper);
      if not oCdbWrapper.bCdbRunning: return None;
      if not oBugReport:
        # This exception is not a bug, continue the application.
        return None;
    
    # Calculate sStackId, create sStackHTML and determine sBugLocation.
    cBugReport_fProcessStackIdHTMLAndBugLocation(oBugReport);
    oBugReport.sId = "%s %s" % (oBugReport.sBugTypeId, oBugReport.sStackId);
    # Get sRegistersHTML
    asRegisters = oCdbWrapper.fasSendCommandAndReadOutput("rM 0x%X" % (0x1 + 0x4 + 0x8 + 0x10 + 0x20 + 0x40));
    if not oCdbWrapper.bCdbRunning: return None;
    sRegistersHTML = "<br/>".join([fsHTMLEncode(s) for s in asRegisters]);
    oBugReport.sRegistersHTML = oBugReport.sRegistersHTML + (oBugReport.sRegistersHTML and "<hr/>" or "") + sRegistersHTML;
    # Get sReferencedMemoryHTML, sDisassemblyHTML and sBinaryInformationHTML.
    if not cBugReport_fbGetReferencedMemoryHTML(oBugReport, oCdbWrapper): return None;
    if not cBugReport_fbGetDisassemblyHTML(oBugReport, oCdbWrapper): return None;
    if not cBugReport_fbGetBinaryInformationHTML(oBugReport, oCdbWrapper): return None;
    
    return oBugReport;
