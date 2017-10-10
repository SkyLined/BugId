import os, sys;

sModuleFolderPath = os.path.dirname(os.path.abspath(__file__));
sBaseFolderPath = os.path.dirname(sModuleFolderPath);
sys.path.extend([
  sBaseFolderPath,
  sModuleFolderPath,
  os.path.join(sModuleFolderPath, "modules"),
]);

from mWindowsAPI import *;

if __name__ == "__main__":
  uTestColor = 0x0A; # Bright green
  hStdOut = KERNEL32.GetStdHandle(STD_OUTPUT_HANDLE);
  oConsoleScreenBufferInfo = CONSOLE_SCREEN_BUFFER_INFO();
  assert KERNEL32.GetConsoleScreenBufferInfo(hStdOut, PCONSOLE_SCREEN_BUFFER_INFO(oConsoleScreenBufferInfo)), \
      "GetConsoleScreenBufferInfo(%d, ...) => Error %08X" % \
      (oConsole.hStdOut, KERNEL32.GetLastError());
  uOriginalColor = oConsoleScreenBufferInfo.wAttributes & 0xFF;
  assert KERNEL32.SetConsoleTextAttribute(hStdOut, uTestColor), \
      "meh";
  print "Test successful";
  assert KERNEL32.SetConsoleTextAttribute(hStdOut, uOriginalColor), \
      "meh";
