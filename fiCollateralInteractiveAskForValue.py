from mNotProvided import fAssertTypes;

from foConsoleLoader import foConsoleLoader;
from mColorsAndChars import *;
oConsole = foConsoleLoader();

def fiCollateralInteractiveAskForValue(uProcessId, uThreadId, sInstruction, a0txRegisters, sDestination, i0CurrentValue, u0OriginalValue, iMinValue, iMaxValue, iSuggestedValue):
  fAssertTypes({
    "uProcessId": (uProcessId, int),
    "uThreadId": (uThreadId, int),
    "sInstruction": (sInstruction, str),
    "a0txRegisters": (a0txRegisters, [tuple], None),
    "sDestination": (sDestination, str),
    "i0CurrentValue": (i0CurrentValue, int, None),
    "u0OriginalValue": (u0OriginalValue, int, None),
    "iMinValue": (iMinValue, int),
    "iMaxValue": (iMaxValue, int),
    "iSuggestedValue": (iSuggestedValue, int),
  });
  
  def fsValueToString(iValue):
    return ("-" if iValue < 0 else "") + ("0x%X" % abs(iValue));
  
  oConsole.fOutput(
    COLOR_NORMAL, "  The exception happened in process ",
    COLOR_INFO, "%d" % uProcessId,
    COLOR_NORMAL, "/",
    COLOR_INFO, "0x%X" % uProcessId,
    COLOR_NORMAL, ", thread ",
    COLOR_INFO, "%d" % uThreadId,
    COLOR_NORMAL, "/",
    COLOR_INFO, "0x%X" % uThreadId,
    COLOR_NORMAL, ".",
  );
  if a0txRegisters is None:
    oConsole.fOutput(
      COLOR_NORMAL, "  The values of the register at the time of the exception could not be determined.",
    );
  else:
    oConsole.fOutput(
      COLOR_NORMAL, "  Register values at the time of the exception:"
    );
    for (sbRegisterName, uRegisterValue, uBitSize, s0Details) in a0txRegisters:
      sRegisterValueHex = "%X" % uRegisterValue;
      oConsole.fOutput(
        COLOR_NORMAL, "    ",
        COLOR_INFO, str(sbRegisterName, "ascii", "strict").ljust(6),
        COLOR_NORMAL, " = ",
        COLOR_DIM, "0" * ((uBitSize >> 2) - len(sRegisterValueHex)),
        COLOR_INFO, sRegisterValueHex,
        [] if s0Details is None else [
          COLOR_NORMAL, " => ",
          COLOR_INFO, s0Details,
        ],
      );
  oConsole.fOutput(
    COLOR_NORMAL, "  The instruction that triggered the exception:"
  );
  oConsole.fOutput(
    COLOR_NORMAL, "  ",
    COLOR_INFO, sInstruction,
  );
  oConsole.fOutput(
    COLOR_INFO, CHAR_INFO,
    COLOR_NORMAL, " This bug can be ignore by skipping over the instruction that caused the exception.",
  );
  oConsole.fOutput(
    COLOR_NORMAL, "  In order to do this, you must provide a value for ",
    COLOR_INFO, sDestination,
    [
      COLOR_NORMAL, " (current value: ",
      COLOR_INFO, fsValueToString(i0CurrentValue),
      COLOR_NORMAL, ")",
    ] if i0CurrentValue is not None else [],
    ".",
  );
  if u0OriginalValue is not None:
    iDefaultValue = u0OriginalValue;
    oConsole.fOutput(
      COLOR_NORMAL, "  It would be set to ",
      COLOR_INFO, fsValueToString(u0OriginalValue),
      COLOR_NORMAL, " if the instruction had succeeded (the default), but you can set it to ",
      COLOR_INFO, fsValueToString(iSuggestedValue),
      COLOR_NORMAL, " to poison the value.",
    );
  else:
    iDefaultValue = iSuggestedValue;
    oConsole.fOutput(
      COLOR_NORMAL, "  It is suggested you set it to ",
      COLOR_INFO, fsValueToString(iSuggestedValue),
      COLOR_NORMAL, " to poison the value (the default).",
    );
  oConsole.fOutput(
    COLOR_NORMAL, "  The value must be between ",
    COLOR_INFO, fsValueToString(iMinValue),
    COLOR_NORMAL, " and ",
    COLOR_INFO, fsValueToString(iMaxValue),
    COLOR_NORMAL, ".",
  );
  while 1:
    # Loop until the user accepts the suggested value, or enters a valid value.
    oConsole.fStatus(
      COLOR_NORMAL, "  ",
      COLOR_INFO, sDestination,
      COLOR_NORMAL, " (", fsValueToString(iDefaultValue), ") > ",
    );
    sValue = input().strip();
    if sValue == "":
      return iDefaultValue;
    iSignMultiplier = -1 if sValue[0] == "-" else 1;
    sValue = sValue.lstrip("-");
    try:
      if sValue.lower().startswith("0x"):
        uValue = int(sValue[2:], 16);
      else:
        uValue = int(sValue);
    except ValueError:
      oConsole.fOutput(
        COLOR_NORMAL, "  ",
        COLOR_ERROR, CHAR_ERROR,
        COLOR_NORMAL, " That is not a valid value!",
      );
    else:
      iValue = iSignMultiplier * uValue;
      if iMinValue <= iValue <= iMaxValue:
        return iValue;
      oConsole.fOutput(
        COLOR_NORMAL, "  ",
        COLOR_ERROR, CHAR_ERROR,
        COLOR_NORMAL, " That value is outside the valid range!",
      );
