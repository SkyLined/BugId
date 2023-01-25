from dxConfig import dxConfig;
from foConsoleLoader import foConsoleLoader;
from mColorsAndChars import *;
oConsole = foConsoleLoader();

def fbApplyConfigSetting(sSettingName, xValue, sIndentation): # sIndentation is None means no output!
  asGroupNames = sSettingName.split("."); # last element is not a group name
  sFullName = ".".join(asGroupNames);
  sSettingName = asGroupNames.pop();          # so pop it.
  dxConfigGroup = dxConfig;
  asHandledGroupNames = [];
  for sGroupName in asGroupNames:
    asHandledGroupNames.append(sGroupName);
    if sGroupName not in dxConfigGroup:
      oConsole.fOutput(
        COLOR_ERROR, "Unknown config group ",
        COLOR_INFO, ".".join(asHandledGroupNames),
        COLOR_ERROR, " in setting name ",
        COLOR_INFO, sFullName,
        COLOR_ERROR, ".",
      );
      return False;
    dxConfigGroup = dxConfigGroup.get(sGroupName, {});
  if sSettingName not in dxConfigGroup:
    if len(asHandledGroupNames) > 0:
      oConsole.fOutput(
        COLOR_ERROR, "Unknown setting name ",
        COLOR_INFO, sSettingName,
        COLOR_ERROR, " in config group ",
        COLOR_INFO, ".".join(asHandledGroupNames),
        COLOR_ERROR, ".",
      );
    else:
      oConsole.fOutput(
        COLOR_ERROR, "Unknown setting name ",
        COLOR_INFO, sSettingName,
        COLOR_ERROR, ".",
      );
    return False;
  if repr(dxConfigGroup[sSettingName]) == repr(xValue):
    if sIndentation is not None:
      oConsole.fOutput(sIndentation, "* The default value for config setting ", COLOR_HILITE, sFullName, COLOR_NORMAL, \
          " is ", COLOR_INFO, repr(dxConfigGroup[sSettingName]), COLOR_NORMAL, ".");
  else:
    if sIndentation is not None:
      oConsole.fOutput(sIndentation, "+ Changed config setting ", COLOR_HILITE, sFullName, COLOR_NORMAL, \
          " from ", COLOR_HILITE, repr(dxConfigGroup[sSettingName]), COLOR_NORMAL, " to ", COLOR_INFO, repr(xValue), COLOR_NORMAL, ".");
    dxConfigGroup[sSettingName] = xValue;
  return True;
