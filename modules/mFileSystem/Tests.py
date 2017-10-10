import codecs, os, sys;
sys.stdout = codecs.getwriter("cp437")(sys.stdout, "replace");

sModuleFolderPath = os.path.dirname(os.path.abspath(__file__));
sBaseFolderPath = os.path.dirname(sModuleFolderPath);
sys.path.extend([
  sBaseFolderPath,
  sModuleFolderPath,
  os.path.join(sModuleFolderPath, "modules"),
]);

import FileSystem;

sTempFolderPath = FileSystem.fsPath(os.environ["TEMP"]);
sSpecialChars = 'test[[[\0\r\n"<>\\/?*:|]]]';

sSpecialCharsPath = FileSystem.fsPath(sTempFolderPath, sSpecialChars);

sCWD = os.getcwdu().rstrip("\\");
sCWDDrive, sCWDPath = os.path.splitdrive(sCWD);
print "* Testing fsPath...";
dsPathTests = {
  r".":                   r"\\?\%s" % sCWD,
  r"x":                   r"\\?\%s\x" % sCWD,
  r"x\y":                 r"\\?\%s\x\y" % sCWD,
  r"%sx\y" % sCWDDrive:   r"\\?\%s\x\y" % sCWD,
  r"%s\x\y" % sCWDDrive:  r"\\?\%s\x\y" % sCWDDrive,
  r"x:\y\z":              r"\\?\x:\y\z",
  r"\\?\x:\y\z":          r"\\?\x:\y\z",
  r"\\x\y\z":             r"\\?\UNC\x\y\z",
  r"\\?\UNC\x\y\z":       r"\\?\UNC\x\y\z",
};
for (sInput, sExpectedOutput) in dsPathTests.items():
  sOutput = FileSystem.fsPath(sInput);
  assert sOutput == sExpectedOutput, \
      "fsPath error for %s: got %s, expected %s" % (sInput, sOutput, sExpectedOutput);
  sInput += "\\";
  sOutput = FileSystem.fsPath(sInput);
  assert sOutput == sExpectedOutput, \
      "fsPath error for %s: got %s, expected %s" % (sInput, sOutput, sExpectedOutput);

