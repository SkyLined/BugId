import re;

def cCrashInfo_fiEvaluateExpression(oCrashInfo, sExpression):
  asEvaluateExpressionOutput = oCrashInfo._fasSendCommandAndReadOutput("? %s" % sExpression);
  if not oCrashInfo._bCdbRunning: return;
  oEvaluateExpressionOutputMatch = (
    len(asEvaluateExpressionOutput) == 1
    and re.match(r"Evaluate expression: (-?\d+) = ([0-9`a-f]+)\s*$", asEvaluateExpressionOutput[0])
  );
  assert oEvaluateExpressionOutputMatch, \
      "Unknown evaluate expression output:\r\n%s" % "\r\n".join(asEvaluateExpressionOutput);
  sValue, sValueHex = oEvaluateExpressionOutputMatch.groups();
  iValue = long(sValue);
  return iValue;

