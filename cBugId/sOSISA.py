import os;
sOSISA = {"AMD64": "x64", "x86": "x86"}[os.getenv("PROCESSOR_ARCHITEW6432") or os.getenv("PROCESSOR_ARCHITECTURE")];
