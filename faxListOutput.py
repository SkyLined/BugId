from mColors import *;

def faxListOutput(asData, sAndOr, uDataColor = INFO, uNormalColor = NORMAL):
  if len(asData) == 1:
    asOutput = [uDataColor, asData[0], uNormalColor];
  elif len(asData) == 2:
    asOutput = [uDataColor, asData[0], uNormalColor, " %s " % sAndOr, uDataColor, asData[1], uNormalColor];
  else:
    asOutput = [];
    for sData in asData[:-1]:
      asOutput += [uDataColor, sData, uNormalColor, ", "];
    asOutput += ["and ", uDataColor, asData[-1], uNormalColor];
  return asOutput;
