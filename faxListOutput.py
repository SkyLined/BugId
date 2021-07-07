from mColors import *;

def faxListOutput(asData, sAndOr, asImportantData, uImportantDataColor = INFO, uNonImportantDataColor = DIM, uNormalColor = NORMAL):
  def faxColoredData(sData):
    return [uImportantDataColor if sData in asImportantData else uNonImportantDataColor, sData];
  if len(asData) == 1:
    asOutput = [faxColoredData(asData[0]), uNormalColor];
  elif len(asData) == 2:
    asOutput = [faxColoredData(asData[0]), uNormalColor, " %s " % sAndOr, faxColoredData(asData[1]), uNormalColor];
  else:
    asOutput = [];
    for sData in asData[:-1]:
      asOutput += [faxColoredData(sData), uNormalColor, ", "];
    asOutput += ["and ", faxColoredData(asData[-1]), uNormalColor];
  return asOutput;
