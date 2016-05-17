import re;
from cException_fSetSecurityImpact import cException_fSetSecurityImpact;
from cException_fSetTypeId import cException_fSetTypeId;
from cStack import cStack;
from cStowedException import cStowedException;
from dxBugIdConfig import dxBugIdConfig;
from NTSTATUS import *;

class cException(object):
  def __init__(oException, oProcess, uCode, sCodeDescription, asExceptionRecord = None):
    oException.oProcess = oProcess;
    oException.uCode = uCode;
    oException.sCodeDescription = sCodeDescription;
    oException.asExceptionRecord = asExceptionRecord; # This is here merely to be able to debug issues - it is not used.
    
    oException.uAddress = None;
    oException.sAddressSymbol = None; # See below
    oException.sUnloadedModuleFileName = None;
    oException.oModule = None;
    oException.uModuleOffset = None;
    oException.oFunction = None;
    oException.uFunctionOffset = None;
    
    oException.uFlags = None;
    oException.auParameters = None;
    oException.sDetails = None;
    oException.sTypeId = None;
    oException.sDescription = None;
    oException.sSecurityImpact = None;
  
  def foGetStack(oException, oCdbWrapper):
    # This is not going to chance, so we can cache it:
    if not hasattr(oException, "oStack"):
      oException.oStack = cStack.foCreate(oCdbWrapper);
      # If the exception record was retreived earlier, it may have been done before all symbols were loaded.
      if oException.asExceptionRecord is not None:
        # Getting the stack loads all symbols, so get the exception record again to extract the "ExceptionAddress" symbol.
        oException.asExceptionRecord = oCdbWrapper.fasSendCommandAndReadOutput(".exr -1");
        if not oCdbWrapper.bCdbRunning: return None;
        for sLine in oException.asExceptionRecord:
          # "ExceptionAddress:" whitespace address whitespace "(" (symbol) ")" }
          oExceptionAddressSymbolMatch = re.match(r"ExceptionAddress\:\s+[0-9A-F`]+\s+\((.+)\)", sLine, re.I);
          if oExceptionAddressSymbolMatch:
            oException.sAddressSymbol = oExceptionAddressSymbolMatch.group(1);
            break;
        # verify the exception and the first stack frame have the same information where applicable.
        oException.fCheckWithFirstStackFrame(oCdbWrapper);
    return oException.oStack;

  def fCheckWithFirstStackFrame(oException, oCdbWrapper):
    # Compare stack with exception information
    if oException.sAddressSymbol:
      doModules_by_sCdbId = oCdbWrapper.fdoGetModulesByCdbIdForCurrentProcess();
      (
        oException.uAddress,
        oException.sUnloadedModuleFileName, oException.oModule, oException.uModuleOffset,
        oException.oFunction, oException.uFunctionOffset
      ) = oCdbWrapper.ftxSplitSymbolOrAddress(oException.sAddressSymbol, doModules_by_sCdbId);
      sCdbLine = oException.sAddressSymbol;
      if oException.uCode == STATUS_BREAKPOINT and oException.oFunction and oException.oFunction.sName == "ntdll.dll!DbgBreakPoint":
        # This breakpoint most likely got inserted into the process by cdb. There will be no trace of it in the stack,
        # so do not try to check that exception information matches the first stack frame.
        return;
    else:
      sCdbLine = "0x%x" % oException.uAddress; # Kinda faking it here :)
    if not oException.oStack.aoFrames:
      # Failed to get stack, use information from exception.
      uFrameNumber = 0;
      oException.oStack.fCreateAndAddStackFrame(
        uFrameNumber, sCdbLine,
        oException.uAddress,
        oException.sUnloadedModuleFileName, oException.oModule, oException.uModuleOffset,
        oException.oFunction, oException.uFunctionOffset,
        None, None
      );
    else:
      if oException.uCode == STATUS_WAKE_SYSTEM_DEBUGGER:
        # This exception does not happen in a particular part of the code, and the exception address is therefore 0.
        # Do not try to find this address on the stack.
        pass;
      elif oException.uCode in [STATUS_WX86_BREAKPOINT, STATUS_BREAKPOINT]:
        oFrame = oException.oStack.aoFrames[0];
        if (
          oFrame.uAddress == oException.uAddress
          and oFrame.sUnloadedModuleFileName == oException.sUnloadedModuleFileName
          and oFrame.oModule == oException.oModule
          and oFrame.uModuleOffset == oException.uModuleOffset
          and oFrame.oFunction == oException.oFunction
          and oFrame.uFunctionOffset == oException.uFunctionOffset
        ):
          pass;
        else:
          # A breakpoint normally happens at an int 3 instruction, and eip/rip will be updated to the next instruction.
          # If the same exception code (0x80000003) is raised using ntdll!RaiseException, the address will be
          # off-by-one, see if this can be fixed:
          if oException.uAddress is not None:
            oException.uAddress -= 1;
          elif oException.uModuleOffset is not None:
            oException.uModuleOffset -= 1;
          elif oException.uFunctionOffset is not None:
            oException.uFunctionOffset -= 1;
          else:
            raise AssertionError("The exception record appears to have no address or offet to adjust.\r\n%s" % oException.asExceptionRecord);
          assert (
            oFrame.uAddress == oException.uAddress
            and oFrame.sUnloadedModuleFileName == oException.sUnloadedModuleFileName
            and oFrame.oModule == oException.oModule
            and oFrame.uModuleOffset == oException.uModuleOffset
            and oFrame.oFunction == oException.oFunction
            and oFrame.uFunctionOffset == oException.uFunctionOffset
          ), "The first stack frame does not appear to match the exception address:\r\n%s\r\n%s" % (
            repr((oFrame.uAddress, oFrame.sUnloadedModuleFileName, oFrame.oModule, oFrame.uModuleOffset, oFrame.oFunction, oFrame.uFunctionOffset)),
            repr((oException.uAddress, oException.sUnloadedModuleFileName, oException.oModule, oException.uModuleOffset, oException.oFunction, oException.uFunctionOffset)),
          );
      else:
        # Check that the address where the exception happened is on the stack and hide any frames that appear above it,
        # as these are not interesting (e.g. ntdll!RaiseException).
        for oFrame in oException.oStack.aoFrames:
          if (
            oFrame.uAddress == oException.uAddress
            and oFrame.sUnloadedModuleFileName == oException.sUnloadedModuleFileName
            and oFrame.oModule == oException.oModule
            and oFrame.uModuleOffset == oException.uModuleOffset
            and oFrame.oFunction == oException.oFunction
            and oFrame.uFunctionOffset == oException.uFunctionOffset
          ):
            break;
          oFrame.bIsHidden = True;
        else:
          raise AssertionError("The exception address %s was not found on the stack\r\n%s" % \
              (sCdbLine, "\r\n".join(oException.oStack.asCdbLines)));
  
  @classmethod
  def foCreate(cException, oCdbWrapper, oProcess, uCode, sCodeDescription):
    asExceptionRecord = oCdbWrapper.fasSendCommandAndReadOutput(".exr -1");
    if not oCdbWrapper.bCdbRunning: return None;
    oException = cException(oProcess, uCode, sCodeDescription, asExceptionRecord);
    # Sample output:
    # |ExceptionAddress: 00007ff6b0f81204 (Tests_x64!fJMP+0x0000000000000004)
    # |   ExceptionCode: c0000005 (Access violation)
    # |  ExceptionFlags: 00000000
    # |NumberParameters: 2
    # |   Parameter[0]: 0000000000000000
    # |   Parameter[1]: ffffffffffffffff
    # |Attempt to read from address ffffffffffffffff
    uParameterCount = None;
    uParameterIndex = None;
    for sLine in asExceptionRecord:
      oNameValueMatch = re.match(r"^\s*%s\s*$" % (
        r"(\w+)(?:\[(\d+)\])?\:\s+"     # (name) optional{ "[" (index) "]" } ":" whitespace
        r"([0-9A-F`]+)"                  # (value)
        r"(?:\s+\((.*)\))?"             # optional{ whitespace "(" (symbol || description) ")" }
      ), sLine, re.I);
      if oNameValueMatch:
        sName, sIndex, sValue, sDetails = oNameValueMatch.groups();
        uValue = long(sValue.replace("`", ""), 16);
        if sName == "ExceptionAddress":
          oException.uAddress = uValue;
          # Unfortnately, symbols may not have been loaded, so the exception address symbols is unreliable.
          # oException.sAddressSymbol = sDetails;
        elif sName == "ExceptionCode":
          assert uValue == uCode, \
              "Exception record has an unexpected ExceptionCode value (0x%08X vs 0x%08X)\r\n%s" % \
              (uValue, uCode, "\r\n".join(asExceptionRecord));
          assert sDetails is None or sDetails == sCodeDescription, \
              "Exception record has an unexpected ExceptionCode description (%s vs %s)\r\n%s" % \
              (repr(sDetails), repr(sCodeDescription), "\r\n".join(asExceptionRecord));
        elif sName == "ExceptionFlags":
          oException.uFlags = uValue;
        elif sName == "NumberParameters":
          uParameterCount = uValue;
          uParameterIndex = 0;
          oException.auParameters = [];
        elif sName == "Parameter":
          assert long(sIndex, 16) == uParameterIndex, \
              "Unexpected parameter #0x%s vs 0x%X\r\n%s" % (sIndex, uParameterIndex, "\r\n".join(asExceptionRecord));
          oException.auParameters.append(uValue);
          uParameterIndex += 1;
        else:
          raise AssertionError("Unknown exception record value %s\r\n%s" % (sLine, "\r\n".join(asExceptionRecord)));
      elif oException.sDetails is None:
        oException.sDetails = sLine;
      else:
        raise AssertionError("Superfluous exception record line %s\r\n%s" % (sLine, "\r\n".join(asExceptionRecord)));
    assert oException.uAddress is not None, \
        "Exception record is missing an ExceptionAddress value\r\n%s" % "\r\n".join(asExceptionRecord);
    assert oException.uFlags is not None, \
        "Exception record is missing an ExceptionFlags value\r\n%s" % "\r\n".join(asExceptionRecord);
    assert uParameterCount is not None, \
        "Exception record is missing an NumberParameters value\r\n%s" % "\r\n".join(asExceptionRecord);
    assert uParameterCount == len(oException.auParameters), \
        "Unexpected number of parameters (%d vs %d)" % (len(oException.auParameters), uParameterCount);
    # Now handle the information in the exception record to create an exception id that uniquely identifies the
    # type of exception and a description of the exception.
    cException_fSetTypeId(oException);
    oException.sDescription = "%s (code 0x%08X)" % (sCodeDescription, uCode);
    cException_fSetSecurityImpact(oException);
    return oException;
