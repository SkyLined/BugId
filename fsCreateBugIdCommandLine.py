import __main__, sys;

from fsAddQuotesAndEscapesIfNeededInCommandLine import fsAddQuotesAndEscapesIfNeededInCommandLine;

gsPythonExecutableFilePath = sys.executable;
gsBugIdMainScriptFilePath = __main__.__file__;

def fsCreateBugIdCommandLine(asArguments = []):
  return " ".join([
    fsAddQuotesAndEscapesIfNeededInCommandLine(s) for s in (
      [
        gsPythonExecutableFilePath,
        gsBugIdMainScriptFilePath,
      ] + 
      asArguments
    )
  ]);
