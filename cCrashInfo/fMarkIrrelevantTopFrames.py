# "*" is applied to all exceptions.
# Exception codes and exception type ids can be used
# Frame addresses and simplified addresses can be used
from NTSTATUS import *;

dasIrrelevantTopFrameFunctions_xExceptionCodeOrTypeId = {
  "*": [
    "KERNELBASE!RaiseException",
    "ntdll.dll!KiUserExceptionDispatch",
    "ntdll.dll!NtRaiseException",
    "ntdll.dll!RtlDispatchException",
    "ntdll.dll!RtlpExecuteHandlerForException",
    "ntdll.dll!ZwRaiseException",
  ],
  STATUS_ACCESS_VIOLATION: [
    "chrome_child.dll!memcpy",
  ],
  STATUS_FAIL_FAST_EXCEPTION: [
    "EDGEHTML.dll!Abandonment::InduceAbandonment",
    "EDGEHTML.dll!Abandonment::OutOfMemory",
  ],
  STATUS_STACK_BUFFER_OVERRUN: [
    "ntdll.dll!KiUserExceptionDispatcher",
    "ntdll.dll!LdrpValidateUserCallTarget",
    "ntdll.dll!LdrpValidateUserCallTargetBitMapCheck",
    "ntdll.dll!LdrpValidateUserCallTargetBitMapRet",
    "ntdll.dll!LdrpValidateUserCallTargetEH",
    "ntdll.dll!RtlFailFast2",
    "ntdll.dll!RtlpHandleInvalidUserCallTarget",
  ],
  CPP_EXCEPTION_CODE: [
    "KERNELBASE.dll!RaiseException",
    "msvcrt.dll!CxxThrowException",
    "msvcrt.dll!_CxxThrowException",
    "MSVCR110.dll!CxxThrowException",
    "MSVCR110.dll!_CxxThrowException",
  ],
  "Breakpoint": [
    "kernel32.dll!DebugBreak",
    "ntdll.dll!DbgBreakPoint",
  ],
  "FatalError": [
    "chrome_child.dll!blink::reportFatalErrorInMainThread",
    "chrome_child.dll!v8::Utils::ReportApiFailure",
  ],
  "OOM": [
    "chrome.dll!`anonymous namespace'::call_new_handler",
    "chrome.dll!`anonymous namespace'::generic_cpp_alloc",
    "chrome.dll!malloc",
    "chrome.dll!operator new[]",
    "chrome.dll!realloc",
    "chrome.dll!std::_Allocate",
    "chrome.dll!std::allocator<...>::allocate",
    "chrome_child.dll!blink::PurgeableVector::append",
    "chrome_child.dll!blink::RawResource::appendData",
    "chrome_child.dll!blink::Resource::appendData",
    "chrome_child.dll!blink::SharedBuffer::append",
    "chrome_child.dll!blink::SharedBuffer::SharedBuffer",
    "chrome_child.dll!v8::internal::Heap::FatalProcessOutOfMemory",
    "chrome_child.dll!WTF::ArrayBuffer::create",
    "chrome_child.dll!WTF::DefaultAllocator::allocateBacking",
    "chrome_child.dll!WTF::DefaultAllocator::allocateZeroedHashTableBacking<...>",
    "chrome_child.dll!WTF::fastMalloc",
    "chrome_child.dll!WTF::HashTable<...>::add<...>",
    "chrome_child.dll!WTF::HashTable<...>::allocateTable",
    "chrome_child.dll!WTF::HashTable<...>::expand",
    "chrome_child.dll!WTF::HashTable<...>::rehash",
    "chrome_child.dll!WTF::partitionAlloc",
    "chrome_child.dll!WTF::partitionAllocGeneric",
    "chrome_child.dll!WTF::partitionAllocGenericFlags",
    "chrome_child.dll!WTF::partitionAllocSlowPath",
    "chrome_child.dll!WTF::partitionBucketAlloc",
    "chrome_child.dll!WTF::partitionOutOfMemory",
    "chrome_child.dll!WTF::partitionReallocGeneric",
    "chrome_child.dll!WTF::Partitions::bufferMalloc",
    "chrome_child.dll!WTF::String::utf8",
    "chrome_child.dll!WTF::StringBuilder::append",
    "chrome_child.dll!WTF::StringBuilder::appendUninitializedSlow<...>",
    "chrome_child.dll!WTF::StringBuilder::reallocateBuffer<...>",
    "chrome_child.dll!WTF::StringImpl::operator new",
    "chrome_child.dll!WTF::StringImpl::reallocate",
    "chrome_child.dll!WTF::Vector<...>::appendSlowCase<...>",
    "chrome_child.dll!WTF::Vector<...>::expandCapacity",
    "chrome_child.dll!WTF::Vector<...>::extendCapacity",
    "chrome_child.dll!WTF::Vector<...>::reserveCapacity",
    "chrome_child.dll!WTF::Vector<...>::Vector<...>",
    "chrome_child.dll!WTF::VectorBuffer<...>::VectorBuffer<...>",
    "chrome_child.dll!WTF::VectorBuffer<...>::allocateExpandedBuffer",
    "chrome_child.dll!WTF::VectorBufferBase<...>::allocateBuffer",
    "mozglue.dll!moz_xcalloc",
    "mozglue.dll!moz_xmalloc",
    "mozglue.dll!moz_xrealloc",
    "mozglue.dll!mozalloc_abort",
    "mozglue.dll!mozalloc_handle_oom",
    "xul.dll!js::CrashAtUnhandlableOOM",
    "xul.dll!js::MallocProvider<...>",
    "xul.dll!mozilla::CircularByteBuffer::SetCapacity",
    "xul.dll!NS_ABORT_OOM",
    "xul.dll!nsACString_internal::AppendFunc",
    "xul.dll!nsBaseHashtable<...>::Put",
    "xul.dll!nsBaseHashtable::Put",
    "xul.dll!nsGlobalWindow::ClearDocumentDependentSlots",
    "xul.dll!nsPresArena::Allocate",
    "xul.dll!nsTArray_base<...>::EnsureCapacity",
    "xul.dll!nsTArray_Impl<...>::AppendElements",
    "xul.dll!nsTArray_Impl<...>::AppendElement<...>",
    "xul.dll!StatsCompartmentCallback",
    "xul.dll!std::_Allocate<char>",
    "xul.dll!std::basic_string<...>::_Copy",
    "xul.dll!std::basic_string<...>::assign",
    "xul.dll!std::vector<...>::_Reallocate",
    "xul.dll!std::vector<...>::_Reserve",
  ],
  "AVE:NULL": [
    "0x0",
  ],
};

def fMarkIrrelevantTopFrames(oErrorReport, uExceptionCode, oStack):
  asIrrelevantTopFrameFunctions = (
    dasIrrelevantTopFrameFunctions_xExceptionCodeOrTypeId.get("*", []) +
    dasIrrelevantTopFrameFunctions_xExceptionCodeOrTypeId.get(oErrorReport.sExceptionTypeId, []) +
    dasIrrelevantTopFrameFunctions_xExceptionCodeOrTypeId.get(uExceptionCode, [])
  );
  # For each frame
  for oFrame in oStack.aoFrames:
    # if it's not marked as irrelevant yet:
    if not oFrame.bIsIrrelevant:
      # go through all irrelevant top frame functions:
      for sIrrelevantTopFrameFunction in asIrrelevantTopFrameFunctions:
        # and see if one of them is a match:
        if sIrrelevantTopFrameFunction in (oFrame.sAddress, oFrame.sSimplifiedAddress):
          oFrame.bIsIrrelevant = True;
          # yes!, go to the next frame
          break;
      else:
        # no match found: this is not irrelevant
        return;