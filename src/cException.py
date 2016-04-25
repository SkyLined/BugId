import re;
from cException_fSetSecurityImpact import cException_fSetSecurityImpact;
from cException_fSetTypeId import cException_fSetTypeId;
from cStack import cStack;
from cStowedException import cStowedException;
from dxBugIdConfig import dxBugIdConfig;
from NTSTATUS import *;

class cException(object):
  def __init__(oException, oProcess, uCode, sCodeDescription, asExceptionRecord):
    oException.oProcess = oProcess;
    oException.uCode = uCode;
    oException.sCodeDescription = sCodeDescription;
    oException.asExceptionRecord = asExceptionRecord; # This is here merely to be able to debug issues - it is not used.
    oException.uAddress = None;
    oException.sAddressSymbol = None; # See below
    oException.uFlags = None;
    oException.auParameters = None;
    oException.sDetails = None;
    oException.sTypeId = None;
    oException.sDescription = None;
    oException.sSecurityImpact = None;
  
  def foGetStack(oException, oCdbWrapper):
    # This is not going to chance, so we can cache it:
    if not hasattr(oException, "oStack"):
      oStack = oException.oStack = cStack.foCreate(oCdbWrapper);
      # Getting the stack loads all symbols, so the "ExceptionAddress" symbol should now be reliable.
      asExceptionRecord = oCdbWrapper.fasSendCommandAndReadOutput(".exr -1");
      if not oCdbWrapper.bCdbRunning: return None;
      for sLine in asExceptionRecord:
        # "ExceptionAddress:" whitespace address whitespace "(" (symbol) ")" }
        oExceptionAddressSymbolMatch = re.match(r"ExceptionAddress\:\s+[0-9A-F`]+\s+\((.+)\)", sLine, re.I);
        if oExceptionAddressSymbolMatch:
          oException.sAddressSymbol = oExceptionAddressSymbolMatch.group(1);
          break;
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
        oStack.fCreateAndAddStackFrame(uFrameNumber, sCdbSource, uAddress, sUnloadedModuleFileName, oModule, uModuleOffset, oFunction, uFunctionOffset, None, None);
      else:
        if oException.uCode == STATUS_WAKE_SYSTEM_DEBUGGER:
          # This exception does not happen in a particular part of the code, and the exception address is therefore 0.
          # Do not try to find this address on the stack.
          pass;
        elif oException.uCode in [STATUS_WX86_BREAKPOINT, STATUS_BREAKPOINT]:
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
            # A breakpoint normally happens at an int 3 instruction, and eip/rip will be updated to the next instruction.
            # If the same exception code (0x80000003) is raised using ntdll!RaiseException, the address will be
            # off-by-one, see if this can be fixed:
            if uAddress is not None:
              uAddress -= 1;
            elif uModuleOffset is not None:
              uModuleOffset -= 1;
            elif uFunctionOffset is not None:
              uFunctionOffset -= 1;
            else:
              raise AssertionError("The first stack frame appears to have no address or offet to adjust.");
            assert (
              oFrame.uAddress == uAddress
              and oFrame.sUnloadedModuleFileName == sUnloadedModuleFileName
              and oFrame.oModule == oModule
              and oFrame.uModuleOffset == uModuleOffset
              and oFrame.oFunction == oFunction
              and oFrame.uFunctionOffset == uFunctionOffset
            ), "The first stack frame does not appear to match the exception address: %s vs %s" % (
              repr((oFrame.uAddress, oFrame.sUnloadedModuleFileName, oFrame.oModule, oFrame.uModuleOffset, oFrame.oFunction, oFrame.uFunctionOffset)),
              repr((uAddress, sUnloadedModuleFileName, oModule, uModuleOffset, oFunction, uFunctionOffset)),
             );
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
    return oException.oStack;
  
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
