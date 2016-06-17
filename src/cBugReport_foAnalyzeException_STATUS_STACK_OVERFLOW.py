from dxBugIdConfig import dxBugIdConfig;

def cBugReport_foAnalyzeException_STATUS_STACK_OVERFLOW(oBugReport, oCdbWrapper, oException):
  oStack = oBugReport.oStack;
  # Stack exhaustion can be caused by recursive function calls, where one or more functions repeatedly call themselves
  # Figure out if this is the case and fide all frames at the top of the stack until the "first" frame in the loop.
  oBugReport.sBugTypeId = "StackExhaustion";
  oBugReport.sBugDescription = "The process exhausted available stack memory";
  oBugReport.sSecurityImpact = None;
  bLoopFound = False;
  for uFirstLoopStartIndex in xrange(len(oStack.aoFrames) - 1):
#    print "*" * 80;
#    print "Start index: %d" % uFirstLoopStartIndex;
    # Find out how large at most a loop can be and still be repeated often enough for detection in the remaining stack:
    uRemainingStackSize = len(oStack.aoFrames) - uFirstLoopStartIndex;
    uMaxLoopSize = long(uRemainingStackSize / dxBugIdConfig["uMinStackRecursionLoops"]);
    for uLoopSize in xrange(1, min(uMaxLoopSize, dxBugIdConfig["uMaxStackRecursionLoopSize"])):
#      print "  Loop size: %d" % uLoopSize;
      for uLoopNumber in xrange(1, dxBugIdConfig["uMinStackRecursionLoops"]):
#        print "    Loop number: %d" % uLoopNumber;
        uLoopStartIndex = uFirstLoopStartIndex + uLoopNumber * uLoopSize;
#        print "    Loop start index: %d" % uLoopStartIndex;
        bLoopNotFound = False;
        for uFrameIndexInLoop in xrange(uLoopSize):
#          print "      Frame number: %d" % uFrameIndexInLoop;
          oFirstLoopFrameAtIndex = oStack.aoFrames[uFirstLoopStartIndex + uFrameIndexInLoop];
          oNthLoopFrameAtIndex = oStack.aoFrames[uLoopStartIndex + uFrameIndexInLoop];
#          print "        %s %s %s " % (oFirstLoopFrameAtIndex.sAddress, \
#              oFirstLoopFrameAtIndex.sAddress == oNthLoopFrameAtIndex.sAddress and "==" or "!=", oNthLoopFrameAtIndex.sAddress);
          if oFirstLoopFrameAtIndex.sAddress != oNthLoopFrameAtIndex.sAddress:
#            print "      LOOP FRAME MISMATCH";
            bLoopNotFound = True;
            break;
        if bLoopNotFound:
#          print "      LOOP REPEAT MISMATCH";
          break;
      else:
        bLoopFound = True;
        # A loop was found in the stack
        # Obviously a loop has no end and the stack will not be complete so the start of the loop may be unknown. This
        # means there is no obvious way to decide which of the functions involved in the loop is the first or last.
        # In order to create a stack id and to compare two loops, a way to pick a frame as the "first" in the loop
        # is needed that will yield the same results every time. This is currently done by creating a strings
        # concatinating the simplified addresses of all frames in order for each possible "first" frame.
        duStartOffset_by_sSimplifiedAddresses = {};
        for uStartOffset in xrange(uLoopSize):
          sSimplifiedAddresses = "".join([
            oStack.aoFrames[uFirstLoopStartIndex + uStartOffset + uIndex].sSimplifiedAddress
            for uIndex in xrange(0, uLoopSize)
          ]);
          duStartOffset_by_sSimplifiedAddresses[sSimplifiedAddresses] = uStartOffset;
        # These strings are now sorted alphabetically and the first one is picked.
        sFirstSimplifiedAddresses = sorted(duStartOffset_by_sSimplifiedAddresses.keys())[0];
        # The associated start offset is added to the start index of the first loop.
        uStartOffset = duStartOffset_by_sSimplifiedAddresses[sFirstSimplifiedAddresses];
        uFirstLoopStartIndex += uStartOffset;
        # All top frames up until the "first" frame in the first loop are hidden:
        for oHiddenFrame in oStack.aoFrames[:uFirstLoopStartIndex]:
          oHiddenFrame.bIsHidden = True;
        # All frames in the loop are part of the hash:
        oStack.uHashFramesCount = uLoopSize;
        # The bug id and description are adjusted to explain the recursive function call as its cause.
        oBugReport.sBugTypeId = "RecursiveCall";
        if uLoopSize == 1:
          oBugReport.sBugDescription = "A recursive function call exhausted available stack memory";
        else:
          oBugReport.sBugDescription = "A recursive function call involving %d functions exhausted available stack memory" % uLoopSize;
        break;
    if bLoopFound:
      break;
    uFirstLoopStartIndex += 1;
  return oBugReport;
