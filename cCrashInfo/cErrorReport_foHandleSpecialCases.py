from NTSTATUS import *;

# Used for consistency

ddtxExceptionTranslation_xExceptionCodeOrTypeId = {
  "Breakpoint": { # Covers both regular and and WoW64 breakpoints.
    "OOM": (
      "The process triggered a breakpoint to indicate it was unable to allocate enough memory",
      None,
      [
        [     # Chrome
          "chrome.dll!base::`anonymous namespace'::OnNoMemory",
        ], [
          "chrome_child.dll!base::`anonymous namespace'::OnNoMemory",
        ], [
          "chrome_child.dll!blink::reportFatalErrorInMainThread",
          "chrome_child.dll!v8::Utils::ReportApiFailure",
          "chrome_child.dll!v8::Utils::ApiCheck",
          "chrome_child.dll!v8::internal::V8::FatalProcessOutOfMemory",
        ], [  # Edge
          "KERNELBASE.dll!RaiseException",
          "EDGEHTML.dll!Abandonment::InduceAbandonment",
          "EDGEHTML.dll!Abandonment::OutOfMemory",
        ], [  # Firefox
          "mozglue.dll!mozalloc_abort",
          "mozglue.dll!mozalloc_handle_oom",
        ], [
          "xul.dll!js::CrashAtUnhandlableOOM",
        ], [
          "xul.dll!NS_ABORT_OOM",
        ], [  # MSIE
          "KERNELBASE.dll!DebugBreak",
          "script9.dll!ReportFatalException",
          "jscript9.dll!JavascriptDispatch_OOM_fatal_error",
        ],
      ],
    ),
    "HeapCorrupt": (
      "A corrupted heap block was detected",
      "This is probably an exploitable security issue",
      [
        [
          "verifier.dll!VerifierStopMessage",
          "verifier.dll!AVrfpDphReportCorruptedBlock",
        ],
      ],
    ),
  },
  STATUS_WX86_BREAKPOINT: {
    # When a 32-bit application is running on a 64-bit OS, any new processes will generate a STATUS_BREAKPOINT and
    # a status STATUS_WX86_BREAKPOINT exception. The former is recognized as the initial process breakpoint, and the
    # new process is registered. The later is not, but it can be recognized by its stack and should be ignored:
    None: (
      None,
      None,
      [
        [
          "ntdll.dll!LdrpDoDebuggerBreak",
          "ntdll.dll!LdrpInitializeProcess",
        ],
      ],
    ),
  },
  STATUS_ACCESS_VIOLATION: {
    # MSIE 8 can test if DEP is enabled by storing a RET instruction in RW memory and calling it. This causes an
    # access violation if DEP is enabled, which is caught and handled. Therefore this exception should be ignored:
    None: (
      None,
      None,
      [
        [
          "(unknown)", # The location where the RET instruction is stored is not inside a module and has no symbol.
          "corpol.dll!IsNxON",
        ],
      ],
    ),
  },
  STATUS_FAIL_FAST_EXCEPTION: {
    "OOM": (
      "The process triggered a fail-fast exception to indicate it was unable to allocate enough memory",
      None,
      [
        [
          "EDGEHTML.dll!Abandonment::InduceAbandonment",
          "EDGEHTML.dll!Abandonment::OutOfMemory",
        ],
      ],
    ),
  },
  "AVW:NULL": {
    "Assert": (
      "The process caused an access violation by writing to NULL to indicate an assertion failed",
      "This is probably not a security isssue",
      [
        [
          "mozglue.dll!mozalloc_abort",
          "xul.dll!NS_DebugBreak",
        ],
      ],
    ),
    "OOM": (
      "The process caused an access violation by writing to NULL to indicate it was unable to allocate enough memory",
      None,
      [
        [
          "chrome.dll!CrashOnProcessDetach",
          "chrome.dll!DllMain",
          "chrome.dll!__DllMainCRTStartup",
          "chrome.dll!_DllMainCRTStartup",
          "ntdll.dll!LdrpCallInitRoutine",
          "ntdll.dll!LdrShutdownProcess",
          "ntdll.dll!RtlExitUserProcess",
          "kernel32.dll!ExitProcessStub",
          "chrome.dll!__crtExitProcess",
          "chrome.dll!doexit",
          "chrome.dll!_exit",
          "chrome.dll!base::`anonymous namespace'::OnNoMemory",
        ], [
          "chrome.dll!CrashOnProcessDetach",
          "chrome.dll!DllMain",
          "chrome.dll!__DllMainCRTStartup",
          "chrome.dll!_DllMainCRTStartup",
          "ntdll.dll!LdrxCallInitRoutine", # different from the above stack here
          "ntdll.dll!LdrpCallInitRoutine", # and here
          "ntdll.dll!LdrShutdownProcess",
          "ntdll.dll!RtlExitUserProcess",
          "KERNEL32.DLL!ExitProcessImplementation",# and here
          "chrome.dll!__crtExitProcess",
          "chrome.dll!doexit",
          "chrome.dll!_exit",
          "chrome.dll!base::`anonymous namespace'::OnNoMemory",
        ], [
          "chrome_child.dll!blink::reportFatalErrorInMainThread",
          "chrome_child.dll!v8::Utils::ReportApiFailure",
          "chrome_child.dll!v8::Utils::ApiCheck",
          "chrome_child.dll!v8::internal::V8::FatalProcessOutOfMemory",
        ], [
          "chrome_child.dll!WTF::ArrayBuffer::create",
        ], [
          "chrome_child.dll!WTF::partitionOutOfMemory"
        ], [
          "mozglue.dll!mozalloc_abort",
          "mozglue.dll!mozalloc_handle_oom",
        ], [
          "mozglue.dll!moz_abort",
          "mozglue.dll!pages_commit",
        ], [
          "xul.dll!js::CrashAtUnhandlableOOM",
        ], [
          "xul.dll!NS_ABORT_OOM",
        ], [
          "xul.dll!StatsCompartmentCallback",
        ], [
          "xul.dll!nsGlobalWindow::ClearDocumentDependentSlots",
        ],
      ],
    ),
  },
  "C++": {
    "OOM": (
      "The process triggered a C++ exception to indicate it was unable to allocate enough memory",
      None,
      [
        [
          "KERNELBASE.dll!RaiseException",
          "msvcrt.dll!_CxxThrowException",
          "jscript9.dll!Js::Throw::OutOfMemory",
        ],
      ],
    ),
  },
};

