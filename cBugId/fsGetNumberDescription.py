from dxBugIdConfig import dxBugIdConfig;

def fsGetNumberDescription(uNumber, sSign = "+"):
  if uNumber == 0:
    return "";
  uArchitectureIndependentBugIdBytes = dxBugIdConfig["uArchitectureIndependentBugIdBits"] / 8;
  if uArchitectureIndependentBugIdBytes == 0 or uNumber < uArchitectureIndependentBugIdBytes:
    # Architecture independent bug ids are disabled, or the number is too small to require fixing.
    if uNumber < 10:
      return "%d" % uNumber;
    return "0x%X" % uNumber;
  uRemainder = uNumber % uArchitectureIndependentBugIdBytes;
  sRemainder = uRemainder and sSign + fsGetNumberDescription(uRemainder) or "";
  return "%d*N%s" % (uArchitectureIndependentBugIdBytes, sRemainder);
