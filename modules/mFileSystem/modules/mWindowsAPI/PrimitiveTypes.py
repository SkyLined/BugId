import ctypes;
from Functions import *;

# We want a list of the names of the primitive types defined below so we can
# automatically generate pointer-to-types for them. We will do this by getting
# a list of the names of all globals now and after they have been defined, so
# we can determine what globals were added.
asGlobalsBeforeTypeDefinitions = globals().keys() + ["asGlobalsBeforeTypeDefinitions"];

################################################################################
# Non-pointer primitive types
################################################################################

#BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
BOOL = ctypes.c_long;
BOOLEAN = ctypes.c_byte;
BYTE = ctypes.c_byte;
#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
CHAR = ctypes.c_short;
#DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
DOUBLE = ctypes.c_double;
DWORD = ctypes.c_ulong;
#FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
FLOAT = ctypes.c_float;
#HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
HACCEL = ctypes.c_void_p;
HANDLE = ctypes.c_void_p;
HBITMAP = ctypes.c_void_p;
HBRUSH = ctypes.c_void_p;
HCOLORSPACE = ctypes.c_void_p;
HDC = ctypes.c_void_p;
HDESK = ctypes.c_void_p;
HDWP = ctypes.c_void_p;
HENHMETAFILE = ctypes.c_void_p;
HFONT = ctypes.c_void_p;
HGDIOBJ = ctypes.c_void_p;
HGLOBAL = ctypes.c_void_p;
HHOOK = ctypes.c_void_p;
HICON = ctypes.c_void_p;
HINSTANCE = ctypes.c_void_p;
HKEY = ctypes.c_void_p;
HKL = ctypes.c_void_p;
HLOCAL = ctypes.c_void_p;
HMENU = ctypes.c_void_p;
HMETAFILE = ctypes.c_void_p;
HMODULE = ctypes.c_void_p;
HMONITOR = ctypes.c_void_p;
HPALETTE = ctypes.c_void_p;
HPEN = ctypes.c_void_p;
HRGN = ctypes.c_void_p;
HRSRC = ctypes.c_void_p;
HSTR = ctypes.c_void_p;
HTASK = ctypes.c_void_p;
HWINSTA = ctypes.c_void_p;
HWND = ctypes.c_void_p;
#IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
INT = ctypes.c_int;
#LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL
LONG = ctypes.c_long;
LPCOLESTR = ctypes.c_wchar_p;
LPCSTR = ctypes.c_char_p;
LPCVOID = ctypes.c_void_p;
LPCWSTR = ctypes.c_wchar_p;
LPOLESTR = ctypes.c_wchar_p;
LPSTR = ctypes.c_char_p;
LPVOID = ctypes.c_void_p;
LPWSTR = ctypes.c_wchar_p;
#OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
OLESTR = ctypes.c_wchar_p;
#PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
PVOID = ctypes.c_void_p;
#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SHORT = ctypes.c_short;
SIZE_T = ctypes.c_size_t;
#TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT
TOKEN_INFORMATION_CLASS = ctypes.c_ulong;
#UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU
UCHAR = ctypes.c_ushort;
UINT = ctypes.c_uint;
ULONG = ctypes.c_ulong;
USHORT = ctypes.c_ushort;
#WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
WCHAR = ctypes.c_wchar;
WORD = ctypes.c_ushort;

################################################################################
# Automatically define "P<type_name>" and "LP<type_name>" as pointer-to-type and
# "PP<type_name>" pointer-to-pointer-to-type. Some of these may make no sense,
# but they do not cause any problems and doing this automatically is a lot
# cleaner than manually adding them.
################################################################################
for sTypeName in globals().keys():
  if sTypeName not in asGlobalsBeforeTypeDefinitions:
    cType = globals()[sTypeName];
    globals()["P" + sTypeName] = POINTER(cType);
    globals()["LP" + sTypeName] = POINTER(cType);
    globals()["PP" + sTypeName] = POINTER(POINTER(cType));
