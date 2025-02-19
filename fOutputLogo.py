from foConsoleLoader import foConsoleLoader;
from mColorsAndChars import *;
oConsole = foConsoleLoader();

asBugIdLogo = [s.rstrip() for s in """
  ____________________________________________________________________________  
                              __             ╷                   ╷              
   ││▌║█▐▐║▌▌█│║║│      _,siSP**YSis,_      ─╒╦╦══╦╗            ─╒╦╦╕    ╔╦╕    
   ││▌║█▐▐║▌▌█│║║│    ,SP*'`    . `'*YS,      ║╠══╬╣ ╔╗ ╔╗ ╔╦═╦╗  ║║  ╔╦═╬╣     
   ╵2808197631337╵   dS'  _    |    _ 'Sb    ╘╩╩══╩╝ ╚╩═╩╝ ╚╩═╬╣ ╘╩╩╛ ╚╩═╩╝     
                    dP     \\,-` `-<` `  Y;                 ╚╩═╩╝    ╮╷╭         
      ╮╷╭          ,S`  \\+' \\      \\    `Sissssssssssssssssssss,   :O()         
     :O()          (S   (   | --====)   :SSSSSSSSSSSSSSSSSSSSSSD    ╯╵╰         
      ╯╵╰  ╮╷╭     'S,  /+, /      /    ,S?********************'                 
           ()O:     Yb    _/'-_ _-<._.  dP                                      
           ╯╵╰       YS,       |      ,SP         https://bugid.skylined.nl     
  ____________________`Sbs,_    ' _,sdS`______________________________________  
                        `'*YSissiSY*'`                                          
                              ``                                                """.split("""
""")];

# We can now add color to console output, so let's create a second version of
# the above logo, but with color information (" " = default terminal color, hex
# digit = color number.
asBugIdLogoColors = [s.rstrip() for s in """
  EAEAAEAAAEAAAAAAAAAAAAAAAAAAAAA2AAA2AA2AA2A2A2A2A2A22A22A222A222228222822828  
                              FF             7                   7               
   FFFFFFFFFFFFFFF      FFFFF77777FFFF      7EAAAAA2            7EAA2    EA2    
   FFFFFFFFFFFFFFF    FF7788    6 7777FF      A22AA2 EA EA EAAAA  A2  EAAA2     
   F7777777777777F   F78  6    6    6 77F    A232323 A3223 A22A2 A233 A2323     
                    F7     6CCC CCC6 6  7F                 A2323    888         
      666          F78  67C 4      C    777F7F7F7F7F7F7F7F7F7F7F   7999         
     7CCC          F7   C   4 444444C   F77777777777777777777777    888         
      666  222     F78  67C 4      C    F77888888888888888888888                
           3337     F7    66CCC CCC666  78                                      
           222       778       6      F78         _AAAAAAAAAAAAAAAAAAAAAAAAA_   
  EAEAAA2AA2A2A22A282877777F    6 FFF787EAEAAEAAAAA2AAA2AA2A2A2A2A22A222A22828  
                        8887777F778788                                          
                              88                                                """.split("""
""")];

def fOutputLogo():
  # We will use the above ASCII and color data to create a list of arguments
  # that can be passed to oConsole.fOutput in order to output the logo in color:
  oConsole.fLock();
  try:
    for uLineIndex in range(len(asBugIdLogo)):
      uCurrentColor = COLOR_NORMAL;
      bUnderlined = False;
      asBugIdLogoPrintArguments = [""];
      sCharsLine = asBugIdLogo[uLineIndex];
      sColorsLine = asBugIdLogoColors[uLineIndex];
      uColorIndex = 0;
      for uColumnIndex in range(len(sCharsLine)):
        sColor = sColorsLine[uColorIndex];
        uColorIndex += 1;
        if sColor == "_":
          bUnderlined = not bUnderlined;
          sColor = sColorsLine[uColorIndex];
          uColorIndex += 1;
        uColor = (sColor != " " and (0x0F00 + int(sColor, 16)) or COLOR_NORMAL) + (bUnderlined and CONSOLE_UNDERLINE or 0);
        if uColor != uCurrentColor:
          asBugIdLogoPrintArguments.extend([uColor, ""]);
          uCurrentColor = uColor;
        sChar = sCharsLine[uColumnIndex];
        asBugIdLogoPrintArguments[-1] += sChar;
      oConsole.fOutput(*asBugIdLogoPrintArguments);
  finally:
    oConsole.fUnlock();
