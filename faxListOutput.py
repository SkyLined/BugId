from mColorsAndChars import \
  COLOR_DIM, \
  COLOR_INFO, \
  COLOR_NORMAL;

def faxListOutput(
  asData,
  sAndOr,
  a0sImportantData = None,
  uImportantDataColor = COLOR_INFO,
  uNonImportantDataColor = COLOR_DIM,
  uNormalColor = COLOR_NORMAL, \
):
  asData = [str(x) for x in asData];
  asImportantData = (
    a0sImportantData if a0sImportantData is not None
    else asData
  );

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
