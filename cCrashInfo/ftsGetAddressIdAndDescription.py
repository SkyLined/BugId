from dxCrashInfoConfig import dxCrashInfoConfig;

dsId_uAddress = {     # Short             # This message is inserted into "Attemp to [read|write|execute] memory at 0x### (%s)"
          0x00000000: ('NULL',            "a NULL ptr"),
          0xBBADBEEF: ('assertion',       "used to indicate an assertion has failed"),
          0xBAADF00D: ('uninitialized',   "a pointer was used before it was initialized"),
  0xBAADF00DBAADF00D: ('uninitialized',   "a pointer was used before it was initialized"),
          0xCCCCCCCC: ('uninitialized',   "a pointer was used before it was initialized"),
  0xCCCCCCCCCCCCCCCC: ('uninitialized',   "a pointer was used before it was initialized"),
          0xC0C0C0C0: ('uninitialized',   "a pointer was used before it was initialized"),
  0xC0C0C0C0C0C0C0C0: ('uninitialized',   "a pointer was used before it was initialized"),
          0xCDCDCDCD: ('uninitialized',   "a pointer was used before it was initialized"),
  0xCDCDCDCDCDCDCDCD: ('uninitialized',   "a pointer was used before it was initialized"),
          0xD0D0D0D0: ('uninitialized',   "a pointer was used before it was initialized"),
  0xD0D0D0D0D0D0D0D0: ('uninitialized',   "a pointer was used before it was initialized"),
          0xDDDDDDDD: ('free',            "a pointer was used after it was freed"),
  0xDDDDDDDDDDDDDDDD: ('free',            "a pointer was used after it was freed"),
          0xF0F0F0F0: ('free',            "a pointer was used after it was freed"),
  0xF0F0F0F0F0F0F0F0: ('free',            "a pointer was used after it was freed"),
          0xFDFDFDFD: ('canary',          "a pointer was used from an out-of-bounds memory canary"),
  0xF0DE7FFFF0DE7FFF: ('poison',          "a poisoned pointer was used"),
          0xF0DE7FFF: ('poison',          "a poisoned pointer was used"),
  0xF0090100F0090100: ('poison',          "a poisoned pointer was used"),
          0xF0090100: ('poison',          "a poisoned pointer was used"),
  0xFEEEFEEEFEEEFEEE: ('free',            "a pointer was used after it was freed"),
          0xFEEEFEEE: ('free',            "a pointer was used after it was freed"),
};

def ftsGetAddressIdAndDescription(uAddress):
  for (uBaseAddress, (sId, sDescription)) in dsId_uAddress.items():
    iOffset = uAddress - uBaseAddress;
    if iOffset == 0:
      return sId;
    uMaxAddressOffset = dxCrashInfoConfig.get("uMaxAddressOffset", 0xFFF);
    if iOffset > uMaxAddressOffset: # Maybe this is wrapping:
      iOffset -= 0x100000000;
    elif iOffset < -uMaxAddressOffset: # Maybe this is wrapping:
      iOffset += 0x100000000;
    uOffset = abs(iOffset);
    if uOffset < uMaxAddressOffset:
      return "%s%s0x%X" % (sId, iOffset < 0 and "-" or "+", uOffset), sDescription;
  return "Arbitrary", "an invalid pointer was used";

if __name__ == "__main__":
  for uAddress in dsId_uAddress.keys():
    for uOffset in [0x100000004, 0, 4]:
      sId, sDescription = ftsGetAddressIdAndDescription(uAddress);
      print "%16X: %s" % (0xFFFFFFFF & (uAddress + uOffset), sId, sDescription);