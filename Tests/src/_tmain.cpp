#include <SDKDDKVer.h>
#include <stdio.h>
#include <tchar.h>
#include <windows.h>
#include <exception>

#ifdef _WIN64
  #define fpFromHexString(sInput) ((VOID*)_tcstoui64(sInput, NULL, 16))
#else
  #define fpFromHexString(sInput) ((VOID*)_tcstoul(sInput, NULL, 16))
#endif

#define fdwFromHexString(sInput) ((DWORD)_tcstoul(sInput, NULL, 16))
#define fuFromHexString(sInput) ((UINT)_tcstoul(sInput, NULL, 16))
#define fiFromHexString(sInput) ((INT)_tcstol(sInput, NULL, 16))

extern "C" {
  VOID __stdcall fCall(VOID*);
  VOID __stdcall fJump(VOID*);
  VOID __stdcall fIllegalInstruction();
  VOID __stdcall fIntergerOverflow();
  VOID __stdcall fPrivilegedInstruction();
}

// C++ exception
class cException: public std::exception {
} oException;

// cPureCallBase is initialize before initializing cPureCall. cPureCallBase call fVirtual,
// which has not been initialized, causing a pure vitual function call error.
class cPureCallBase;
VOID fCallVirtual (cPureCallBase* pBase);
class cPureCallBase {
  public:
    virtual void fVirtual() = 0;
	  cPureCallBase() { fCallVirtual(this); }
};
VOID fCallVirtual (cPureCallBase* pBase) {
  pBase->fVirtual();
}
class cPureCall : cPureCallBase {
  public:
     void fVirtual() {}
};
VOID fStackRecursion() {
  alloca(0x1000);
  fStackRecursion();
}

