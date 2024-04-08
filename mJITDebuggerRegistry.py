sCommandLineHiveName = "HKLM";
ddsCommandLineKeyPath_by_sTargetBinaryISA_by_sOSISA = {
  "x64": {
    # Two different registry paths must be adjusted individually on x64 systems - one for 64-bit applications, and a different one for 32-bit 
    # applications, as outlined in https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/enabling-postmortem-debugging
    "x64": r"Software\Microsoft\Windows NT\CurrentVersion\AEDebug",
    "x86": r"SOFTWARE\WOW6432Node\Microsoft\Windows NT\CurrentVersion\AeDebug",
  },
  "x86": {
    "x86": r"Software\Microsoft\Windows NT\CurrentVersion\AEDebug",
  },
};
