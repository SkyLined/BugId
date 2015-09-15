IFDEF x86
  .586
  .model flat, stdcall
ENDIF
option casemap :none   

.code

fIntegerOverflow PROC
  MOV   EAX, 80000000H
  CDQ
  IDIV  EDX
fIntegerOverflow ENDP

END