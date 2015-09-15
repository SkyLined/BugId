IFDEF x86
  .586
  .model flat, stdcall
ENDIF
option casemap :none   

.code

fIllegalInstruction PROC
  db 0FFH, 0FFH
fIllegalInstruction ENDP

END