from NTSTATUS import *;

dsId_uCode = {
  STATUS_WX86_SINGLE_STEP: "Not a security issue",
  STATUS_WX86_BREAKPOINT: "Not a security issue",
  0x40080201: "Not a security issue",
  0x406D1388: "Not a security issue",
  STATUS_GUARD_PAGE_VIOLATION: "May be a security issue, but probably not exploitable",
  STATUS_DATATYPE_MISALIGNMENT: "May be a security issue",
  STATUS_BREAKPOINT: "Not a security issue",
  STATUS_SINGLE_STEP: "Not a security issue",
  0x8007000E: "Not a security issue",
  STATUS_ACCESS_VIOLATION: "May be a security issue", # Special cased if exception parameters are available
  STATUS_IN_PAGE_ERROR: "Not a security issue",
  STATUS_INVALID_HANDLE: "May be a security issue, but probably not exploitable",
  STATUS_NO_MEMORY: "Not a security issue",
  STATUS_ILLEGAL_INSTRUCTION: "May be a security issue",
  STATUS_NONCONTINUABLE_EXCEPTION: "Not a security issue",
  STATUS_ARRAY_BOUNDS_EXCEEDED: "May be a security issue, but probably not exploitable",
  STATUS_FLOAT_DENORMAL_OPERAND: "Not a security issue",
  STATUS_FLOAT_DIVIDE_BY_ZERO: "Not a security issue",
  STATUS_FLOAT_INEXACT_RESULT: "Not a security issue",
  STATUS_FLOAT_INVALID_OPERATION: "Not a security issue",
  STATUS_FLOAT_OVERFLOW: "Not a security issue",
  STATUS_FLOAT_STACK_CHECK: "Not a security issue",
  STATUS_FLOAT_UNDERFLOW: "Not a security issue",
  STATUS_INTEGER_DIVIDE_BY_ZERO: "Not a security issue",
  STATUS_INTEGER_OVERFLOW: "Not a security issue",
  STATUS_PRIVILEGED_INSTRUCTION: "May be a security issue",
  STATUS_STACK_OVERFLOW: "Not a security issue",
  0xC000027B: "Not a security issue",
  STATUS_STACK_BUFFER_OVERRUN: "Potentially exploitable security issue",
  0xC000041D: "May be a security issue",
  STATUS_FAIL_FAST_EXCEPTION: "May be a security issue", # Special cased if exception parameters are available
  0xE06D7363: "Not a security issue",
};
def fsGetSecurityImpact(uExceptionCode):
  return dsId_uCode.get(uExceptionCode) or "Unknown";