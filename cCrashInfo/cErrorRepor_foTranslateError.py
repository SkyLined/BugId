def cErrorRepor_foTranslateError(oErrorReport, dtxTranslations):
  for (sErrorTypeId, txTranslation) in dtxTranslations.items():
    (sErrorDescription, sSecurityImpact, aasStackTopFrameAddresses) = txTranslation;
    # See if we have a matching stack top:
    for asStackTopFrameAddresses in aasStackTopFrameAddresses:
      uFrameIndex = 0;
      for sStackTopFrameAddress in asStackTopFrameAddresses:
        oTopFrame = oErrorReport.oStack.aoFrames[uFrameIndex];
        uFrameIndex += 1;
        if oTopFrame.sSimplifiedAddress != sStackTopFrameAddress:
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
