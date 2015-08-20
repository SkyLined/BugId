# "*" is applied to all exceptions.
# Exception codes and exception type ids can be used
# Frame addresses and simplified addresses can be used
from NTSTATUS import *;

dasIrrelevantTopFrameFunctions_xExceptionCodeOrTypeId = {
  "*": [
    "ntdll.dll!KiUserExceptionDispatch",
    "ntdll.dll!NtRaiseException",
    "ntdll.dll!RtlDispatchException",
    "ntdll.dll!RtlpExecuteHandlerForException",
    "ntdll.dll!ZwRaiseException",
  ],
  STATUS_ACCESS_VIOLATION: [ # All Access Violations
    "chrome_child.dll!memcpy",
  ],
  STATUS_STACK_BUFFER_OVERRUN: [ # All FailFast exceptions
    "ntdll.dll!RtlFailFast2",
    "ntdll.dll!RtlpHandleInvalidUserCallTarget",
    "ntdll.dll!RtlDispatchException",
    "ntdll.dll!KiUserExceptionDispatcher",
    "ntdll.dll!LdrpValidateUserCallTargetBitMapCheck",
  ],
  "Breakpoint": [
    "kernel32.dll!DebugBreak",
    "ntdll.dll!DbgBreakPoint",
  ],
  "C++": [
    "KERNELBASE.dll!RaiseException",
    "msvcrt.dll!CxxThrowException",
  ],
  "FatalError": [
    "chrome_child.dll!blink::reportFatalErrorInMainThread",
    "chrome_child.dll!v8::Utils::ReportApiFailure",
  ],
  "OOM": [
    "chrome_child.dll!blink::PurgeableVector::append",
    "chrome_child.dll!blink::RawResource::appendData",
    "chrome_child.dll!blink::Resource::appendData",
    "chrome_child.dll!blink::SharedBuffer::append",
    "chrome_child.dll!blink::SharedBuffer::SharedBuffer",
    "chrome_child.dll!WTF::DefaultAllocator::allocateBacking",
    "chrome_child.dll!WTF::DefaultAllocator::allocateZeroedHashTableBacking<...>",
    "chrome_child.dll!WTF::fastMalloc",
    "chrome_child.dll!WTF::HashTable<...>::add<...>",
    "chrome_child.dll!WTF::HashTable<...>::allocateTable",
    "chrome_child.dll!WTF::HashTable<...>::expand",
    "chrome_child.dll!WTF::HashTable<...>::rehash",
    "chrome_child.dll!WTF::partitionAllocSlowPath",
    "chrome_child.dll!WTF::partitionOutOfMemory",
    "chrome_child.dll!WTF::partitionReallocGeneric",
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
    "mozalloc.dll!moz_xmalloc",
    "mozalloc.dll!moz_xrealloc",
    "mozalloc.dll!mozalloc_abort",
    "mozalloc.dll!mozalloc_handle_oom",
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
  "AVE@NULL": [
    "0x0",
  ],
  "SecurityCheck": [
    "ntdll.dll!LdrpValidateUserCallTarget",
    "ntdll.dll!LdrpValidateUserCallTargetBitMapCheck",
    "ntdll.dll!LdrpValidateUserCallTargetBitMapRet",
    "ntdll.dll!LdrpValidateUserCallTargetEH",
    "ntdll.dll!RtlpHandleInvalidUserCallTarget",
    "ntdll.dll!KiUserExceptionDispatcher",
  ],
};

def fbIsIrrelevantTopFrame(sExceptionTypeId, uExceptionCode, oFrame):
  def fbIsIrrelevantAddress(sAddress):
    return (
      sAddress in dasIrrelevantTopFrameFunctions_xExceptionCodeOrTypeId.get("*", [])
      or sAddress in dasIrrelevantTopFrameFunctions_xExceptionCodeOrTypeId.get(sExceptionTypeId, [])
      or sAddress in dasIrrelevantTopFrameFunctions_xExceptionCodeOrTypeId.get(uExceptionCode, [])
    );
  return (
    fbIsIrrelevantAddress(oFrame.sAddress)
    or fbIsIrrelevantAddress(oFrame.sSimplifiedAddress)
  );
