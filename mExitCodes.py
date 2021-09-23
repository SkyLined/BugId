# Running this script will return an exit code, which are defined here:
# These are for errors that most of my scripts could have:
guExitCodeSuccess                        = 0;
guExitCodeInternalError                  = 1;
guExitCodeBadArgument                    = 2;
guExitCodeBadDependencyError             = 3;
guExitCodeLicenseError                   = 4;
guExitCodeCannotReadFromFileSystem       = 5;
guExitCodeCannotWriteToFileSystem        = 6;
guExitCodeTerminatedByUser               = 7;
# These are specific to this particular script:
guExitCodeApplicationBinaryNotFound      = 10;
guExitCodeNoBugsDetected                 = 11;
