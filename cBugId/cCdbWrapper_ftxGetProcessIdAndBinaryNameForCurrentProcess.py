import os, re;

def cCdbWrapper_ftxGetProcessIdAndBinaryNameForCurrentProcess(oCdbWrapper):
  # Gather process id and binary name for the current process.
  asProcessesOutput = oCdbWrapper.fasSendCommandAndReadOutput("|.; $$ Get current process");
  if not oCdbWrapper.bCdbRunning: return None, None;
  #Output:
  # |.  2 id:  e44 child   name: chrome.exe
  # |.  1 id:  28c child   name: iexplore.exe
  # |.  4 id:  c74 exited  name: chrome.exe
  oMatch = len(asProcessesOutput) == 1 and re.match(r"^\s*%s\s*$" % (
    r"\.\s+"                # "." whitespace
    r"\d+"                  # cdb_process_number
    r"\s+id:\s+"            # whitespace "id:" whitespace
    r"([0-9a-f]+)"          # (pid)
    r"\s+\w+\s+name:\s+"    # whitespace {"create" || "child"} whitespace "name:" whitespace
    r"(.*?)"                # (binary_name)
  ), asProcessesOutput[0]);
  assert oMatch, "Unexpected current process output:\r\n%s" % "\r\n".join(asProcessesOutput);
  sProcessId, sBinaryNameOrPath = oMatch.groups();
  uProcessId = int(sProcessId, 16);
  if sBinaryNameOrPath == "?NoImage?":
    # No idea why this happens, but apparently it does...
    sBinaryName = None;
  else:
    sBinaryName = os.path.basename(sBinaryNameOrPath);
  return (uProcessId, sBinaryName);
