IFDEF x86
  .586
  .model flat, stdcall
ENDIF
option casemap :none   

.code

fCall PROC pAddress:PTR VOID
  IFDEF x86
    CALL pAddress
  ELSE
    CALL RCX ; this may be stdcall, but VS insists on calling it as fastcall
  ENDIF
  RET
fCall ENDP

END