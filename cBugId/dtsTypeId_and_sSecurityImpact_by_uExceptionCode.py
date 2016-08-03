from NTSTATUS import *;
from HRESULT import *;

dtsTypeId_and_sSecurityImpact_by_uExceptionCode = {
  # uException Code                 # sTypeId                 # sSecurityImpact
  STATUS_WX86_SINGLE_STEP:          ("SingleStep",            None),
  STATUS_WX86_BREAKPOINT:           ("Breakpoint",            None),
  0x40080201:                       ("WRTOriginate",          None),
  0x406D1388:                       ("ThreadName",            None),
  STATUS_GUARD_PAGE_VIOLATION:      ("GuardPage",             "May be a security issue, but probably not exploitable"),
  STATUS_DATATYPE_MISALIGNMENT:     ("DataMisalign",          "May be a security issue"),
  STATUS_BREAKPOINT:                ("Breakpoint",            None),
  STATUS_SINGLE_STEP:               ("SingleStep",            None),
  E_OUTOFMEMORY:                    ("OOM",                   None),
  STATUS_NOT_IMPLEMENTED:           ("PureCall",              "May be a security issue"),
  STATUS_ACCESS_VIOLATION:          ("AV",                    "May be a security issue"), # Special cased if exception parameters are available
  STATUS_IN_PAGE_ERROR:             ("InPageIO",              None),
  STATUS_INVALID_HANDLE:            ("InvalidHandle",         "May be a security issue, but probably not exploitable"),
  STATUS_NO_MEMORY:                 ("OOM",                   None),
  STATUS_ILLEGAL_INSTRUCTION:       ("IllegalInstruction",    "May be a security issue"),
  STATUS_NONCONTINUABLE_EXCEPTION:  ("NonContinuable",        None),
  STATUS_INVALID_DISPOSITION:       ("InvalidDisposition",    "Unknown"),
  STATUS_ARRAY_BOUNDS_EXCEEDED:     ("ArrayBounds",           "May be a security issue, but probably not exploitable"),
  STATUS_FLOAT_DENORMAL_OPERAND:    ("FloatDenormalOperand",  None),
  STATUS_FLOAT_DIVIDE_BY_ZERO:      ("FloatDivideByZero",     None),
  STATUS_FLOAT_INEXACT_RESULT:      ("FloatInexactResult",    None),
  STATUS_FLOAT_INVALID_OPERATION:   ("FloatInvalidOperation", None),
  STATUS_FLOAT_OVERFLOW:            ("FloatOverflow",         None),
  STATUS_FLOAT_STACK_CHECK:         ("FloatStackCheck",       None),
  STATUS_FLOAT_UNDERFLOW:           ("FloatUnderflow",        None),
  STATUS_INTEGER_DIVIDE_BY_ZERO:    ("IntegerDivideByZero",   None),
  STATUS_INTEGER_OVERFLOW:          ("IntegerOverflow",       None),
  STATUS_PRIVILEGED_INSTRUCTION:    ("PrivilegedInstruction", "May be a security issue"),
  STATUS_STACK_OVERFLOW:            ("StackExhaustion",       None),
  STATUS_STOWED_EXCEPTION:          ("WRTLanguage",           "Unknown"),
  STATUS_STACK_BUFFER_OVERRUN:      ("FailFast2",             "Potentially exploitable security issue"),
  0xC000041D:                       ("Verifier",              "May be a security issue"),
  STATUS_FAIL_FAST_EXCEPTION:       ("FailFast",              "May be a security issue"), # Special cased if exception parameters are available
  CPP_EXCEPTION_CODE:               ("C++",                   None),
  STATUS_FAILFAST_OOM_EXCEPTION:    ("OOM",                   None),
};
