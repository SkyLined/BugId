from mConsole import oConsole;

from mColors import *;

asBugIdLogo = [s.rstrip() for s in """
                          __                     _____________                  
                    _,siSP**YSis,_        ,-~-._/             |                 
                  ,SP*'`    . `'*YS,     |     |`-O    BugId  |                 
                 dS'  _    |    _ 'Sb   ,'      \_____________|   ,,,           
    ,,,         dP     \,-` `-<` `  Y; _&/                       :O()           
   :O()        ,S`  \+' \      \    `Sis|ssssssssssssssssss,      ```    ,,,    
    ```  ,,,   (S   (   | --====)    SSS|SSSSSSSSSSSSSSSSSSD             ()O:   
        :O()   'S,  /+, /      /    ,S?*/******************'             ```    
         ```    Yb    _/'-_ _-<._.  dP `                                        
  ______________ YS,       |      ,SP ________________________________________  
                  `Sbs,_    ' _,sdS`                                            
                    `'*YSissiSY*'`                   https://bugid.skylined.nl  
                          ``                                                    """.split("""
""")];

# We can now add color to console output, so let's create a second version of
# the above logo, but with color information (" " = default terminal color, hex
# digit = color number.
asBugIdLogoColors = [s.rstrip() for s in """
                          77                     AAAAAAAAAAAAA                  
                    77777777777777        AAAAAAA             A                 
                  777888    8 888877     A     AAAA    AAAAA  A                 
                 788  8    8    8 887   AA      AAAAAAAAAAAAAAA   888           
    888         78     8CCC CCC8 8  87 AAA                       7CCC           
   7CCC        788  87C 4      C    8877A7777777777777777777      888    888    
    888  888   78   C   4 444444C    888A8888888888888888888             CCC7   
        7CCC   888  87C 4      C    8888A8888888888888888888             888    
         888    88    88CCC CCC888  88 A                                        
  87777777777778 887       8      788 8777777777777777777777777777777777777778  
                  887777    8 777788                                            
                    88877777777888                   _AAAAAAAAAAAAAAAAAAAAAAAAA_  
                          88                                                    """.split("""
""")];

def fPrintLogo():
  # We will use the above ASCII and color data to create a list of arguments
  # that can be passed to oConsole.fOutput in order to output the logo in color:
  oConsole.fLock();
  try:
    for uLineIndex in range(len(asBugIdLogo)):
      uCurrentColor = NORMAL;
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
        uColor = (sColor != " " and (0x0F00 + int(sColor, 16)) or NORMAL) + (bUnderlined and UNDERLINE or 0);
        if uColor != uCurrentColor:
          asBugIdLogoPrintArguments.extend([uColor, ""]);
          uCurrentColor = uColor;
        sChar = sCharsLine[uColumnIndex];
        asBugIdLogoPrintArguments[-1] += sChar;
      oConsole.fOutput(*asBugIdLogoPrintArguments);
  finally:
    oConsole.fUnlock();
