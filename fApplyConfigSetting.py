import json;
from mColors import *;
from oConsole import oConsole;

def fApplyConfigSetting(sSettingName, xValue, sIndentation):
  asGroupNames = sSettingName.split("."); # last element is not a group name
  sFullName = ".".join(asGroupNames);
  sSettingName = asGroupNames.pop();          # so pop it.
  dxConfigGroup = dxConfig;
  asHandledGroupNames = [];
  for sGroupName in asGroupNames:
    asHandledGroupNames.append(sGroupName);
    assert sGroupName in dxConfigGroup, \
        "Unknown config group %s in setting name %s." % (repr(".".join(asHandledGroupNames)), repr(sFullName));
    dxConfigGroup = dxConfigGroup.get(sGroupName, {});
  assert sSettingName in dxConfigGroup, \
      "Unknown setting name %s%s." % (sSettingName, \
          len(asHandledGroupNames) > 0 and " in config group %s" % ".".join(asHandledGroupNames) or "");
  if json.dumps(dxConfigGroup[sSettingName]) == json.dumps(xValue):
    if gbVerbose:
      oConsole.fPrint(sIndentation, "* The default value for config setting ", HILITE, sFullName, NORMAL, \
          " is ", json.dumps(dxConfigGroup[sSettingName]), ".");
  else:
    if gbVerbose:
      oConsole.fPrint(sIndentation, "+ Changed config setting ", HILITE, sFullName, NORMAL, \
          " from ", HILITE, repr(dxConfigGroup[sSettingName]), NORMAL, " to ", INFO, repr(xValue), NORMAL, ".");
    dxConfigGroup[sSettingName] = xValue;

