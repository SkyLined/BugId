@ECHO OFF
DEL "Test reports\*.html" /Q
SET _NT_SYMBOL_PATH=
python Tests.py %*