from dxCrashInfoConfig import dxCrashInfoConfig;

dsId_uAddress = {
  0x00000000: 'NULL',
  0xBBADBEEF: 'assertion',
  0xBAADF00D: 'uninitialized',
  0xCCCCCCCC: 'uninitialized',
  0xC0C0C0C0: 'uninitialized',
  0xCDCDCDCD: 'uninitialized',
  0xD0D0D0D0: 'uninitialized',
  0xDDDDDDDD: 'free',
  0xF0F0F0F0: 'free',
  0xFDFDFDFD: 'canary',
  0xF0DE7FFF: 'poison',
  0xF0090100: 'poison',
  0xFEEEFEEE: 'free',
};

def fsGetAddressId(uAddress):
  for (uBaseAddress, sId) in dsId_uAddress.items():
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
      return "%s%s0x%X" % (sId, iOffset < 0 and "-" or "+", uOffset);
  return "Arbitrary";

if __name__ == "__main__":
  for uAddress in [-1, 0, 1, 0xF0F0F000, 0xD0D0D000]:
    print "%d: %s" % (uAddress, fsGetAddressId(uAddress));