def cErrorReport_foHandleSpecialCases(oErrorReport, uExceptionCode, oStack):
  # See if we have a translationtable for this exception:
  for (xExceptionCodeOrTypeId, dtxExceptionTranslation) in ddtxExceptionTranslation_xExceptionCodeOrTypeId.items():
    if xExceptionCodeOrTypeId in (oErrorReport.sExceptionTypeId, uExceptionCode):
      for (sNewExceptionTypeId, txExceptionTranslation) in dtxExceptionTranslation.items():
        (sNewExceptionDescription, sNewSecurityImpact, aasStackTopFrameAddresses) = \
            txExceptionTranslation;
        # See if we have a matching stack top:
        for asStackTopFrameAddresses in aasStackTopFrameAddresses:
          uFrameIndex = 0;
          for sStackTopFrameAddress in asStackTopFrameAddresses:
            oTopFrame = oStack.aoFrames[uFrameIndex];
            uFrameIndex += 1;
            if oTopFrame.sSimplifiedAddress != sStackTopFrameAddress:
              # These frames don't match: stop checking frames
              break;
          else:
            # All frames matched: translate exception:
            if sNewExceptionTypeId is None:
              # This exception should be ignored:
              return None;
            else:
              oErrorReport.sExceptionTypeId = sNewExceptionTypeId;
              oErrorReport.sExceptionDescription = sNewExceptionDescription;
              oErrorReport.sSecurityImpact = sNewSecurityImpact;
              # And hide all the matched frames as they are irrelevant
              for oFrame in oStack.aoFrames[:uFrameIndex]:
                oFrame.bIsHidden = True;
              return oErrorReport;
  # No match; no translation
  return oErrorReport;
