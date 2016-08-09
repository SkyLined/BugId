import os, re;
from dxBugIdConfig import dxBugIdConfig;

def cCdbWrapper_fasGetStack(oCdbWrapper, sGetStackCommand):
  asSymbolLoadStackOutput = None;
  asLastSymbolReloadOutput = None;
  # Get the stack, which should make sure all relevant symbols are loaded or at least marked as requiring loading.
  # Noisy symbol loading is turned on during the command, so there will be symbol loading debug messages in between
  # the stack output, which makes the stack hard to parse: it is therefore discarded and the command is executed
  # again later (without noisy symbol loading) when symbols ae loaded.
  asSymbolLoadStackOutput = oCdbWrapper.fasSendCommandAndReadOutput( \
      ".symopt+ 0x80000000;%s;.symopt- 0x80000000; $$ Get stack with debug symbols enabled" % sGetStackCommand);
  if not oCdbWrapper.bCdbRunning: return None;
  if dxBugIdConfig["uMaxSymbolLoadingRetries"] > 0:
    # Try to reload all modules and symbols. The symbol loader will not reload all symbols, but only those symbols that
    # were loaded before or those it attempted to load before, but failed. The symbol loader will output all kinds of
    # cruft, which may contain information about PDB files that cannot be loaded (e.g. corrupt files). If any such
    # issues are detected, these PDB files are deleted and the code loops, so the symbol loader can download them
    # again and any further issues can be detected and fixed. The code loops until there are no more issues that can be
    # fixed, or it has run ten times.
    # This step may also provide some help debugging symbol loading problems that cannot be fixed automatically.
    for x in xrange(dxBugIdConfig["uMaxSymbolLoadingRetries"]):
      # Reload all modules with noisy symbol loading on to detect any errors. These errors are automatically detected
      # and handled in cCdbOutput.fHandleCommonErrorsInOutput, so all we have to do is check if any errors were found
      # and try again to see if they have been fixed.
      asLastSymbolReloadOutput = oCdbWrapper.fasSendCommandAndReadOutput( \
          ".symopt+ 0x80000000;.reload /v;.symopt- 0x80000000; $$ Reload symbols for all modules");
      if not oCdbWrapper.bCdbRunning: return None;
      bErrorsDuringLoading = False;
      for sLine in asLastSymbolReloadOutput:
        # If there were any errors, make sure we try loading again.
        if re.match(r"^%s\s*$" % "|".join([
          r"DBGHELP: (.*?) (\- E_PDB_CORRUPT|dia error 0x[0-9a-f]+)",
          r"\*\*\* ERROR: .+",
        ]), sLine):
          break;
          # Found an error, stop this loop and try again.
      else:
        # Loop completed: no errors found, stop reloading modules.
        break;
  # Get the stack for real. At this point, no output from symbol loader is expected or handled.
  asStackOutput = oCdbWrapper.fasSendCommandAndReadOutput(
    "%s; $$ Get stack" % sGetStackCommand,
    bOutputIsInformative = True,
  );
  if not oCdbWrapper.bCdbRunning: return None;
  # Remove checksum warning, if any.
  if re.match(r"^\*\*\* WARNING: Unable to verify checksum for .*$", asStackOutput[0]):
    asStackOutput.pop(0);
  assert asStackOutput, "CDB did not return any stack information for command %s" % repr(sGetStackCommand);
  # Getting the stack twice does not always work: for unknown reasons the second time the stack may be truncated or
  # incorrect. So, if an error in symbol loading is detected while getting the stack, there is no reliable way to try
  # to reload the symbols and get the stack again: we must throw an exception.
  assert not re.match(r"^\*\*\* ERROR: Module load completed but symbols could not be loaded for .+$", asStackOutput[0]), \
      "CDB failed to load symbols:\r\n%s%s%s" % (
        "\r\n".join(["  %s" % s for s in asStackOutput]),
        asSymbolLoadStackOutput is not None and ("\r\nasSymbolLoadStackOutput:\r\n%s" % "\r\n".join(["  %s" % s for s in asSymbolLoadStackOutput])) or "",
        asLastSymbolReloadOutput is not None and ("\r\nasLastSymbolReloadOutput:\r\n%s" % "\r\n".join(["  %s" % s for s in asLastSymbolReloadOutput])) or "",
      );
  return asStackOutput;
