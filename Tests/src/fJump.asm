IFDEF x86
  .586
  .model flat, stdcall
ENDIF
option casemap :none   

.code

fJump PROC, pAddress:PTR VOID
  IFDEF x86
    JMP pAddress
  ELSE
    JMP RCX ; this may be stdcall, but VS insists on calling it as fastcall
  ENDIF
  RET
fJump ENDP

END