import json;

from mConsole import oConsole;

from dxConfig import dxConfig;
from mColors import *;

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
        ERROR, "Unknown config group ",
        ERROR_INFO, ".".join(asHandledGroupNames),
        ERROR, " in setting name ",
        ERROR_INFO, sFullName,
        ERROR, ".",
      );
      return False;
    dxConfigGroup = dxConfigGroup.get(sGroupName, {});
  if sSettingName not in dxConfigGroup:
    if len(asHandledGroupNames) > 0:
      oConsole.fOutput(
        ERROR, "Unknown setting name ",
        ERROR_INFO, sSettingName,
        ERROR, " in config group ",
        ERROR_INFO, ".".join(asHandledGroupNames),
        ERROR, ".",
      );
    else:
      oConsole.fOutput(
        ERROR, "Unknown setting name ",
        ERROR_INFO, sSettingName,
        ERROR, ".",
      );
    return False;
  if json.dumps(dxConfigGroup[sSettingName]) == json.dumps(xValue):
    if sIndentation is not None:
      oConsole.fOutput(sIndentation, "* The default value for config setting ", HILITE, sFullName, NORMAL, \
          " is ", json.dumps(dxConfigGroup[sSettingName]), ".");
  else:
    if sIndentation is not None:
      oConsole.fOutput(sIndentation, "+ Changed config setting ", HILITE, sFullName, NORMAL, \
          " from ", HILITE, repr(dxConfigGroup[sSettingName]), NORMAL, " to ", INFO, repr(xValue), NORMAL, ".");
    dxConfigGroup[sSettingName] = xValue;
  return True;
