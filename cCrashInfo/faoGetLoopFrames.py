import math;

def faoGetLoopFrames(oStack):
  for uFirstLoopStartIndex in xrange(len(oStack.aoFrames) - 1):
#    print "*" * 80;
#    print "Start index: %d" % uFirstLoopStartIndex;
    uRemainingStackSize = len(oStack.aoFrames) - uFirstLoopStartIndex;
    for uLoopSize in xrange(1, int(uRemainingStackSize / 2)):
#      print "  Loop size: %d" % uLoopSize;
      # Ten loops suffice in case the number of frames is really large
      for uLoopNumber in xrange(1, min(10, int(uRemainingStackSize / uLoopSize))):
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
        aoLoopFrames = oStack.aoFrames[uFirstLoopStartIndex : uFirstLoopStartIndex + uLoopSize];
        return aoLoopFrames;
    uFirstLoopStartIndex += 1;
  return None;

