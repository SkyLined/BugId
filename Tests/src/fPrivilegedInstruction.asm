IFDEF x86
  .586
  .model flat, stdcall
ENDIF
option casemap :none   

.code

fPrivilegedInstruction PROC
  CLI
fPrivilegedInstruction ENDP

END