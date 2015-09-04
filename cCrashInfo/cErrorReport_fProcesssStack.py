import hashlib;
from dxCrashInfoConfig import dxCrashInfoConfig;
from NTSTATUS import *;
from mHTML import *;

def cErrorReport_fProcesssStack(oErrorReport, oCrashInfo, oStack, oException):
  # Find out which frame should be the "main" frame and get stack id.
  oTopmostRelevantFrame = None;          # topmost relevant frame
  oTopmostRelevantFunctionFrame = None;  # topmost relevant frame that has a function symbol
  oTopmostRelevantModuleFrame = None;    # topmost relevant frame that has no function symbol but a module
  uFramesHashed = 0;
  asHTMLStack = [];
  sStackId = "";
  for oFrame in oStack.aoFrames:
    if oFrame.bIsHidden:
      # This frame is hidden (because it is irrelevant to the crash)
      asHTMLStack.append("<s>%s</s><br/>" % fsHTMLEncode(oFrame.sAddress));
    else:
      oTopmostRelevantFrame = oTopmostRelevantFrame or oFrame;
      sHTMLAddress = fsHTMLEncode(oFrame.sAddress);
      # Make stack frames without a function symbol italic
      if not oFrame.oFunction:
        sHTMLAddress = "<i>%s</i>" % sHTMLAddress;
      # Hash frame address for id and output frame to html
      if uFramesHashed == oStack.uHashFramesCount:
        # no more hashing is needed: just output as is:
        asHTMLStack.append("%s<br/>" % sHTMLAddress);
      elif oFrame.sIdAddress:
        # frame is part of id: add hash and output bold
        oHasher = hashlib.md5();
        oHasher.update(oFrame.sIdAddress);
        sFrameId = "%02X" % ord(oHasher.digest()[0]);
        sStackId += sFrameId;
        uFramesHashed += 1;
        asHTMLStack.append("<b>%s</b> (%s in id)<br/>" % (sHTMLAddress, sFrameId));
        # Determine the top frame for the id:
        if oFrame.oFunction:
          oTopmostRelevantFunctionFrame = oTopmostRelevantFunctionFrame or oFrame;
        elif oFrame.oModule:
          oTopmostRelevantModuleFrame = oTopmostRelevantModuleFrame or oFrame;
      else:
        # This is not part of the id, but between frames that are: add "__" to id and output strike-through
        sStackId += "__";
        asHTMLStack.append("<s>%s</s><br/>" % sHTMLAddress);
  oErrorReport.sStackId = uFramesHashed == 0 and "##" or sStackId;
  if oStack.bPartialStack:
    asHTMLStack.append("... (rest of the stack was ignored)<br/>");
  # Use a function for the id
  oIdFrame = oTopmostRelevantFunctionFrame or oTopmostRelevantModuleFrame;
  oErrorReport.sFunctionId = oIdFrame and oIdFrame.sSimplifiedAddress or "(unknown)";
  
  # Create the location description 
  oErrorReport.sLocationDescription = oTopmostRelevantFrame and oTopmostRelevantFrame.sAddress or "(unknown)";
  
  # Create HTML details
  oErrorReport.sHTMLDetails = sHTMLDetailsTemplate % {
    "sId": fsHTMLEncode(oErrorReport.sId),
    "sExceptionDescription": fsHTMLEncode(oErrorReport.sExceptionDescription),
    "sProcessBinaryName": fsHTMLEncode(oException.oProcess.sBinaryName),
    "sLocationDescription": fsHTMLEncode(oErrorReport.sLocationDescription),
    "sSecurityImpact": oErrorReport.sSecurityImpact and "<b>%s</b>" % fsHTMLEncode(oErrorReport.sSecurityImpact) or "None",
    "sStack": "".join(asHTMLStack),
    "sAdditionalInformation": "".join(
      [
        sHTMLAdditionalInformationTemplate % {
          "sName": fsHTMLEncode(sName),
          "sDetails": "".join(["%s<br/>" % fsHTMLEncode(x) for x in asDetails]),
        }
        for (sName, asDetails) in oErrorReport.atsAdditionalInformation
      ]
    ),
    "sCdbIO": "".join(["%s<br/>" % fsHTMLEncode(x) for x in oCrashInfo.asCdbIO]),
  };
