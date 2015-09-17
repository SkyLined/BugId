// Tests.cpp : Defines the entry point for the console application.
//

#include <SDKDDKVer.h>
#include <stdio.h>
#include <tchar.h>
#include <windows.h>
#include <exception>

#ifdef _WIN64
  #define _tcstop _tcstoui64
#else
  #define _tcstop _tcstoul
#endif

#define _tcstodw _tcstoul

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
  if (uArgumentsCount < 2) {
    _tprintf(_T("Usage:\r\n"));
    _tprintf(_T("  %s exception [arguments]\r\n"), asArguments[0]);
    _tprintf(_T("Exceptions and arguments:\r\n"));
    _tprintf(_T("  AccessViolation [CALL|JMP|READ|WRITE] ADDRESS\r\n"));
    _tprintf(_T("    e.g. AccessViolation CALL DEADBEEF\r\n"));
    _tprintf(_T("  UseAfterFree [READ|WRITE] SIZE\r\n"));
    _tprintf(_T("    e.g. UseAfterFree READ 20\r\n"));
    _tprintf(_T("  OutOfBounds [READ|WRITE] SIZE OFFSET\r\n"));
    _tprintf(_T("    e.g. UseAfterFree READ 20 1\r\n"));
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
    VOID* pAddress = (VOID*) _tcstop(asArguments[3], NULL, 16);
    if (_tcsicmp(asArguments[2], _T("Call")) == 0) {
      fCall(pAddress);
    } else if (_tcsicmp(asArguments[2], _T("Jump")) == 0) {
      fJump(pAddress);
    } else if (_tcsicmp(asArguments[2], _T("Read")) == 0) {
      BYTE x = *(BYTE*)pAddress;
    } else if (_tcsicmp(asArguments[2], _T("Write")) == 0) {
      *(BYTE*)pAddress = 0;
    } else {
      _tprintf(_T("Please use Call, Jmp, Read or Write, not %s\r\n"), asArguments[2]);
    }
  } else if (_tcsicmp(asArguments[1], _T("Breakpoint")) == 0) {
    __debugbreak();
  } else if (_tcsicmp(asArguments[1], _T("C++")) == 0) {
    throw oException;
  } else if (_tcsicmp(asArguments[1], _T("IntegerDivideByZero")) == 0) {
    volatile UINT uN = 0;
    uN = 0 / uN;
  } else if (_tcsicmp(asArguments[1], _T("Numbered")) == 0) {
    DWORD dwCode = (DWORD) _tcstodw(asArguments[2], NULL, 16);
    DWORD dwFlags = (DWORD) _tcstodw(asArguments[3], NULL, 16);
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
    DWORD dwSize = (DWORD) _tcstodw(asArguments[3], NULL, 16);
    BYTE* pMemory = new BYTE[dwSize];
    delete pMemory;
    if (_tcsicmp(asArguments[2], _T("Read")) == 0) {
      BYTE x = *(BYTE*)pMemory;
    } else if (_tcsicmp(asArguments[2], _T("Write")) == 0) {
      *(BYTE*)pMemory = 0;
    } else {
      _tprintf(_T("Please use Read or Write, not %s\r\n"), asArguments[2]);
    }
  } else if (_tcsicmp(asArguments[1], _T("OutOfBounds")) == 0) {
    DWORD dwSize = (DWORD) _tcstodw(asArguments[3], NULL, 16);
    DWORD dwOffset = (DWORD) _tcstodw(asArguments[4], NULL, 16);
    BYTE* pMemory = new BYTE[dwSize];
    if (_tcsicmp(asArguments[2], _T("Read")) == 0) {
      BYTE x = *(BYTE*)(pMemory + dwSize + dwOffset);
    } else if (_tcsicmp(asArguments[2], _T("Write")) == 0) {
      *(BYTE*)(pMemory + dwSize + dwOffset) = 0;
    } else {
      _tprintf(_T("Please use Read or Write, not %s\r\n"), asArguments[2]);
    }
  } else {
    _tprintf(_T("Invalid exception type %s\r\n"), asArguments[1]);
  }
  return 0;
}
