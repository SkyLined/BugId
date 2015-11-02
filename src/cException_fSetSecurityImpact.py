from NTSTATUS import *;

dsId_uCode = {
  STATUS_WX86_SINGLE_STEP:          None,
  STATUS_WX86_BREAKPOINT:           None,
  0x40080201:                       None,
  0x406D1388:                       None,
  STATUS_GUARD_PAGE_VIOLATION:      "May be a security issue, but probably not exploitable",
  STATUS_DATATYPE_MISALIGNMENT:     "May be a security issue",
  STATUS_BREAKPOINT:                None,
  STATUS_SINGLE_STEP:               None,
  0x8007000E:                       None,
  STATUS_ACCESS_VIOLATION:          "May be a security issue", # Special cased if exception parameters are available
  STATUS_IN_PAGE_ERROR:             None,
  STATUS_INVALID_HANDLE:            "May be a security issue, but probably not exploitable",
  STATUS_NO_MEMORY:                 None,
  STATUS_ILLEGAL_INSTRUCTION:       "May be a security issue",
  STATUS_NONCONTINUABLE_EXCEPTION:  None,
  STATUS_ARRAY_BOUNDS_EXCEEDED:     "May be a security issue, but probably not exploitable",
  STATUS_FLOAT_DENORMAL_OPERAND:    None,
  STATUS_FLOAT_DIVIDE_BY_ZERO:      None,
  STATUS_FLOAT_INEXACT_RESULT:      None,
  STATUS_FLOAT_INVALID_OPERATION:   None,
  STATUS_FLOAT_OVERFLOW:            None,
  STATUS_FLOAT_STACK_CHECK:         None,
  STATUS_FLOAT_UNDERFLOW:           None,
  STATUS_INTEGER_DIVIDE_BY_ZERO:    None,
  STATUS_INTEGER_OVERFLOW:          None,
  STATUS_PRIVILEGED_INSTRUCTION:    "May be a security issue",
  STATUS_STACK_OVERFLOW:            None,
  0xC000027B:                       None,
  STATUS_STACK_BUFFER_OVERRUN:      "Potentially exploitable security issue",
  0xC000041D:                       "May be a security issue",
  STATUS_FAIL_FAST_EXCEPTION:       "May be a security issue", # Special cased if exception parameters are available
  0xE06D7363:                       None,
};
def cException_fSetSecurityImpact(oException):
  oException.sSecurityImpact = dsId_uCode.get(oException.uCode, "Unknown");