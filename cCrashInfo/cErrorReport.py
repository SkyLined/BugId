import hashlib;
from fsGetSpecialExceptionTypeId import fsGetSpecialExceptionTypeId;
from fbIsIrrelevantTopFrame import fbIsIrrelevantTopFrame;

from dxCrashInfoConfig import dxCrashInfoConfig;

def fsHTMLEncode(sData):
  return sData.replace('&', '&amp;').replace(" ", "&nbsp;").replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;');

class cErrorReport(object):
  def __init__(self, sId, sDescription, sSecurityImpact, sHTMLDetails):
    self.sId = sId;
    self.sDescription = sDescription;
    self.sSecurityImpact = sSecurityImpact;
    self.sHTMLDetails = sHTMLDetails;
  
  @classmethod
  def foCreateFromException(cSelf, oException, asCdbIO):
    # Get initial exception type id and description
    oTopFrame = len(oException.oStack.aoFrames) > 0 and oException.oStack.aoFrames[0] or None;
    # Get application id.
    sApplicationId = oException.oProcess.sBinaryName;
    # See if its in a "special" exception and rewrite the exception type id accordingly.
    if oTopFrame and oTopFrame.oFunction:
      sTypeId = fsGetSpecialExceptionTypeId(oException.sTypeId, oTopFrame) \
                or oException.sTypeId; # in case there is no special type id.
    else:
      sTypeId = oException.sTypeId;
    # Find out which frame should be the "main" frame and get stack id.
    # * Stack exhaustion can be caused by recursive function calls, where one or more functions repeatedly call
    #   themselves. If possible, this is detected, and the alphabetically first functions is chosen as the main function
    #   The stack hash is created using only the looping functions.
    #   ^^^^ THIS IS NOT YET IMPLEMENTED ^^^
    # * Plenty of exceptions get thrown by special functions, eg. kernel32!DebugBreak, which are not relevant to the
    #   exception. These are ignored and the calling function is used as the "main" frame).
    
    oMainFrame = None;
    uIgnoredFramesHashed = 0;
    uFramesHashed = 0;
    asHTMLStack = [];
    sStackId = "";
    oIgnoredFramesHasher = hashlib.md5();
    oSkippedFramesHasher = hashlib.md5();
    for oFrame in oException.oStack.aoFrames:
      if (uFramesHashed - uIgnoredFramesHashed == dxCrashInfoConfig.get("uStackHashFramesCount", 3)):
        asHTMLStack.append("%s<br/>" % fsHTMLEncode(oFrame.sAddress));
        continue;
      if oMainFrame is None:
        if fbIsIrrelevantTopFrame(sTypeId, oException.uCode, oFrame):
          uIgnoredFramesHashed += 1;
          uFramesHashed += 1;
          asHTMLStack.append("<s>%s</s> (not in hash)<br/>" % fsHTMLEncode(oFrame.sAddress));
          oIgnoredFramesHasher.update(oFrame.sHashAddress);
          continue; # This frame is irrelevant in the context of this exception type.
        if uIgnoredFramesHashed > 0:
          sStackId += "%02X~" % ord(oIgnoredFramesHasher.digest()[0]);
        oMainFrame = oFrame;
      if oFrame.oFunction:
        oHasher = hashlib.md5();
        oHasher.update(oFrame.sHashAddress);
        sStackId += "%02X" % ord(oHasher.digest()[0]);
        asHTMLStack.append("<b><u>%s</u></b> (in hash)<br/>" % fsHTMLEncode(oFrame.sAddress));
      elif oFrame.oModule:
        oHasher = hashlib.md5();
        oHasher.update(oFrame.sHashAddress);
        sStackId += "(%02X)" % ord(oHasher.digest()[0]);
        asHTMLStack.append("<b><u><i>%s</i></u></b> (in hash)<br/>" % fsHTMLEncode(oFrame.sAddress));
      else:
        sStackId += "--";
        asHTMLStack.append("<s>%s</s> (not in hash)<br/>" % fsHTMLEncode(oFrame.sAddress));
      uFramesHashed += 1;
    if uFramesHashed == 0:
      sStackId = "#";
    if oException.oStack.bPartialStack:
      asHTMLStack.append("... (rest of the stack was ignored)<br/>");
    # Get the main stack frame's simplified address as the id.
    sFunctionId = oMainFrame and oMainFrame.sSimplifiedAddress or "(no stack)";
    # Combine the various ids into a unique exception id
    sId = " ".join([sApplicationId, sTypeId, sStackId, sFunctionId]);
    
    # Get the description 
    oLocationFrame = oMainFrame or oTopFrame;
    sLocationDescription = oLocationFrame and oLocationFrame.sAddress or "(no stack)";
    sDescription = "%s in %s" % (oException.sDescription, sLocationDescription);
    
    sSecurityImpact = oException.sSecurityImpact;
    
    # Create HTML details
    sHTMLDetails = """
<!doctype html>
<html>
  <head>
    <style>
      div {
        color: white;
        background: black;
        padding: 5px;
        margin-bottom: 1em;
      }
      code {
        margin-bottom: 1em;
      }
      s {
        color: silver;
        text-decoration: line-through;
      }
    </style>
    <title>%s</title>
  </head>
  <body>
    <div>%s</div>
    <code>%s</code>
    <div>Debugger input/output</div>
    <code>%s</code>
  </body>
</html>""".strip() % (
      fsHTMLEncode(sId),
      fsHTMLEncode(sDescription),
      "".join(asHTMLStack),
      "".join(["%s<br/>" % fsHTMLEncode(x) for x in asCdbIO])
    );
    return cSelf(sId, sDescription, sSecurityImpact, sHTMLDetails);
