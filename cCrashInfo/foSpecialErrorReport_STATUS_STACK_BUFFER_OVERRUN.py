# Source: winnt.h (codemachine.com/downloads/win81/winnt.h)
# I couldn't find much information on most of these exceptions, so this may be incorrect or at least incomplete.
dsFailFastErrorCodes = {
  0:  ("LegacyGS",      "/GS detected that a stack cookie was modified",
                                                                  "Potentially exploitable security issue"),
  1:  ("VTGuard",       "VTGuard detected that virtual function table cookie was modified",
                                                                  "Potentially exploitable security issue"),
  2:  ("StackCookie",   "FAST_FAIL_STACK_COOKIE_CHECK_FAILURE",   "Potentially exploitable security issue"),
  3:  ("CorruptList",   "Safe unlinking detected a corrupted LIST_ENTRY",
                                                                  "Potentially exploitable security issue"),
  4:  ("BadStack",      "FAST_FAIL_INCORRECT_STACK",              "Potentially exploitable security issue"),
  5:  ("InvalidArg",    "FAST_FAIL_INVALID_ARG",                  "Potentially exploitable security issue"),
  6:  ("GSCookie",      "FAST_FAIL_GS_COOKIE_INIT",               "Potentially exploitable security issue"),
  7:  ("AppExit",       "FAST_FAIL_FATAL_APP_EXIT",               None),
  8:  ("RangeCheck",    "FAST_FAIL_RANGE_CHECK_FAILURE",          "Potentially exploitable security issue"),
  9:  ("Registry",      "FAST_FAIL_UNSAFE_REGISTRY_ACCESS",       "Potentially exploitable security issue"),
  10: ("GuardICall",    "Control flow guard detect a call to an invalid address",    "Potentially exploitable security issue"),
  11: ("GuardWrite",    "FAST_FAIL_GUARD_WRITE_CHECK_FAILURE",    "Potentially exploitable security issue"),
  12: ("FiberSwitch",   "FAST_FAIL_INVALID_FIBER_SWITCH",         "Potentially exploitable security issue"),
  13: ("SetContext",    "FAST_FAIL_INVALID_SET_OF_CONTEXT",       "Potentially exploitable security issue"),
  14: ("RefCount",      "A reference counter was incremented beyond its maximum",
                                                                  "Potentially exploitable security issue"),
  18: ("JumpBuffer",    "FAST_FAIL_INVALID_JUMP_BUFFER",          "Potentially exploitable security issue"),
  19: ("MrData",        "FAST_FAIL_MRDATA_MODIFIED",              "Potentially exploitable security issue"),
  20: ("Cert",          "FAST_FAIL_CERTIFICATION_FAILURE",        "Potentially exploitable security issue"),
  21: ("ExceptChain",   "FAST_FAIL_INVALID_EXCEPTION_CHAIN",      "Potentially exploitable security issue"),
  22: ("Crypto",        "FAST_FAIL_CRYPTO_LIBRARY",               "Potentially exploitable security issue"),
  23: ("DllCallout",    "FAST_FAIL_INVALID_CALL_IN_DLL_CALLOUT"   "Potentially exploitable security issue"),
  24: ("ImageBase",     "FAST_FAIL_INVALID_IMAGE_BASE",           "Potentially exploitable security issue"),
  25: ("DLoadProt",     "FAST_FAIL_DLOAD_PROTECTION_FAILURE",     "Potentially exploitable security issue"),
  26: ("ExtCall",       "FAST_FAIL_UNSAFE_EXTENSION_CALL",        "Potentially exploitable security issue"),
};

def foSpecialErrorReport_STATUS_STACK_BUFFER_OVERRUN(oErrorReport, oCrashInfo, oException):
  # Parameter[0] = fail fast code
  assert len(oException.auParameters) == 1, \
      "Unexpected number of fail fast exception parameters (%d vs 1)" % len(oException.auParameters);
  uFailFastCode = oException.auParameters[0];
  sFailFastCodeId, sFailFastCodeDescription, sSecurityImpact = dsFailFastErrorCodes.get( \
      uFailFastCode, ("Unknown", "unknown code", "May be a security issue"));
  
  oErrorReport.sExceptionTypeId += ":%s" % sFailFastCodeId;
  if sFailFastCodeDescription.startswith("FAIL_FAST_"):
    oErrorReport.sExceptionDescription = "A critical issue was detected (code %X, fail fast code %d: %s)" % \
        (oException.uCode, uFailFastCode, sFailFastCodeDefinition);
  else:
    oErrorReport.sExceptionDescription = sFailFastCodeDescription;
  oErrorReport.sSecurityImpact = sSecurityImpact;
  return oException;