from PrimitiveTypes import *;

################################################################################
# Non-numeric defines
################################################################################
FALSE = False;
NULL = None;
TRUE = True;

################################################################################
# Numeric defines
################################################################################

#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
CREATE_SUSPENDED                        = 0x00000004;
CTRL_BREAK_EVENT                        =          1; # https://docs.microsoft.com/en-us/windows/console/generateconsolectrlevent
CTRL_C_EVENT                            =          0; # https://docs.microsoft.com/en-us/windows/console/generateconsolectrlevent
#DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
DELETE                                  = 0x00010000;
#EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
#FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
#HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
HEAP_ZERO_MEMORY                        = 0x00000008;
#IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
INVALID_FILE_SIZE                       = 0xFFFFFFFF;
INVALID_HANDLE_VALUE                    = HANDLE(-1).value;
#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MAX_MODULE_NAME32                       =        255;
MAX_PATH                                =        260;
MEM_COMMIT                              =     0x1000;
MEM_FREE                                =    0x10000;
MEM_IMAGE                               =  0x1000000;
MEM_MAPPED                              =    0x40000;
MEM_PRIVATE                             =    0x20000;
MEM_RESERVE                             =     0x2000;
#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
#PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
PAGE_EXECUTE                            =       0x10;
PAGE_EXECUTE_READ                       =       0x20;
PAGE_EXECUTE_READWRITE                  =       0x40;
PAGE_EXECUTE_WRITECOPY                  =       0x80;
PAGE_NOACCESS                           =        0x1;
PAGE_READONLY                           =        0x2;
PAGE_READWRITE                          =        0x4;
PAGE_WRITECOPY                          =        0x8;
PROCESS_CREATE_PROCESS                  =     0x0080;
PROCESS_CREATE_THREAD                   =     0x0002;
PROCESS_DUP_HANDLE                      =     0x0040;
PROCESS_QUERY_INFORMATION               =     0x0400;
PROCESS_QUERY_LIMITED_INFORMATION       =     0x1000;
PROCESS_SET_INFORMATION                 =     0x0200;
PROCESS_SET_QUOTA                       =     0x0100;
PROCESS_SUSPEND_RESUME                  =     0x0800;
PROCESS_TERMINATE                       =     0x0001;
PROCESS_VM_OPERATION                    =     0x0008;
PROCESS_VM_READ                         =     0x0010;
PROCESS_VM_WRITE                        =     0x0020;
#RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
READ_CONTROL                            = 0x00020000;
#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
STACK_SIZE_PARAM_IS_A_RESERVATION       = 0x00010000;
STILL_ACTIVE                            =      0x103;
STD_ERROR_HANDLE                        =        -12;
STD_INPUT_HANDLE                        =        -10;
STD_OUTPUT_HANDLE                       =        -11;
SYNCHRONIZE                             = 0x00100000;
#TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT
TH32CS_INHERIT                          = 0x80000000;
TH32CS_SNAPALL                          = 0x0000000F;
TH32CS_SNAPHEAPLIST                     = 0x00000001;
TH32CS_SNAPMODULE                       = 0x00000008;
TH32CS_SNAPMODULE32                     = 0x00000010;
TH32CS_SNAPPROCESS                      = 0x00000002;
TH32CS_SNAPTHREAD                       = 0x00000004;
TOKEN_QUERY                             =     0x0008;
TokenIntegrityLevel                     =         25;
#WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
WRITE_DAC                               = 0x00040000;
WRITE_OWNER                             = 0x00080000;

from Defines_error_codes import *;

