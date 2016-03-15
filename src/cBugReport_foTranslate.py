def cBugReport_foTranslate(oBugReport, dtxTranslations):
  if len(oBugReport.oStack.aoFrames) == 0:
    return oBugReport;
  for (sBugTypeId, txTranslation) in dtxTranslations.items():
    (sBugDescription, sSecurityImpact, aasStackTopFrameAddresses) = txTranslation;
    # See if we have a matching stack top:
    for asStackTopFrameAddresses in aasStackTopFrameAddresses:
      uFrameIndex = 0;
      for sStackTopFrameAddress in asStackTopFrameAddresses:
        if uFrameIndex >= len(oBugReport.oStack.aoFrames):
          break; # There are not enough stack frames to match this translation
        oTopFrame = oBugReport.oStack.aoFrames[uFrameIndex];
        uFrameIndex += 1;
        # "*!" means match only the function and not the module.
        if sStackTopFrameAddress[:2] == "*!":
          tsSimplifiedAddress = oTopFrame.sSimplifiedAddress.split("!", 1);
          # Compare the function names:
          if len(tsSimplifiedAddress) != 2 or tsSimplifiedAddress[1].lower() != sStackTopFrameAddress[2:].lower():
            # These frames don't match: stop checking frames
            break;
        elif oTopFrame.sSimplifiedAddress.lower() != sStackTopFrameAddress.lower():
          # These frames don't match: stop checking frames
          break;
      else:
        # All frames matched: translate bug:
        if sBugTypeId is None:
          # This is not a bug and should be ignored; the application can continue to run:
          return None;
        else:
          oBugReport.sBugTypeId = sBugTypeId;
          oBugReport.sBugDescription = sBugDescription;
          oBugReport.sSecurityImpact = sSecurityImpact;
          # And hide all the matched frames as they are irrelevant
          for oFrame in oBugReport.oStack.aoFrames[:uFrameIndex]:
            oFrame.bIsHidden = True;
          return oBugReport;
  return oBugReport;
