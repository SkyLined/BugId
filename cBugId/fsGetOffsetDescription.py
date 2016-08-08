from fsGetNumberDescription import fsGetNumberDescription;

def fsGetOffsetDescription(iOffset):
  sSign = iOffset < 0 and "-" or "+";
  uOffset = abs(iOffset);
  # One bug may result in different offsets for 32-bit and 64-bit versions of an application, so using the exact
  # value of the offset may result in different ids on different platforms. This can be disabled by setting a value
  # for uMaxOffsetMultiplier:
  sOffset = fsGetNumberDescription(uOffset, sSign);
  return sOffset and "%s%s" % (sSign, sOffset) or "";

