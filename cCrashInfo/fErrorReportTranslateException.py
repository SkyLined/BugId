from NTSTATUS import *;

ddtxExceptionTranslation_xExceptionCodeOrTypeId = {
  STATUS_FAIL_FAST_EXCEPTION: {
    "OOM": (
      "The process was unable to allocate enough memory",
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
      "The process failed an assertion",
      "This is probably not a security isssue",
      [
        "mozglue.dll!mozalloc_abort",
        "xul.dll!NS_DebugBreak",
      ],
    ),
    "OOM": (
      "The process was unable to allocate enough memory",
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
      "The process was unable to allocate enough memory",
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

def fErrorReportTranslateException(oErrorReport, uExceptionCode, oStack):
  # See if we have a translationtable for this exception:
  for (xExceptionCodeOrTypeId, dtxExceptionTranslation) in ddtxExceptionTranslation_xExceptionCodeOrTypeId.items():
    if xExceptionCodeOrTypeId in (oErrorReport.sExceptionTypeId, uExceptionCode):
      for (sNewExceptionTypeId, txExceptionTranslation) in dtxExceptionTranslation.items():
        (sExceptionTypeId, sExceptionDescription, sSecurityImpact, aasStackTopFrameAddresses) = \
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
          oErrorReport.sExceptionTypeId = sExceptionTypeId;
          oErrorReport.sExceptionDescription = sExceptionDescription;
          oErrorReport.sSecurityImpact = sSecurityImpact;
          # And mark all the matched frames as irrelevant
          for oFrame in oStack.aoFrames[:uFrameIndex]:
            oFrame.bIsIrrelevant = True;
          return;
        print;
  # No match; no translation