UINT _tmain(UINT uArgumentsCount, _TCHAR* asArguments[]) {
  _set_abort_behavior( 0, _WRITE_ABORT_MSG);
  if (uArgumentsCount < 2) {
    _tprintf(_T("Usage:\r\n"));
    _tprintf(_T("  %s exception [arguments]\r\n"), asArguments[0]);
    _tprintf(_T("Exceptions and arguments:\r\n"));
    _tprintf(_T("  AccessViolation [CALL|JMP|READ|WRITE] ADDRESS\r\n"));
    _tprintf(_T("    e.g. AccessViolation CALL DEADBEEF\r\n"));
    _tprintf(_T("         (attempt to execute code at address 0xDEADBEEF using a CALL instruction)\r\n"));
    _tprintf(_T("  UseAfterFree [READ|WRITE] SIZE OFFSET\r\n"));
    _tprintf(_T("    e.g. UseAfterFree READ 20 4\r\n"));
    _tprintf(_T("         (free a 0x20 byte heap buffer and read from offset 4 of the free memory)\r\n"));
    _tprintf(_T("  OutOfBounds [Heap|Stack] [READ|WRITE] SIZE OFFSET\r\n"));
    _tprintf(_T("    e.g. OutOfBounds Heap READ 20 1\r\n"));
    _tprintf(_T("         (read from an address 1 byte past the end of a 20 byte heap buffer)\r\n"));
    _tprintf(_T("    -or- OutOfBounds Stack Write 20 4\r\n"));
    _tprintf(_T("         (write to an address 4 bytes past the end of a 20 byte stack buffer)\r\n"));
    _tprintf(_T("  BufferOverrun [Heap|Stack] [READ|WRITE] SIZE OVERRUN\r\n"));
    _tprintf(_T("    e.g. BufferOverrun Heap READ 20 4\r\n"));
  	_tprintf(_T("         (read 4 bytes past the end of a 0x20 byte heap buffer)\r\n"));
    _tprintf(_T("    -or- BufferOverrun Stack Write 30 1\r\n"));
    _tprintf(_T("         (read 1 byte past the end of a 0x30 byte stack buffer)\r\n"));
    _tprintf(_T("  StaticStaticBufferOverrun10 [READ|WRITE] SIZE OVERRUN\r\n"));
    _tprintf(_T("    e.g. StaticStaticBufferOverrun10 READ 14\r\n"));
    _tprintf(_T("    -or- StaticStaticBufferOverrun10 Write 11\r\n"));
    _tprintf(_T("  Breakpoint\r\n"));
    _tprintf(_T("  C++\r\n"));
    _tprintf(_T("  IntegerDivideByZero\r\n"));
    _tprintf(_T("  Numbered NUMBER FLAGS\r\n"));
    _tprintf(_T("    e.g. Numbered 41414141 42424242\r\n"));
    _tprintf(_T("  IllegalInstruction\r\n"));
    _tprintf(_T("  PrivilegedInstruction\r\n"));
    _tprintf(_T("  PureCall\r\n"));
    _tprintf(_T("  StackExhaustion\r\n"));
    _tprintf(_T("  RecursiveCall\r\n"));
  } else if (_tcsicmp(asArguments[1], _T("AccessViolation")) == 0) {
    VOID* pAddress = fpFromHexString(asArguments[3]);
    if (_tcsicmp(asArguments[2], _T("Call")) == 0) {
      fCall(pAddress);
    } else if (_tcsicmp(asArguments[2], _T("Jump")) == 0) {
      fJump(pAddress);
    } else if (_tcsicmp(asArguments[2], _T("Read")) == 0) {
      BYTE x = *(BYTE*)pAddress;
    } else if (_tcsicmp(asArguments[2], _T("Write")) == 0) {
      *(BYTE*)pAddress = 0;
    } else {
      _ftprintf(stderr, _T("Please use Call, Jmp, Read or Write, not %s\r\n"), asArguments[2]);
      return 1;
    }
  } else if (_tcsicmp(asArguments[1], _T("Breakpoint")) == 0) {
    __debugbreak();
  } else if (_tcsicmp(asArguments[1], _T("C++")) == 0) {
    throw oException;
  } else if (_tcsicmp(asArguments[1], _T("IntegerDivideByZero")) == 0) {
    volatile UINT uN = 0;
    uN = 0 / uN;
  } else if (_tcsicmp(asArguments[1], _T("Numbered")) == 0) {
    DWORD dwCode = fdwFromHexString(asArguments[2]);
    DWORD dwFlags = fdwFromHexString(asArguments[3]);
    // TODO: implement arguments?
    RaiseException(dwCode, dwFlags, 0, NULL);
  } else if (_tcsicmp(asArguments[1], _T("IllegalInstruction")) == 0) {
    fIllegalInstruction();
  } else if (_tcsicmp(asArguments[1], _T("PrivilegedInstruction")) == 0) {
    fPrivilegedInstruction();
  } else if (_tcsicmp(asArguments[1], _T("PureCall")) == 0) {
    cPureCall oPureCall;
  } else if (_tcsicmp(asArguments[1], _T("StackExhaustion")) == 0) {
    while (1) alloca(0x1000);
  } else if (_tcsicmp(asArguments[1], _T("RecursiveCall")) == 0) {
    fStackRecursion();
  } else if (_tcsicmp(asArguments[1], _T("UseAfterFree")) == 0) {
    DWORD uSize = fuFromHexString(asArguments[3]);
    BYTE* pMemory = new BYTE[uSize];
    delete pMemory;
    if (_tcsicmp(asArguments[2], _T("Read")) == 0) {
      BYTE x = *(BYTE*)pMemory;
    } else if (_tcsicmp(asArguments[2], _T("Write")) == 0) {
      *(BYTE*)pMemory = 0;
    } else {
      _ftprintf(stderr, _T("Please use Read or Write, not %s\r\n"), asArguments[2]);
      return 1;
    }
  } else if (_tcsicmp(asArguments[1], _T("OutOfBounds")) == 0) {
    UINT uSize = fuFromHexString(asArguments[4]);
    INT iOffset = fiFromHexString(asArguments[5]);
    BYTE* pMemory = NULL;
    BOOL bDelete = FALSE;
    if (_tcsicmp(asArguments[2], _T("Heap")) == 0) {
      pMemory = new BYTE[uSize];
      bDelete = TRUE;
    } else if (_tcsicmp(asArguments[2], _T("Stack")) == 0) {
      pMemory = (BYTE*)alloca(uSize);
    } else {
      _ftprintf(stderr, _T("Please use Heap or Stack, not %s\r\n"), asArguments[2]);
      return 1;
    }
    if (_tcsicmp(asArguments[3], _T("Read")) == 0) {
      BYTE x = *(BYTE*)(pMemory + iOffset);
    } else if (_tcsicmp(asArguments[3], _T("Write")) == 0) {
      *(BYTE*)(pMemory + iOffset) = 0;
    } else {
      _ftprintf(stderr, _T("Please use Read or Write, not %s\r\n"), asArguments[3]);
      return 1;
    }
    if (bDelete) {
      delete pMemory;
    }
  } else if (_tcsicmp(asArguments[1], _T("BufferOverrun")) == 0) {
    UINT uSize = fuFromHexString(asArguments[4]);
    UINT uOverrun = fuFromHexString(asArguments[5]);
    BYTE* pMemory;
    BOOL bDelete = FALSE;
    if (_tcsicmp(asArguments[2], _T("Heap")) == 0) {
      pMemory = new BYTE[uSize];
      bDelete = TRUE;
    } else if (_tcsicmp(asArguments[2], _T("Stack")) == 0) {
      pMemory = (BYTE*)alloca(uSize);
    } else {
      _ftprintf(stderr, _T("Please use Heap or Stack, not %s\r\n"), asArguments[2]);
      return 1;
    }
    if (_tcsicmp(asArguments[3], _T("Read")) == 0) {
      for (BYTE* pAddress = pMemory; pAddress < pMemory + uSize + uOverrun; pAddress++) {
        BYTE x = *pAddress;
      }
    } else if (_tcsicmp(asArguments[3], _T("Write")) == 0) {
      for (BYTE* pAddress = pMemory; pAddress < pMemory + uSize + uOverrun; pAddress++) {
        *pAddress = 0;
      }
    } else {
      _ftprintf(stderr, _T("Please use Read or Write, not %s\r\n"), asArguments[3]);
      return 1;
    }
    if (bDelete) {
      delete pMemory;
    }
  } else if (_tcsicmp(asArguments[1], _T("StaticBufferOverrun10")) == 0) {
    UINT uOverrun = fuFromHexString(asArguments[3]);
    BYTE pMemory[10];
    if (_tcsicmp(asArguments[2], _T("Read")) == 0) {
      for (BYTE* pAddress = pMemory; pAddress < pMemory + 10 + uOverrun; pAddress++) {
        BYTE x = *pAddress;
      }
    } else if (_tcsicmp(asArguments[2], _T("Write")) == 0) {
      for (BYTE* pAddress = pMemory; pAddress < pMemory + 10 + uOverrun; pAddress++) {
        *pAddress = 0;
      }
    } else {
      _ftprintf(stderr, _T("Please use Read or Write, not %s\r\n"), asArguments[2]);
      return 1;
    }
  } else if (_tcsicmp(asArguments[1], _T("Nop")) == 0) {
  } else if (_tcsicmp(asArguments[1], _T("CPUUsage")) == 0) {
    while(1){};
  } else {
    _ftprintf(stderr, _T("Invalid test type %s\r\n"), asArguments[1]);
    return 1;
  }
  return 0;
}
