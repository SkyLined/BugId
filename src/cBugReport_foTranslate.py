def cErrorReport_foTranslateError(oErrorReport, dtxTranslations):
  if len(oErrorReport.oStack.aoFrames) == 0:
    return oErrorReport;
  for (sErrorTypeId, txTranslation) in dtxTranslations.items():
    (sErrorDescription, sSecurityImpact, aasStackTopFrameAddresses) = txTranslation;
    # See if we have a matching stack top:
    for asStackTopFrameAddresses in aasStackTopFrameAddresses:
      uFrameIndex = 0;
      for sStackTopFrameAddress in asStackTopFrameAddresses:
        if uFrameIndex >= len(oErrorReport.oStack.aoFrames):
          break; # There are not enough stack frames to match this translation
        oTopFrame = oErrorReport.oStack.aoFrames[uFrameIndex];
        uFrameIndex += 1;
        # "*!" means match only the function and not the module.
        if sStackTopFrameAddress[:2] == "*!":
          tsSimplifiedAddress = oTopFrame.sSimplifiedAddress.split("!", 1);
          # Compare the function names:
          if len(tsSimplifiedAddress) != 2 or tsSimplifiedAddress[1] != sStackTopFrameAddress[2:]:
            # These frames don't match: stop checking frames
            break;
        elif oTopFrame.sSimplifiedAddress != sStackTopFrameAddress:
          # These frames don't match: stop checking frames
          break;
      else:
        # All frames matched: translate error:
        if sErrorTypeId is None:
          # This is not an error and should be ignored; the application can continue to run:
          return None;
        else:
          oErrorReport.sErrorTypeId = sErrorTypeId;
          oErrorReport.sErrorDescription = sErrorDescription;
          oErrorReport.sSecurityImpact = sSecurityImpact;
          # And hide all the matched frames as they are irrelevant
          for oFrame in oErrorReport.oStack.aoFrames[:uFrameIndex]:
            oFrame.bIsHidden = True;
          return oErrorReport;
  return oErrorReport;