for bUnicode in [True, False]:
  print "* Testing file operations with special characters in %s mode..." % (bUnicode and "Unicode" or "ASCII"); 
  sTranslatedSpecialChars = FileSystem.fsValidName(sSpecialChars, bUnicode = bUnicode);
  print u"  File/folder name: %s" % sTranslatedSpecialChars;
  sData = "x";

  # Clean old files/folders
  print "  * Cleaning up old files/folders..."; 
  print "    * Checking if old test file exists..."; 
  ebIsFileResult = FileSystem.febIsFile(sTempFolderPath, sTranslatedSpecialChars);
  assert isinstance(ebIsFileResult, bool), "Expected febIsFile result to be a boolean, got %s" % repr(ebIsFileResult);
  if ebIsFileResult:
    print "    * Deleting old test file..."; 
    ebDeleteFileResult = FileSystem.febDeleteFile(sTempFolderPath, sTranslatedSpecialChars);
    assert ebDeleteFileResult is True, "Expected febDeleteFile result to be True, got %s" % repr(ebDeleteFileResult);
  print "    * Checking if old test folder exists..."; 
  ebIsFolderResult = FileSystem.febIsFolder(sTempFolderPath, sTranslatedSpecialChars);
  assert isinstance(ebIsFolderResult, bool), "Expected febIsFolder result to be a boolean, got %s" % repr(ebIsFolderResult);
  if ebIsFolderResult:
    print "    * Deleting old test folder..."; 
    ebDeleteFolderResult = FileSystem.febDeleteFolder(sTempFolderPath, sTranslatedSpecialChars);
    assert ebDeleteFolderResult is True, "Expected febDeleteFolder result to be True, got %s" % repr(ebDeleteFolderResult);

  print "  * Creating file with special characters..."; 
  # Create a file, detect it, read it, move it and delete it.
  eWriteFileResult = FileSystem.feWriteDataToFile(sData, sTempFolderPath, sTranslatedSpecialChars);
  assert eWriteFileResult is None, "Expected feWriteDataToFile result to be None, got %s" % repr(eWriteFileResult);
  print "    * Checking if file with special characters exists..."; 
  ebIsFileResult = FileSystem.febIsFile(sTempFolderPath, sTranslatedSpecialChars);
  assert ebIsFileResult is True, "Expected febIsFile result to be True, got %s" % repr(ebIsFileResult);
  print "    * Checking if 8.3 path for file with special characters can be found..."; 
  s83Path = FileSystem.fs83Path(sTempFolderPath, sTranslatedSpecialChars);
  print "        => %s" % s83Path;
  ebIsFileResult = FileSystem.febIsFile(s83Path);
  assert ebIsFileResult is True, "Expected febIsFile result to be True, got %s" % repr(ebIsFileResult);
  print "    * Reading file with special characters..."; 
  esReadFileResult = FileSystem.fesReadDataFromFile(sTempFolderPath, sTranslatedSpecialChars);
  assert esReadFileResult == sData, "Expected febReadDataFromFile result to be %s, got %s" % (repr(sData), repr(esReadFileResult));
  print "    * Renaming file with special characters..."; 
  eMoveFileResult = FileSystem.feMoveFile([sTempFolderPath, sTranslatedSpecialChars], [sTempFolderPath, "moved"]);
  assert eMoveFileResult is None, "Expected feMoveFile result to be None, got %s" % repr(eMoveFileResult);
  eMoveFileResult = FileSystem.feMoveFile([sTempFolderPath, "Moved"], [sTempFolderPath, sTranslatedSpecialChars]);
  assert eMoveFileResult is None, "Expected feMoveFile result to be None, got %s" % repr(eMoveFileResult);
  print "    * Deleting file with special characters..."; 
  ebDeleteFileResult = FileSystem.febDeleteFile(sTempFolderPath, sTranslatedSpecialChars);
  assert ebDeleteFileResult is True, "Expected febDeleteFile result to be True, got %s" % repr(ebDeleteFileResult);

  print "  * Testing folder operations with special characters...";
  # Create a folder, detect it, create a file in the folder and delete the folder.
  print "    * Creating folder with special characters..."; 
  ebCreateFolderResult = FileSystem.febCreateFolder("x", sTempFolderPath, sTranslatedSpecialChars);
  assert ebCreateFolderResult is True, "Expected febCreateFolder result to be True, got %s" % repr(ebCreateFolderResult);
  print "    * Checking if folder with special characters exists..."; 
  ebIsFolderResult = FileSystem.febIsFolder(sTempFolderPath, sTranslatedSpecialChars);
  assert ebIsFolderResult is True, "Expected febIsFolder result to be True, got %s" % repr(ebIsFolderResult);
  print "    * Creating file with special characters in folder with special characters..."; 
  eWriteFileResult = FileSystem.feWriteDataToFile(sData, sTempFolderPath, sTranslatedSpecialChars, sTranslatedSpecialChars);
  assert eWriteFileResult is None, "Expected feWriteDataToFile result to be None, got %s" % repr(eWriteFileResult);
  print "    * Checking if 8.3 path for file with special characters in folder with special characters can be found..."; 
  s83Path = FileSystem.fs83Path(sTempFolderPath, sTranslatedSpecialChars, sTranslatedSpecialChars);
  print "        => %s" % s83Path;
  ebIsFileResult = FileSystem.febIsFile(s83Path);
  assert ebIsFileResult is True, "Expected febIsFile result to be True, got %s" % repr(ebIsFileResult);
  print "    * Renaming folder with special characters..."; 
  eMoveFolderResult = FileSystem.feMoveFolder([sTempFolderPath, sTranslatedSpecialChars], [sTempFolderPath, "moved"]);
  assert eMoveFolderResult is None, "Expected feMoveFolder result to be None, got %s" % repr(eMoveFolderResult);
  eMoveFolderResult = FileSystem.feMoveFolder([sTempFolderPath, "moved"], [sTempFolderPath, sTranslatedSpecialChars]);
  assert eMoveFolderResult is None, "Expected feMoveFolder result to be None, got %s" % repr(eMoveFolderResult);
  print "    * Deleting folder with special characters containing a file with special characters..."; 
  ebDeleteFolderResult = FileSystem.febDeleteFolder(sTempFolderPath, sTranslatedSpecialChars);
  assert ebDeleteFolderResult is True, "Expected febDeleteFolder result to be True, got %s" % repr(ebDeleteFolderResult);


print "* Checking invalid file name errors...";
eError = FileSystem.fesReadDataFromFile("c:\|", fbRetryOnFailure = lambda: False);
assert isinstance(eError, IOError) and eError.args == (22, r"Invalid file name \\?\c:\|"), \
    "Unexpected result for attempt to read from file \"c:\\|\": %s" % repr(eError);
eError = FileSystem.feWriteDataToFile("", "c:\|", fbRetryOnFailure = lambda: False);
assert isinstance(eError, IOError) and eError.args == (22, r"Invalid file name \\?\c:\|"), \
    "Unexpected result for attempt to write to file \"c:\\|\": %s" % repr(eError);

print "* Checking write invalid (unicode) data...";
try:
  FileSystem.feWriteDataToFile(u"\u1234", sTempFolderPath, "test.txt", fbRetryOnFailure = lambda: False);
except UnicodeEncodeError:
  pass;

print "+ All tests passed."