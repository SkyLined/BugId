import ctypes;

CAST = ctypes.cast;
SIZEOF = ctypes.sizeof;

def POINTER(cType_or_xInstance):
  if type(cType_or_xInstance).__class__ == type:
    # If this is a type return a pointer-to-type.
    return ctypes.POINTER(cType_or_xInstance);
  else:
    # If this is an instance return a pointer to the instance.
    return ctypes.byref(cType_or_xInstance);

def STR(sData_or_uSize, uSize = None):
  return ctypes.create_string_buffer(sData_or_uSize, uSize);

def WSTR(sData_or_uSize, uSize = None):
  return ctypes.create_unicode_buffer(sData_or_uSize, uSize);

def SUCCEEDED(uHResult):
  return uHResult < 0x80000000;

def HRESULT_FROM_WIN32(uWin32):
  return 0x80070000 + uWin32;

def WIN32_FROM_HRESULT(hResult):
  assert hResult & 0xFFFF0000 == 0x80070000;
  return hResult &0xFFFF;