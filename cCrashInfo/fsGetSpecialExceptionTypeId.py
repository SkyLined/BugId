from NTSTATUS import *;

ddsFunctionName_sSpecialTypeId_sTypeId = {
  "AVW@NULL": {
    "chrome_child.dll!blink::reportFatalErrorInMainThread": "FatalError",
    "chrome_child.dll!WTF::partitionOutOfMemory": "OOM",
    "mozalloc.dll!mozalloc_abort": "OOM",
    "xul.dll!js::CrashAtUnhandlableOOM": "OOM",
    "xul.dll!NS_ABORT_OOM": "OOM",
    "xul.dll!StatsCompartmentCallback": "OOM",
    "xul.dll!nsGlobalWindow::ClearDocumentDependentSlots": "OOM",
  },
};

def fsGetSpecialExceptionTypeId(sTypeId, oFrame):
  dsFunctionName_sSpecialTypeId = ddsFunctionName_sSpecialTypeId_sTypeId.get(sTypeId, {});
  return (
    dsFunctionName_sSpecialTypeId.get(oFrame.sAddress)
    or dsFunctionName_sSpecialTypeId.get(oFrame.sSimplifiedAddress)
  );
